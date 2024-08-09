from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Destinataire(models.Model):
    nom = models.CharField(max_length = 40)
    contact = models.CharField(max_length = 10)
    email = models.EmailField()
    
    def __str__(self):
        return self.nom

class Changement(models.Model):
    TYPE_STATUT = (("E","en cours"),("C","cloture"))
    services_impacte = models.CharField(max_length = 500)
    date_enregistrement = models.DateTimeField(auto_now_add = True)
    date_changement = models.DateTimeField()
    fin_changement = models.DateTimeField()
    date_envoie = models.DateTimeField()
    description = models.TextField()
    destinataires = models.ForeignKey(Destinataire, on_delete = models.PROTECT )
    user = models.ForeignKey(User, on_delete = models.DO_NOTHING )
    statut = models.CharField(choices = TYPE_STATUT, default = "en cours", max_length = 12)
    

class Incident(models.Model):
    TYPE_STATUT = (("E","en cours"),("C","cloture"))
    services_impacte = models.CharField(max_length = 500)
    date_enregistrement = models.DateTimeField(auto_now_add = True)
    description = models.TextField()
    destinataires = models.ManyToManyField(Destinataire)
    user = models.ForeignKey(User, on_delete = models.DO_NOTHING )
    statut = models.CharField(choices = TYPE_STATUT, default = "en cours", max_length = 12)
    

