import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def construire_email_changement(changement):
    """
    Construit la liste des destinataires et le message de notification d'un changement.

    :param changement: L'instance de Changement
    :return: Un tuple (emails, message). Le message est vide si le type de requête n'est pas reconnu.
    """
    nom_plateforme = changement.nom_plateforme
    bd_plateform = f"nom_bd et {nom_plateforme}"
    date_changement = changement.date_changement.strftime("%d/%m/%Y")
    fin_changement = changement.fin_changement.strftime("%d/%m/%Y")
    heure_debut = changement.heure_debut.strftime("%H:%M")
    heure_fin = changement.heure_fin.strftime("%H:%M")
    services_impacte = changement.services_impacte

    # Type de requête choisi et ses destinataires (communs à tous les types)
    requete = changement.Type_requette_changement
    type_nom = requete.nom_requette_changement
    emails = [destinataire.email for destinataire in requete.destinataires.all()]
    if changement.destinataire_nouveau:
        emails.append(changement.destinataire_nouveau)

    # Déterminer le message en fonction du type de requête
    message = ""
    if type_nom in ('Upgrade OS NA', 'Upgrade OS Downtime', 'Upgrade BD NA'):
        message = (
            requete.message.replace("< nom de la BD et plateform >", bd_plateform)
            .replace("< date début >", date_changement)
            .replace("< date fin >", fin_changement)
            .replace("< heure début >", heure_debut)
            .replace("< heure fin >", heure_fin)
            .replace("< nom du service >", str(services_impacte))
        )
    elif type_nom in ('Upgrade BD Downtime', 'Configuration Downtime', 'Maintenance planifiée Downtime'):
        message = f"Y’ello MTNers Une opération de maintenance sur la plateforme {nom_plateforme} est prévue dans la nuit du {date_changement} au {fin_changement} de {heure_debut} à {heure_fin}. Les canaux {nom_plateforme} ci-dessous seront indisponibles de {heure_debut} à {heure_fin}. Nous excusons pour les désagréments occasionnés. IT-MFS"
    elif type_nom == 'Configuration NA':
        message = f"Nous effectuerons des travaux de maintenance planifiée sur {nom_plateforme}, le {date_changement} au {fin_changement}, de {heure_debut} à {heure_fin}. Pendant cet intervalle, les utilisateurs peuvent s'attendre à < impact attendu >. IT-MFS"
    elif type_nom == 'Maintenance planifiée NA':
        message = f"Nous effectuerons des travaux de maintenance planifiée sur {services_impacte}, le {date_changement} au {fin_changement} de {heure_debut} à {heure_fin}. Pendant cet intervalle, les utilisateurs peuvent s'attendre à < impact attendu >."

    return emails, message


def envoyer_email_changement(changement):
    """
    Envoie la notification d'un changement et le marque comme envoyé en cas de succès.

    :param changement: L'instance de Changement
    :return: True si l'e-mail est parti, False sinon
    """
    emails, message = construire_email_changement(changement)
    if not emails or not message:
        logger.error(f"Changement {changement.id} : aucun destinataire ou message, e-mail non envoyé.")
        return False

    try:
        send_mail(
            'Notification Changement',
            message,
            settings.EMAIL_HOST_USER,
            emails,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email du changement {changement.id} : {e}")
        return False

    changement.email_envoye = True
    changement.save(update_fields=['email_envoye'])
    return True


def send_email_u(subjet: str, message, receivers: list):
    """This fonction help to send a customize email to a specific user or set of users."""

    try:
        send_mail(
            subjet,
            message,
            settings.EMAIL_HOST_USER,
            receivers,
            fail_silently=True,
            html_message=message,
        )

        return True

    except Exception as e:
        logger.error(e)

    return False
