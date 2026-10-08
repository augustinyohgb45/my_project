from django import forms
from .models import Incident, Changement, Service, Type_requette_changemen, MESSAGE_CHANGEMENT_PAR_DEFAUT

# Format attendu par les champs HTML <input type="datetime-local">
FORMAT_DATETIME_LOCAL = '%Y-%m-%dT%H:%M'


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['services_impacte', 'description', 'destinataire_nouveau', 'date_envoie', 'statut', 'type_requette', 'numero_ticket']
        widgets = {
            'services_impacte': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'date_envoie': forms.DateTimeInput(format=FORMAT_DATETIME_LOCAL, attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'type_requette': forms.Select(attrs={'class': 'form-control'}),
            'numero_ticket': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ChangementForm(forms.ModelForm):
    """
    Formulaire de changement. Le service et le type peuvent être choisis dans la liste
    ou saisis dans nouveau_service / nouveau_type ; ils sont alors créés à l'enregistrement.
    """
    nouveau_service = forms.CharField(
        required=False,
        label="Nouveau service",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le nouveau service'}),
    )
    nouveau_type = forms.CharField(
        required=False,
        label="Nouveau type de changement",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le nouveau type'}),
    )

    class Meta:
        model = Changement
        fields = [
            'services_impacte', 'date_changement', 'fin_changement',
            'date_envoie', 'description', 'nom_plateforme', 'destinataire_nouveau',
            'statut', 'Type_requette_changement', 'Numero_ticket', 'heure_debut', 'heure_fin'
        ]
        widgets = {
            'services_impacte': forms.Select(attrs={'class': 'form-control'}),
            'date_changement': forms.DateTimeInput(format=FORMAT_DATETIME_LOCAL, attrs={'type': 'datetime-local'}),
            'fin_changement': forms.DateTimeInput(format=FORMAT_DATETIME_LOCAL, attrs={'type': 'datetime-local'}),
            'date_envoie': forms.DateTimeInput(format=FORMAT_DATETIME_LOCAL, attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'heure_debut': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'Type_requette_changement': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Une valeur vide dans la liste signifie « ajouter un nouveau service / type »
        self.fields['services_impacte'].required = False
        self.fields['Type_requette_changement'].required = False

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

        # Un nouveau type n'a encore aucun destinataire : il en faut au moins un pour la notification
        if not destinataire_nouveau:
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
