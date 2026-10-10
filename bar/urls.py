from django.urls import path

from . import views

urlpatterns = [
    path('', views.stock, name='bar_stock'),  # état du stock
    path('mouvements/', views.mouvements, name='bar_mouvements'),  # saisie et historique des mouvements
    path('produits/nouveau/', views.produit_nouveau, name='bar_produit_nouveau'),
    path('produits/<int:produit_id>/modifier/', views.produit_modifier, name='bar_produit_modifier'),
    path('importer/', views.importer, name='bar_importer'),  # import du catalogue Excel (administrateurs)
]
