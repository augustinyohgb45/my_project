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
        self.assertRedirects(reponse, reverse('utilisateurs'))
        self.assertTrue(User.objects.filter(username='nouveau').exists())

    def test_case_administrateur_donne_les_droits(self):
        self.client.force_login(User.objects.create_superuser('admin', password='motdepasse-test'))
        self.client.post(reverse('inscription'), dict(self.donnees, est_admin='on'))
        nouveau = User.objects.get(username='nouveau')
        self.assertTrue(nouveau.is_superuser)
        self.assertTrue(nouveau.is_staff)


class GestionUtilisateursTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', password='motdepasse-test')
        self.simple = User.objects.create_user('simple', password='motdepasse-test')
        self.client.force_login(self.admin)

    def test_liste_reservee_aux_administrateurs(self):
        self.assertContains(self.client.get(reverse('utilisateurs')), 'simple')
        self.client.force_login(self.simple)
        self.assertEqual(self.client.get(reverse('utilisateurs')).status_code, 403)
        self.assertEqual(self.client.get(reverse('modifier_utilisateur', args=[self.admin.id])).status_code, 403)

    def test_promouvoir_et_modifier(self):
        reponse = self.client.post(reverse('modifier_utilisateur', args=[self.simple.id]), {
            'first_name': 'Awa', 'last_name': 'Koné', 'email': 'awa@example.com', 'is_active': 'on', 'est_admin': 'on',
        })
        self.assertRedirects(reponse, reverse('utilisateurs'))
        self.simple.refresh_from_db()
        self.assertEqual(self.simple.get_full_name(), 'Awa Koné')
        self.assertTrue(self.simple.is_superuser and self.simple.is_staff)

    def test_impossible_de_se_retirer_ses_droits(self):
        reponse = self.client.post(reverse('modifier_utilisateur', args=[self.admin.id]), {'email': '', 'is_active': 'on'})
        self.assertContains(reponse, "Vous ne pouvez pas retirer vos propres droits")
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_superuser)

    def test_desactiver_empeche_la_connexion(self):
        self.client.post(reverse('activer_utilisateur', args=[self.simple.id]))
        self.simple.refresh_from_db()
        self.assertFalse(self.simple.is_active)
        self.client.logout()
        reponse = self.client.post(reverse('connexion'), {'username': 'simple', 'password': 'motdepasse-test'})
        self.assertContains(reponse, 'incorrect')

    def test_impossible_de_se_desactiver(self):
        self.client.post(reverse('activer_utilisateur', args=[self.admin.id]))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_activation_par_get_refusee(self):
        self.assertEqual(self.client.get(reverse('activer_utilisateur', args=[self.simple.id])).status_code, 405)

    def test_changer_le_mot_de_passe(self):
        nouveau = 'Nouveau-mot-de-passe-99'
        reponse = self.client.post(reverse('modifier_utilisateur', args=[self.simple.id]), {
            'mot_de_passe': '1', 'new_password1': nouveau, 'new_password2': nouveau,
        })
        self.assertRedirects(reponse, reverse('utilisateurs'))
        self.simple.refresh_from_db()
        self.assertTrue(self.simple.check_password(nouveau))
