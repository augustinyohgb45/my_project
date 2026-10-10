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


class InscriptionTests(TestCase):
    donnees = {'username': 'nouveau', 'password1': 'Un-mot-de-passe-solide-42', 'password2': 'Un-mot-de-passe-solide-42'}

    def test_visiteur_redirige_vers_la_connexion(self):
        reponse = self.client.post(reverse('inscription'), self.donnees)
        self.assertRedirects(reponse, reverse('connexion') + '?next=' + reverse('inscription'))
        self.assertFalse(User.objects.filter(username='nouveau').exists())

    def test_utilisateur_normal_refuse(self):
        self.client.force_login(User.objects.create_user('simple', password='motdepasse-test'))
        self.assertEqual(self.client.get(reverse('inscription')).status_code, 403)
        self.assertEqual(self.client.post(reverse('inscription'), self.donnees).status_code, 403)
        self.assertFalse(User.objects.filter(username='nouveau').exists())

    def test_administrateur_cree_un_compte(self):
        self.client.force_login(User.objects.create_superuser('admin', password='motdepasse-test'))
        reponse = self.client.post(reverse('inscription'), self.donnees)
        self.assertRedirects(reponse, reverse('acceuil'))
        self.assertTrue(User.objects.filter(username='nouveau').exists())

    def test_case_administrateur_donne_les_droits(self):
        self.client.force_login(User.objects.create_superuser('admin', password='motdepasse-test'))
        self.client.post(reverse('inscription'), dict(self.donnees, est_admin='on'))
        nouveau = User.objects.get(username='nouveau')
        self.assertTrue(nouveau.is_superuser)
        self.assertTrue(nouveau.is_staff)
