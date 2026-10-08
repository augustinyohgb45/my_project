from django.db import models
from django.contrib.auth.models import User

# Message proposé par défaut pour un type de changement créé depuis le formulaire.
# Les balises < ... > sont remplacées à l'envoi (voir utils.construire_email_changement).
MESSAGE_CHANGEMENT_PAR_DEFAUT = (
    "Y’ello MTNers, une opération de maintenance sur < nom du service > est prévue "
    "du < date début > au < date fin >, de < heure début > à < heure fin >. IT-MFS"
)


class Service(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class Destinataire(models.Model):
    nom = models.CharField(max_length=40)
    contact = models.CharField(max_length=10)
    email = models.EmailField()

    def __str__(self):
        return self.nom


class Type_requette_changemen(models.Model):
    nom_requette_changement = models.CharField(max_length=200)
    message = models.TextField(default="test")
    destinataires = models.ManyToManyField(Destinataire, related_name="changements")

    def __str__(self):
        return self.nom_requette_changement


class Type_requette(models.Model):
    nom_requette = models.CharField(max_length=200)
    message = models.TextField(default="test")
    destinataires = models.ManyToManyField(Destinataire, related_name="incidents")

    def __str__(self):
        return self.nom_requette


class Changement(models.Model):
    TYPE_STATUT = (("E", "en cours"), ("C", "cloture"))
    Numero_ticket = models.CharField(max_length=10)
    services_impacte = models.ForeignKey(Service, on_delete=models.PROTECT)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    date_changement = models.DateTimeField()
    fin_changement = models.DateTimeField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    date_envoie = models.DateTimeField()
    description = models.TextField()
    destinataire_nouveau = models.CharField(null=True, blank=True, max_length=500)
    nom_plateforme = models.CharField(max_length=500, default="Plateforme inconnue")
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    statut = models.CharField(choices=TYPE_STATUT, default="E", max_length=12)
    en_cours = models.BooleanField(default=True)
    email_envoye = models.BooleanField(default=False)
    Type_requette_changement = models.ForeignKey(Type_requette_changemen, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        # en_cours reste toujours cohérent avec le statut
        self.en_cours = self.statut == "E"
        super().save(*args, **kwargs)


class Incident(models.Model):
    TYPE_STATUT = (("E", "en cours"), ("C", "clôturé"))
    numero_ticket = models.CharField(max_length=10)
    services_impacte = models.ForeignKey(Service, on_delete=models.PROTECT)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    date_envoie = models.DateTimeField()
    description = models.TextField()
    destinataire_nouveau = models.CharField(null=True, blank=True, max_length=500)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    statut = models.CharField(choices=TYPE_STATUT, default="E", max_length=12)
    en_cours = models.BooleanField(default=True)
    type_requette = models.ForeignKey(Type_requette, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        # en_cours reste toujours cohérent avec le statut
        self.en_cours = self.statut == "E"
        super().save(*args, **kwargs)
