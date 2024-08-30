from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Incident)
class Adminincident(admin.ModelAdmin):
    list_display = ["services_impacte","date_enregistrement","description",'destinataire_nouveau',"statut"]

@admin.register(Destinataire)    
class Admindestinataires(admin.ModelAdmin):
    list_display =  ["nom","email","contact"]
    
@admin.register(Changement)    
class Admindestinataires(admin.ModelAdmin):
    list_display =  [
            'services_impacte', 'date_changement', 'fin_changement', 
            'date_envoie', 'description','destinataire_nouveau', 'statut','heure_debut','heure_fin'
        ]

@admin.register(Type_requette)    
class AdminTypeRequete(admin.ModelAdmin):
    list_display =  [
            'Nom_requette',
        ]
@admin.register(Type_requette_changemen)        
class AdminTypeRequeteChangement(admin.ModelAdmin):
    list_display =  [
            'Nom_requette_changement',
        ]

    