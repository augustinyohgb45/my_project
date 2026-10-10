from django import forms
from django.utils import timezone

from .models import Incident, Changement, Service, Type_requette_changemen, MESSAGE_CHANGEMENT_PAR_DEFAUT

# Format attendu par les champs HTML <input type="datetime-local">
FORMAT_DATETIME_LOCAL = '%Y-%m-%dT%H:%M'


def _maintenant_local():
    return timezone.localtime().replace(second=0, microsecond=0)


class StyleBootstrapMixin:
    """Ajoute la classe Bootstrap adaptée à chaque champ et marque les champs en erreur."""

    def appliquer_style(self):
        for champ in self.fields.values():
            champ.widget.attrs['class'] = 'custom-select' if isinstance(champ.widget, forms.Select) else 'form-control'

    def full_clean(self):
        super().full_clean()
        for nom in self.errors:
            if nom in self.fields:
                self.fields[nom].widget.attrs['class'] += ' is-invalid'


class IncidentForm(StyleBootstrapMixin, forms.ModelForm):
    destinataire_nouveau = forms.EmailField(
        required=False,
        max_length=500,
        label="Destinataire supplémentaire",
        help_text="Facultatif. Reçoit la notification en plus des destinataires du type d'incident.",
        widget=forms.EmailInput(attrs={'placeholder': 'prenom.nom@exemple.com'}),
    )

    class Meta:
        model = Incident
        fields = ['numero_ticket', 'type_requette', 'services_impacte', 'description', 'destinataire_nouveau', 'date_envoie', 'statut']
        labels = {
            'numero_ticket': "Numéro de ticket",
            'type_requette': "Type d'incident",
            'services_impacte': "Service impacté",
            'description': "Description",
            'date_envoie': "Date de la notification",
            'statut': "Statut",
        }
        help_texts = {
            'type_requette': "Les incidents « indisponibilite » et « instabilite » déclenchent un e-mail.",
        }
        widgets = {
            'numero_ticket': forms.TextInput(attrs={'placeholder': 'Ex. INC0012345'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': "Décrivez l'incident constaté…"}),
            'date_envoie': forms.DateTimeInput(format=FORMAT_DATETIME_LOCAL, attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_envoie'].initial = _maintenant_local
        self.fields['type_requette'].empty_label = "Choisissez un type…"
        self.fields['services_impacte'].empty_label = "Choisissez un service…"
        self.appliquer_style()


class ChangementForm(StyleBootstrapMixin, forms.ModelForm):
    """
    Formulaire de changement. Le service et le type peuvent être choisis dans la liste
    ou saisis dans nouveau_service / nouveau_type ; ils sont alors créés à l'enregistrement.
    """
    nouveau_service = forms.CharField(
        required=False,
        label="Nouveau service",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nom du nouveau service'}),
    )
    nouveau_type = forms.CharField(
        required=False,
        label="Nouveau type de changement",
        max_length=200,
        help_text="Un message par défaut lui sera associé ; vous pourrez le modifier dans l'admin.",
        widget=forms.TextInput(attrs={'placeholder': 'Nom du nouveau type'}),
    )
    destinataire_nouveau = forms.EmailField(
        required=False,
        max_length=500,
        label="Destinataire supplémentaire",
        help_text="Obligatoire si le type de changement n'a encore aucun destinataire.",
        widget=forms.EmailInput(attrs={'placeholder': 'prenom.nom@exemple.com'}),
    )

    class Meta:
        model = Changement
        fields = [
            'Numero_ticket', 'services_impacte', 'Type_requette_changement', 'nom_plateforme',
            'date_changement', 'fin_changement', 'heure_debut', 'heure_fin', 'date_envoie',
            'description', 'destinataire_nouveau', 'statut',
        ]
        labels = {
            'Numero_ticket': "Numéro de ticket",
            'services_impacte': "Service impacté",
            'Type_requette_changement': "Type de changement",
            'nom_plateforme': "Plateforme",
            'date_changement': "Début du changement",
            'fin_changement': "Fin du changement",
            'heure_debut': "Heure de début",
            'heure_fin': "Heure de fin",
            'date_envoie': "Date d'envoi de la notification",
            'description': "Description",
            'statut': "Statut",
        }
        help_texts = {
            'date_envoie': "Dans le futur, l'e-mail partira automatiquement à cette date.",
            'heure_debut': "Heure annoncée dans le message.",
            'heure_fin': "Heure annoncée dans le message.",
        }
        widgets = {
            'Numero_ticket': forms.TextInput(attrs={'placeholder': 'Ex. CHG0012345'}),
            'nom_plateforme': forms.TextInput(attrs={'placeholder': 'Ex. MoMo, USSD, API…'}),
            'date_changement': forms.DateTimeInput(format=FORMAT_DATETIME_LOCAL, attrs={'type': 'datetime-local'}),
            'fin_changement': forms.DateTimeInput(format=FORMAT_DATETIME_LOCAL, attrs={'type': 'datetime-local'}),
            'date_envoie': forms.DateTimeInput(format=FORMAT_DATETIME_LOCAL, attrs={'type': 'datetime-local'}),
            'heure_debut': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Objectif et impact du changement…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Une valeur vide dans la liste signifie « ajouter un nouveau service / type »
        self.fields['services_impacte'].required = False
        self.fields['Type_requette_changement'].required = False
        self.fields['date_envoie'].initial = _maintenant_local
        # Ne pas pré-remplir avec la valeur par défaut du modèle (« Plateforme inconnue »)
        if not self.instance.pk:
            self.initial['nom_plateforme'] = ''
        self.appliquer_style()

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('services_impacte')
        nouveau_service = (cleaned_data.get('nouveau_service') or '').strip()
        type_requette = cleaned_data.get('Type_requette_changement')
        nouveau_type = (cleaned_data.get('nouveau_type') or '').strip()
        destinataire_nouveau = (cleaned_data.get('destinataire_nouveau') or '').strip()

        if not service and not nouveau_service:
            self.add_error('nouveau_service', "Choisissez un service dans la liste ou saisissez un nouveau service.")
        if not type_requette and not nouveau_type:
            self.add_error('nouveau_type', "Choisissez un type dans la liste ou saisissez un nouveau type.")

        debut, fin = cleaned_data.get('date_changement'), cleaned_data.get('fin_changement')
        if debut and fin and fin < debut:
            self.add_error('fin_changement', "La fin du changement doit être après son début.")

        # Un nouveau type n'a encore aucun destinataire : il en faut au moins un pour la notification
        if not destinataire_nouveau and 'destinataire_nouveau' not in self.errors:
            if not type_requette and nouveau_type:
                type_existant = Type_requette_changemen.objects.filter(nom_requette_changement=nouveau_type).first()
                sans_destinataire = type_existant is None or not type_existant.destinataires.exists()
            else:
                sans_destinataire = type_requette is not None and not type_requette.destinataires.exists()
            if sans_destinataire:
                self.add_error('destinataire_nouveau', "Ce type de changement n'a aucun destinataire : saisissez un e-mail de destinataire.")

        cleaned_data['nouveau_service'] = nouveau_service
        cleaned_data['nouveau_type'] = nouveau_type
        return cleaned_data

    def save(self, commit=True):
        changement = super().save(commit=False)
        if not self.cleaned_data.get('services_impacte'):
            changement.services_impacte, _ = Service.objects.get_or_create(nom=self.cleaned_data['nouveau_service'])
        if not self.cleaned_data.get('Type_requette_changement'):
            changement.Type_requette_changement, _ = Type_requette_changemen.objects.get_or_create(
                nom_requette_changement=self.cleaned_data['nouveau_type'],
                defaults={'message': MESSAGE_CHANGEMENT_PAR_DEFAUT},
            )
        if commit:
            changement.save()
        return changement
