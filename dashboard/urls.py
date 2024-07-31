from django.urls import path 
from dashboard import views

urlpatterns = [
    path('acceuil/', views.acceuil, name='acceuil'),  # Route pour la page d'accueil
    path('incident/', views.incident, name='incident'),
    path('changement/', views.changement, name='changement'),
]
