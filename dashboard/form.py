# forms.py
from django import forms
from .models import Incident, Destinataire
from .models import Changement

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['services_impacte', 'description', 'destinataires', 'statut']
        widgets = {
            'services_impacte': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'destinataires': forms.CheckboxSelectMultiple(),  # Utilisez CheckboxSelectMultiple
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['destinataires'].queryset = Destinataire.objects.all()    
            
class ChangementForm(forms.ModelForm):
    class Meta:
        model = Changement
        fields = [
            'services_impacte', 'date_changement', 'fin_changement', 
            'date_envoie', 'description', 'destinataires', 'statut'
        ]
        widgets = {
            'services_impacte': forms.TextInput(attrs={'class': 'form-control'}),
            'date_changement': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fin_changement': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_envoie': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'destinataires': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }