# forms.py
from django import forms
from .models import Incident, Destinataire, Changement,Service
from .models import  Type_requette_changemen




class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['services_impacte', 'description', 'destinataire_nouveau', 'date_envoie', 'statut', 'type_requette', 'numero_ticket']
        widgets = {
            'services_impacte': forms.Select(attrs={'class': 'form-control'}),  # Correction: Utilisation d'un Select
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'date_envoie': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'type_requette': forms.Select(attrs={'class': 'form-control'}),
            'numero_ticket': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Correction pour services_impacte : queryset pour récupérer les services disponibles
        self.fields['services_impacte'].queryset = Service.objects.all()
        
        # Gestion du champ destinataires (si utilisé)
        if 'destinataires' in self.fields:
            self.fields['destinataires'].queryset = Destinataire.objects.all()


# class IncidentForm(forms.ModelForm):


   # class Meta:
    #     model = Incident
    #     fields = ['services_impacte', 'description','destinataire','destinataire_nouveau','date_envoie', 'statut','Type_requette_id','Numero_ticket','destinataires']
    #     widgets = {
    #         'services_impacte': forms.TextInput(attrs={'class': 'form-control'}),
    #         'description': forms.Textarea(attrs={'class': 'form-control'}),
    #         'date_envoie': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
    #         'statut': forms.Select(attrs={'class': 'form-control'}),

    #     }

    # def _init_(self, *args, **kwargs):
    #     super()._init_(*args, **kwargs)
    #     self.fields['destinataires'].queryset = Destinataire.objects.all()  
        

class ChangementForm(forms.ModelForm):
    nouveau_type = forms.CharField(
        required=False,
        label="Ajouter nouveau",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    nouveau_service = forms.CharField(
        required=False,
        label="Ajouter nouveau service",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
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
            'date_changement': forms.DateTimeInput(attrs={ 'type':  'datetime-local'}),
            'fin_changement': forms.DateTimeInput(attrs={ 'type': 'datetime-local'}),
            'date_envoie': forms.DateTimeInput(attrs={ 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'heure_debut': forms.TimeInput(format='%H:%M', attrs={ 'type': 'time'}),
            'heure_fin': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'Type_requette_changement': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Charger les types de requête existants et ajouter une option pour un nouveau type
        types = [(type.id, type.nom_requette_changement) for type in Type_requette_changemen.objects.all()]
        self.fields['Type_requette_changement'].choices = types + [('', 'Ajouter nouveau')]

    def clean(self):
        cleaned_data = super().clean()
        nouveau_type = cleaned_data.get('nouveau_type')
        nouveau_service = cleaned_data.get('nouveau_service')
        type_id = cleaned_data.get('Type_requette_changement')
        service_id = cleaned_data.get('services_impacte')

        # Validation pour nouveau type
        if not type_id and nouveau_type:
            if not nouveau_type.strip():
                raise forms.ValidationError("Veuillez saisir un nouveau type ou sélectionner un type existant.")
            # Créer le nouveau type de requête si un nouveau type est fourni
            type_requette, created = Type_requette_changemen.objects.get_or_create(nom_requette_changement=nouveau_type)
            cleaned_data['Type_requette_changemen'] = type_requette

        # Validation pour nouveau service
        if service_id == 'add_new_service' and not nouveau_service.strip():
            raise forms.ValidationError("Veuillez saisir un nouveau service si vous avez sélectionné 'Ajouter nouveau service'.")
        
        return cleaned_data 
    
    
# class ChangementForm(forms.ModelForm):
#     class Meta:
#         model = Changement
#         fields = [
#             'services_impacte', 'date_changement', 'fin_changement', 
#             'date_envoie', 'description', 'nom_plateforme', 'destinataire_nouveau', 
#             'statut', 'Type_requette_changement_id', 'Numero_ticket', 'heure_debut', 'heure_fin'
#         ]
#         widgets = {
#             'services_impacte': forms.TextInput(attrs={'class': 'form-control'}),
#             'date_changement': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
#             'fin_changement': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
#             'date_envoie': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
#             'description': forms.Textarea(attrs={'class': 'form-control'}),
#             'heure_debut': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
#             'heure_fin': forms.TimeInput(format='%H:%M', attrs={'class': 'form-control', 'type': 'time'}),
#             'statut': forms.Select(attrs={'class': 'form-control'}),
#             'Type_requette_changement_id': forms.Select(attrs={'class': 'form-control'}) 

#         }

#     def _init_(self, *args, **kwargs):
#             super()._init_(*args, **kwargs)
#             self.fields['destinataire_nouveau'].widget.attrs.update(
#                 {
#                     'required':'false'
#                 }
#             )
#             self.fields['destinataires'].widget.attrs.update(
#                 {
#                     'required':'false'
#                 }
#             )

        