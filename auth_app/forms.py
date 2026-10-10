from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth.models import User

TEXTE_ADMIN = "Peut gérer les utilisateurs et accéder à l'administration Django."


class StyleFormulaireMixin:
    """Classe Bootstrap sur chaque champ texte et marquage des champs en erreur."""
    champs_sans_style = ('est_admin', 'is_active')

    def appliquer_style(self):
        for nom, champ in self.fields.items():
            if nom not in self.champs_sans_style:
                champ.widget.attrs['class'] = 'form-control'

    def full_clean(self):
        super().full_clean()
        for nom in self.errors:
            if nom in self.fields and nom not in self.champs_sans_style:
                self.fields[nom].widget.attrs['class'] += ' is-invalid'


class NouvelUtilisateurForm(StyleFormulaireMixin, UserCreationForm):
    """Création d'un compte par un administrateur."""
    email = forms.EmailField(
        required=False,
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={'placeholder': 'prenom.nom@exemple.com'}),
    )
    est_admin = forms.BooleanField(required=False, label="Administrateur", help_text=TEXTE_ADMIN)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {'username': "Nom d'utilisateur", 'first_name': "Prénom", 'last_name': "Nom"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = "Mot de passe"
        self.fields['password2'].label = "Confirmation du mot de passe"
        self.appliquer_style()

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        if self.cleaned_data.get('est_admin'):
            utilisateur.is_staff = True
            utilisateur.is_superuser = True
        if commit:
            utilisateur.save()
        return utilisateur


class ModifierUtilisateurForm(StyleFormulaireMixin, forms.ModelForm):
    """Modification des informations, du rôle et de l'état d'un compte."""
    est_admin = forms.BooleanField(required=False, label="Administrateur", help_text=TEXTE_ADMIN)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_active')
        labels = {
            'first_name': "Prénom",
            'last_name': "Nom",
            'email': "Adresse e-mail",
            'is_active': "Compte actif",
        }
        help_texts = {'is_active': "Un compte désactivé ne peut plus se connecter ; son historique est conservé."}

    def __init__(self, *args, utilisateur_connecte=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.utilisateur_connecte = utilisateur_connecte
        self.fields['est_admin'].initial = self.instance.is_superuser
        self.appliquer_style()

    def clean(self):
        cleaned_data = super().clean()
        # Un administrateur ne peut pas se retirer ses propres droits ni se désactiver
        if self.utilisateur_connecte and self.instance.pk == self.utilisateur_connecte.pk:
            if not cleaned_data.get('est_admin'):
                self.add_error('est_admin', "Vous ne pouvez pas retirer vos propres droits d'administrateur.")
            if not cleaned_data.get('is_active'):
                self.add_error('is_active', "Vous ne pouvez pas désactiver votre propre compte.")
        return cleaned_data

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.is_superuser = utilisateur.is_staff = bool(self.cleaned_data.get('est_admin'))
        if commit:
            utilisateur.save()
        return utilisateur


class NouveauMotDePasseForm(StyleFormulaireMixin, SetPasswordForm):
    """Définition d'un nouveau mot de passe par un administrateur."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = "Nouveau mot de passe"
        self.fields['new_password2'].label = "Confirmation"
        self.appliquer_style()
