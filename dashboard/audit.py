"""
Journal d'audit : enregistre automatiquement les connexions et les créations, clôtures,
modifications et suppressions des objets suivis, quel que soit l'écran utilisé
(application, admin Django ou commande planifiée).
"""
import datetime
import logging
import threading

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    Changement, Destinataire, Incident, JournalAudit, Service, Type_requette, Type_requette_changemen,
)

logger = logging.getLogger(__name__)
_contexte = threading.local()

# Modèles suivis et nom affiché dans le journal
MODELES_SUIVIS = {
    Incident: "Incident",
    Changement: "Changement",
    Service: "Service",
    Destinataire: "Destinataire",
    Type_requette: "Type d'incident",
    Type_requette_changemen: "Type de changement",
    User: "Utilisateur",
}

# Champs techniques ignorés dans le détail des modifications
CHAMPS_IGNORES = {'id', 'last_login', 'date_joined', 'date_enregistrement', 'en_cours', 'password'}

# Libellés affichés pour les champs modifiés
LIBELLES = {
    'numero_ticket': "Ticket", 'Numero_ticket': "Ticket",
    'services_impacte': "Service", 'type_requette': "Type", 'Type_requette_changement': "Type",
    'description': "Description", 'destinataire_nouveau': "Destinataire supplémentaire",
    'date_envoie': "Date de notification", 'statut': "Statut", 'email_envoye': "Notification envoyée",
    'date_changement': "Début", 'fin_changement': "Fin", 'heure_debut': "Heure de début",
    'heure_fin': "Heure de fin", 'nom_plateforme': "Plateforme", 'user': "Créé par",
    'nom': "Nom", 'contact': "Contact", 'email': "E-mail", 'message': "Message",
    'nom_requette': "Nom", 'nom_requette_changement': "Nom",
    'username': "Nom d'utilisateur", 'first_name': "Prénom", 'last_name': "Nom",
    'is_active': "Compte actif", 'is_superuser': "Administrateur", 'is_staff': "Accès à l'admin",
}


class AuditMiddleware:
    """Mémorise la requête en cours pour connaître l'auteur et l'adresse IP des actions."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _contexte.request = request
        try:
            return self.get_response(request)
        finally:
            _contexte.request = None


def _requete():
    return getattr(_contexte, 'request', None)


def _adresse_ip(request):
    return request.META.get('REMOTE_ADDR') if request else None


def journaliser(action, objet='', type_objet='', details='', utilisateur=None, request=None):
    """Ajoute une entrée au journal. Sans utilisateur connecté, l'action est attribuée au « Système »."""
    request = request or _requete()
    if utilisateur is None and request is not None and getattr(request, 'user', None) is not None:
        if request.user.is_authenticated:
            utilisateur = request.user
    try:
        JournalAudit.objects.create(
            utilisateur=utilisateur if utilisateur is not None and utilisateur.pk else None,
            nom_utilisateur=utilisateur.get_username() if utilisateur is not None else '',
            action=action,
            type_objet=type_objet,
            objet=str(objet)[:255],
            details=details,
            adresse_ip=_adresse_ip(request),
        )
    except Exception as e:
        # L'audit ne doit jamais empêcher l'action elle-même
        logger.error(f"Impossible d'enregistrer l'audit ({action} {objet}) : {e}")


# ---------- Connexions ----------

@receiver(user_logged_in)
def _connexion(sender, request, user, **kwargs):
    journaliser(JournalAudit.CONNEXION, objet=user.get_username(), type_objet="Session", utilisateur=user, request=request)


@receiver(user_logged_out)
def _deconnexion(sender, request, user, **kwargs):
    if user is not None:
        journaliser(JournalAudit.DECONNEXION, objet=user.get_username(), type_objet="Session", utilisateur=user, request=request)


@receiver(user_login_failed)
def _echec_connexion(sender, credentials, request=None, **kwargs):
    nom = credentials.get('username', '')
    journaliser(JournalAudit.ECHEC_CONNEXION, objet=nom, type_objet="Session",
                details=f"Tentative avec le nom d'utilisateur « {nom} ».", request=request)


# ---------- Créations, modifications, clôtures, suppressions ----------

def _champs(instance):
    return [f for f in instance._meta.concrete_fields if f.name not in CHAMPS_IGNORES]


def _valeur_lisible(instance, champ):
    if champ.choices:
        return str(dict(champ.flatchoices).get(getattr(instance, champ.attname), getattr(instance, champ.attname)))
    valeur = getattr(instance, champ.name, None)
    if valeur is None or valeur == '':
        return "—"
    if isinstance(valeur, bool):
        return "oui" if valeur else "non"
    if isinstance(valeur, datetime.datetime):
        if timezone.is_aware(valeur):
            valeur = timezone.localtime(valeur)
        return valeur.strftime('%d/%m/%Y %H:%M')
    if isinstance(valeur, datetime.date):
        return valeur.strftime('%d/%m/%Y')
    if isinstance(valeur, datetime.time):
        return valeur.strftime('%H:%M')
    texte = str(valeur)
    return texte if len(texte) <= 80 else texte[:77] + "…"


def _instantane(instance):
    return {champ.name: _valeur_lisible(instance, champ) for champ in _champs(instance)}


@receiver(pre_save)
def _avant_enregistrement(sender, instance, **kwargs):
    if sender not in MODELES_SUIVIS or not instance.pk:
        return
    ancien = sender.objects.filter(pk=instance.pk).first()
    if ancien is not None:
        instance._audit_avant = _instantane(ancien)
        instance._audit_avant_brut = {
            'statut': getattr(ancien, 'statut', None),
            'password': getattr(ancien, 'password', None),
        }


@receiver(post_save)
def _apres_enregistrement(sender, instance, created, **kwargs):
    if sender not in MODELES_SUIVIS:
        return
    type_objet = MODELES_SUIVIS[sender]

    if created:
        journaliser(JournalAudit.CREATION, objet=instance, type_objet=type_objet)
        return

    avant = getattr(instance, '_audit_avant', None)
    if avant is None:
        return
    brut = instance._audit_avant_brut
    apres = _instantane(instance)
    champs_modifies = [nom for nom in apres if avant.get(nom) != apres[nom]]
    changements = [f"{LIBELLES.get(nom, nom)} : {avant[nom]} → {apres[nom]}" for nom in champs_modifies]

    mot_de_passe_change = sender is User and brut['password'] != instance.password
    if mot_de_passe_change:
        changements.append("mot de passe modifié")
    del instance._audit_avant, instance._audit_avant_brut
    if not changements:
        return

    if getattr(instance, 'statut', None) == 'C' and brut['statut'] == 'E':
        action = JournalAudit.CLOTURE
    elif sender is Changement and champs_modifies == ['email_envoye']:
        action = JournalAudit.NOTIFICATION
    else:
        action = JournalAudit.MODIFICATION
    journaliser(action, objet=instance, type_objet=type_objet, details="\n".join(changements))


@receiver(post_delete)
def _apres_suppression(sender, instance, **kwargs):
    if sender in MODELES_SUIVIS:
        journaliser(JournalAudit.SUPPRESSION, objet=instance, type_objet=MODELES_SUIVIS[sender])


@receiver(m2m_changed)
def _destinataires_modifies(sender, instance, action, pk_set, **kwargs):
    # Ajout ou retrait de destinataires sur un type d'incident ou de changement
    if action not in ('post_add', 'post_remove') or type(instance) not in (Type_requette, Type_requette_changemen) or not pk_set:
        return
    noms = ", ".join(str(d) for d in Destinataire.objects.filter(pk__in=pk_set))
    verbe = "ajouté(s)" if action == 'post_add' else "retiré(s)"
    journaliser(JournalAudit.MODIFICATION, objet=instance, type_objet=MODELES_SUIVIS[type(instance)],
                details=f"Destinataire(s) {verbe} : {noms}")
