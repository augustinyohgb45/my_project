from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Changement, Destinataire, Service, Type_requette, Incident, Type_requette_changemen


class EmailChangementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testeur', password='motdepasse-test')
        self.client.force_login(self.user)
        self.service = Service.objects.create(nom='Mobile Money')
        destinataire = Destinataire.objects.create(nom='Equipe', contact='0000000000', email='equipe@example.com')
        self.type = Type_requette_changemen.objects.create(nom_requette_changement='Configuration Downtime')
        self.type.destinataires.add(destinataire)

    def donnees_formulaire(self, date_envoie):
        maintenant = timezone.localtime()
        return {
            'Numero_ticket': 'CHG001',
            'services_impacte': self.service.id,
            'Type_requette_changement': self.type.id,
            'date_changement': maintenant.strftime('%Y-%m-%dT%H:%M'),
            'fin_changement': (maintenant + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
            'heure_debut': '22:00',
            'heure_fin': '23:00',
            'date_envoie': timezone.localtime(date_envoie).strftime('%Y-%m-%dT%H:%M'),
            'description': 'Test',
            'nom_plateforme': 'MoMo',
            'statut': 'E',
        }

    def test_envoi_immediat_si_date_atteinte(self):
        self.client.post(reverse('changement'), self.donnees_formulaire(timezone.now() - timedelta(minutes=5)))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['equipe@example.com'])
        self.assertTrue(Changement.objects.get().email_envoye)

    def test_envoi_differe_par_la_commande(self):
        self.client.post(reverse('changement'), self.donnees_formulaire(timezone.now() + timedelta(days=1)))
        self.assertEqual(len(mail.outbox), 0)
        changement = Changement.objects.get()
        self.assertFalse(changement.email_envoye)

        # La commande n'envoie rien tant que la date n'est pas atteinte
        call_command('envoyer_emails_planifies')
        self.assertEqual(len(mail.outbox), 0)

        changement.date_envoie = timezone.now() - timedelta(minutes=1)
        changement.save()
        call_command('envoyer_emails_planifies')
        self.assertEqual(len(mail.outbox), 1)

        # Pas de second envoi
        call_command('envoyer_emails_planifies')
        self.assertEqual(len(mail.outbox), 1)

    def test_cloture_annonce_la_fin_du_changement(self):
        self.client.post(reverse('changement'), self.donnees_formulaire(timezone.now() - timedelta(minutes=5)))
        changement = Changement.objects.get()
        self.client.post(reverse('action_statut_change', args=[changement.id]))
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('est terminé', mail.outbox[1].body)
        self.assertNotIn('annulation', mail.outbox[1].body)
        self.assertEqual(mail.outbox[1].to, ['equipe@example.com'])


class EmailIncidentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testeur', password='motdepasse-test')
        self.client.force_login(self.user)
        self.service = Service.objects.create(nom='Mobile Money')

    def poster_incident(self, nom_type):
        type_requette = Type_requette.objects.create(nom_requette=nom_type)
        self.client.post(reverse('incident'), {
            'numero_ticket': 'INC001',
            'services_impacte': self.service.id,
            'type_requette': type_requette.id,
            'description': 'Test',
            'destinataire_nouveau': 'support@example.com',
            'date_envoie': timezone.localtime().strftime('%Y-%m-%dT%H:%M'),
            'statut': 'E',
        })

    def test_un_seul_email_avec_expediteur(self):
        self.poster_incident('indisponibilite')
        self.assertEqual(Incident.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotEqual(mail.outbox[0].from_email, 'webmaster@localhost')

    def test_pas_d_email_vide_pour_un_type_inconnu(self):
        self.poster_incident('autre')
        self.assertEqual(Incident.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)
