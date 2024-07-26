from django.contrib import admin
from django.urls import path
from auth_app import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Route pour accéder à l'interface d'administration
    path('', views.inscription, name='inscription'),  # Route pour la page d'inscription
    path('connexion/', views.connexion, name='connexion'),  # Route pour la page de connexion
    path('acceuil/', views.acceuil, name='acceuil'),  # Route pour la page d'accueil
    path('deconnexion/', views.deconnexion, name='deconnexion'),  # Route
]
