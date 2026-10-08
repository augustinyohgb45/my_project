import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

# Logo affiché en haut et en bas des e-mails d'incident
IMAGE_EMAIL_URL = "https://www.mtn.co.ug/wp-content/uploads/sites/7/2023/02/Logo-cobranding_Artboard-3.jpg"

# Types d'incident pour lesquels un e-mail est prévu
TYPES_INCIDENT_NOTIFIES = ('indisponibilite', 'instabilite')


def envoyer_email(sujet, message, destinataires, html_message=None):
    """
    Envoie un e-mail depuis l'adresse configurée (EMAIL_HOST_USER).

    :param sujet: Le sujet de l'e-mail
    :param message: Le contenu texte de l'e-mail
    :param destinataires: La liste des adresses e-mail
    :param html_message: Une version HTML facultative du contenu
    :return: True si l'e-mail est parti, False sinon
    """
    if not destinataires:
        return False
    try:
        email = EmailMultiAlternatives(sujet, message, settings.EMAIL_HOST_USER, destinataires)
        if html_message:
            email.attach_alternative(html_message, "text/html")
        email.send()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email « {sujet} » : {e}")
        return False


def destinataires_incident(incident):
    """Destinataires du type d'incident, plus le destinataire saisi dans le formulaire."""
    emails = [destinataire.email for destinataire in incident.type_requette.destinataires.all()]
    if incident.destinataire_nouveau:
        emails.append(incident.destinataire_nouveau)
    return emails


def envoyer_email_incident(incident, resolu=False):
    """
    Envoie la notification d'ouverture ou de résolution d'un incident.

    :param incident: L'instance d'Incident
    :param resolu: True pour la notification de résolution
    :return: True si l'e-mail est parti, False sinon (type non notifié, aucun destinataire ou erreur)
    """
    type_incident = incident.type_requette.nom_requette
    if type_incident not in TYPES_INCIDENT_NOTIFIES:
        return False

    contexte = {
        'type_incident': type_incident,
        'resolu': resolu,
        'service': incident.services_impacte,
        'date_incident': incident.date_enregistrement.strftime("%d/%m/%Y"),
        'image_url': IMAGE_EMAIL_URL,
    }
    html_message = render_to_string('dashboard/emails/incident.html', contexte)
    sujet = 'Notification mise à jour incident' if resolu else 'Notification Incident'
    return envoyer_email(sujet, '', destinataires_incident(incident), html_message=html_message)


def destinataires_changement(changement):
    """Destinataires du type de changement, plus le destinataire saisi dans le formulaire."""
    emails = [destinataire.email for destinataire in changement.Type_requette_changement.destinataires.all()]
    if changement.destinataire_nouveau:
        emails.append(changement.destinataire_nouveau)
    return emails


def construire_email_changement(changement):
    """
    Construit la liste des destinataires et le message de notification d'un changement.

    :param changement: L'instance de Changement
    :return: Un tuple (emails, message)
    """
    nom_plateforme = changement.nom_plateforme
    date_changement = changement.date_changement.strftime("%d/%m/%Y")
    fin_changement = changement.fin_changement.strftime("%d/%m/%Y")
    heure_debut = changement.heure_debut.strftime("%H:%M")
    heure_fin = changement.heure_fin.strftime("%H:%M")
    services_impacte = changement.services_impacte

    requete = changement.Type_requette_changement
    type_nom = requete.nom_requette_changement

    if type_nom in ('Upgrade BD Downtime', 'Configuration Downtime', 'Maintenance planifiée Downtime'):
        message = f"Y’ello MTNers Une opération de maintenance sur la plateforme {nom_plateforme} est prévue dans la nuit du {date_changement} au {fin_changement} de {heure_debut} à {heure_fin}. Les canaux {nom_plateforme} ci-dessous seront indisponibles de {heure_debut} à {heure_fin}. Nous excusons pour les désagréments occasionnés. IT-MFS"
    elif type_nom == 'Configuration NA':
        message = f"Nous effectuerons des travaux de maintenance planifiée sur {nom_plateforme}, le {date_changement} au {fin_changement}, de {heure_debut} à {heure_fin}. Pendant cet intervalle, les utilisateurs peuvent s'attendre à < impact attendu >. IT-MFS"
    elif type_nom == 'Maintenance planifiée NA':
        message = f"Nous effectuerons des travaux de maintenance planifiée sur {services_impacte}, le {date_changement} au {fin_changement} de {heure_debut} à {heure_fin}. Pendant cet intervalle, les utilisateurs peuvent s'attendre à < impact attendu >."
    else:
        # Upgrade OS NA, Upgrade OS Downtime, Upgrade BD NA et les types ajoutés depuis
        # le formulaire : message enregistré sur le type, avec ses balises remplacées
        message = (
            requete.message.replace("< nom de la BD et plateform >", f"nom_bd et {nom_plateforme}")
            .replace("< date début >", date_changement)
            .replace("< date fin >", fin_changement)
            .replace("< heure début >", heure_debut)
            .replace("< heure fin >", heure_fin)
            .replace("< nom du service >", str(services_impacte))
        )

    return destinataires_changement(changement), message


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

    if not envoyer_email('Notification Changement', message, emails):
        return False

    changement.email_envoye = True
    changement.save(update_fields=['email_envoye'])
    return True


def envoyer_email_cloture_changement(changement):
    """
    Envoie la notification de fin d'un changement aux mêmes destinataires qu'à sa création.

    :param changement: L'instance de Changement
    :return: True si l'e-mail est parti, False sinon
    """
    type_nom = changement.Type_requette_changement.nom_requette_changement
    signature = "La DSI" if type_nom == 'Upgrade BD NA' else "IT-MFS"
    message = (
        f"Yello MTNers, veuillez noter que le changement planifié sur la plateforme {changement.nom_plateforme} "
        f"du {changement.date_changement.strftime('%d/%m/%Y')} au {changement.fin_changement.strftime('%d/%m/%Y')}, "
        f"de {changement.heure_debut.strftime('%H:%M')} à {changement.heure_fin.strftime('%H:%M')}, est terminé. "
        f"Merci pour votre compréhension. {signature}"
    )
    return envoyer_email('Notification de mise à jour de changement', message, destinataires_changement(changement))
