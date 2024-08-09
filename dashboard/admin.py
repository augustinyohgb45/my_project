from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Incident)
class Adminincident(admin.ModelAdmin):
    list_display = ["services_impacte","date_enregistrement","description","statut"]

@admin.register(Destinataire)    
class Admindestinataires(admin.ModelAdmin):
    list_display =  ["nom","email","contact"]
    
@admin.register(Changement)    
class Admindestinataires(admin.ModelAdmin):
    list_display =  [
            'services_impacte', 'date_changement', 'fin_changement', 
            'date_envoie', 'description', 'destinataires', 'statut'
        ]
    
    