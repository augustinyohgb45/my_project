from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),  # Route pour accéder à l'interface d'administration
    path('auth_app/', include('auth_app.urls') ),  # Route pour la page de connexion
    path('dashboard/', include('dashboard.urls')),  # Route pour la page d'accueil
]
