import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

def send_email_if_due(current_date, send_date, subject, message, recipient_list):
    """
    Envoie un e-mail si la date actuelle est égale ou postérieure à la date d'envoi.

    :param current_date: La date actuelle 
    :param send_date: La date à laquelle l'e-mail doit être envoyé
    :param subject: Le sujet de l'e-mail
    :param message: Le message de l'e-mail
    :param recipient_list: La liste des destinataires de l'e-mail (liste d'adresses e-mail)
    """
    if current_date >= send_date:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
        )
        return True
    return False



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