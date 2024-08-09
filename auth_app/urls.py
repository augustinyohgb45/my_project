from django.urls import path
from auth_app import views
urlpatterns = [
    path('accueil/', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'), 
    path('deconnexion/', views.deconnexion, name='deconnexion'),
]
