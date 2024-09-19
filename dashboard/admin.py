from django.contrib import admin
from .models import Incident, Destinataire, Service, Changement, Type_requette, Type_requette_changemen

@admin.register(Service)
class AdminService(admin.ModelAdmin):
    list_display = ['nom']

@admin.register(Incident)
class AdminIncident(admin.ModelAdmin):
    list_display = [
        "services_impacte", "date_enregistrement", "description", 
        'destinataire_nouveau', "statut"
    ]

@admin.register(Destinataire)
class AdminDestinataire(admin.ModelAdmin):
    list_display = ["nom", "email", "contact"]

@admin.register(Changement)
class AdminChangement(admin.ModelAdmin):
    list_display = [
        'services_impacte', 'date_changement', 'fin_changement', 
        'date_envoie', 'description', 'destinataire_nouveau', 'statut',
        'heure_debut', 'heure_fin'
    ]

@admin.register(Type_requette)
class AdminTypeRequete(admin.ModelAdmin):
    list_display = ['nom_requette']

@admin.register(Type_requette_changemen)
class AdminTypeRequeteChangement(admin.ModelAdmin):
    list_display = ['nom_requette_changement']


# @admin.register(Incident)
# class Adminincident(admin.ModelAdmin):
#     list_display = ["services_impacte","date_enregistrement","description",'destinataire_nouveau',"date_envoie","statut"]

# @admin.register(Destinataire)    
# class Admindestinataires(admin.ModelAdmin):
#     list_display =  ["nom","email","contact"]
    
# @admin.register(Changement)    
# class AdminChangement(admin.ModelAdmin):
#     list_display =  [
#             'services_impacte', 'date_changement', 'fin_changement', 
#             'date_envoie', 'description','destinataire','destinataire_nouveau', 'statut','heure_debut','heure_fin'
#         ]

# @admin.register(Type_requette)    
# class AdminTypeRequete(admin.ModelAdmin):
#     list_display =  [
#             'Nom_requette',
#         ]
# @admin.register(Type_requette_changemen)        
# class AdminTypeRequeteChangement(admin.ModelAdmin):
#     list_display =  [
#             'Nom_requette_changement',
#         ]


    