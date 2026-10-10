from django.urls import path
from auth_app import views

urlpatterns = [
    path('accueil/', views.accueil, name='accueil'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    # Gestion des utilisateurs (administrateurs uniquement)
    path('utilisateurs/', views.utilisateurs, name='utilisateurs'),
    path('inscription/', views.inscription, name='inscription'),
    path('utilisateurs/<int:utilisateur_id>/modifier/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/<int:utilisateur_id>/activer/', views.activer_utilisateur, name='activer_utilisateur'),
]
