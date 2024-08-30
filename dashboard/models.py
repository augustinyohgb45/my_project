from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Destinataire(models.Model):
    nom = models.CharField(max_length = 40)
    contact = models.CharField(max_length = 10)
    email = models.EmailField()
    
    def __str__(self):
        return self.nom

class Type_requette_changemen(models.Model):
    Nom_requette_changement = models.CharField(max_length=200)
    def __str__(self):
            return self.Nom_requette_changement

class Type_requette(models.Model):
    Nom_requette = models.CharField(max_length=200)
    def __str__(self):
            return self.Nom_requette
        
class Changement(models.Model):
    TYPE_STATUT = (("E","en cours"),("C","cloture"))
    Numero_ticket = models.CharField(max_length = 155)
    services_impacte = models.CharField(max_length = 500)
    date_enregistrement = models.DateTimeField(auto_now_add = True)
    date_changement = models.DateTimeField()
    fin_changement = models.DateTimeField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    date_envoie = models.DateTimeField()
    description = models.TextField()
    destinataire_nouveau = models.EmailField(null=True, blank=True) 
    nom_plateforme = models.CharField(max_length=500, default="Plateforme inconnue")
    user = models.ForeignKey(User, on_delete = models.DO_NOTHING )
    statut = models.CharField(choices = TYPE_STATUT, default = "en cours", max_length = 12)
    en_cours = models.BooleanField(default = True)
    Type_requette_changement_id = models.ForeignKey(Type_requette_changemen, on_delete=models.DO_NOTHING)


class Incident(models.Model):
    TYPE_STATUT = (("E","en cours"),("C","cloture"))
    Numero_ticket = models.CharField(max_length = 150)
    services_impacte = models.CharField(max_length = 500)
    date_enregistrement = models.DateTimeField(auto_now_add = True)
    description = models.TextField()
    destinataire_nouveau = models.EmailField(null=True,blank=True)    
    user = models.ForeignKey(User, on_delete = models.DO_NOTHING )
    statut = models.CharField(choices = TYPE_STATUT, default = "en cours", max_length = 12)
    en_cours = models.BooleanField(default = True)
    Type_requette_id = models.ForeignKey(Type_requette, on_delete=models.DO_NOTHING)


