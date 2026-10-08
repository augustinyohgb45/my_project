from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Changement
from dashboard.utils import envoyer_email_changement


class Command(BaseCommand):
    help = "Envoie les notifications des changements dont la date d'envoi est atteinte."

    def handle(self, *args, **options):
        changements = Changement.objects.filter(
            email_envoye=False,
            statut='E',
            date_envoie__lte=timezone.now(),
        )
        envoyes = 0
        for changement in changements:
            if envoyer_email_changement(changement):
                envoyes += 1
            else:
                self.stderr.write(f"Échec de l'envoi pour le changement {changement.id}.")
        self.stdout.write(f"{envoyes} e-mail(s) envoyé(s).")
