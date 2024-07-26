from django.db import models


class Utilisateur(models.Model):
    nom_utilisateur = models.CharField(max_length=50)
    mot_de_passe = models.CharField(max_length=50)
    
