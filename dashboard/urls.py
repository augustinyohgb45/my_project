from django.urls import path 
from . import views 

urlpatterns = [
    path('acceuil/', views.acceuil, name='acceuil'),  # Route pour la page d'accueil
    path('incident/', views.incident, name='incident'), #route formulaire incident
    path('changement/', views.changement, name='changement'), #route formulaire changement
    path('listeincident/', views.listeincident, name='listeincident'),#route liste incident
    path('listechangement/', views.listechangement, name='listechangement'),#route liste changement
    path('action_statut/<int:incident_id>', views.action_statut, name='action_statut'),
    path('action_statut_change/<int:changement_id>', views.action_statut_change, name='action_statut_change'),
]
