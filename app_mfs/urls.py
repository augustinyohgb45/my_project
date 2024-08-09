from django.contrib import admin 
from django.urls import path, include 
from django.shortcuts import redirect
urlpatterns = [
    path('admin/', admin.site.urls,name="admin"),  # Route pour accéder à l'interface d'administration
    path('auth_app/', include('auth_app.urls') ),  # Route pour la page de connexion
    path('dashboard/', include('dashboard.urls')),  # Route pour la page d'accueil
    path('', lambda request: redirect('connexion')),  # Redirection de la racine vers la page de connexion

]
