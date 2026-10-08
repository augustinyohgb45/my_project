from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ConnexionTests(TestCase):
    def setUp(self):
        User.objects.create_user('testeur', password='motdepasse-test')

    def test_redirige_vers_la_page_demandee(self):
        url = reverse('connexion') + '?next=' + reverse('listeincident')
        reponse = self.client.post(url, {'username': 'testeur', 'password': 'motdepasse-test'})
        self.assertRedirects(reponse, reverse('listeincident'))

    def test_ignore_une_redirection_externe(self):
        url = reverse('connexion') + '?next=https://exemple.com/'
        reponse = self.client.post(url, {'username': 'testeur', 'password': 'motdepasse-test'})
        self.assertRedirects(reponse, reverse('acceuil'))

    def test_mauvais_mot_de_passe(self):
        reponse = self.client.post(reverse('connexion'), {'username': 'testeur', 'password': 'faux'})
        self.assertContains(reponse, 'incorrect')
