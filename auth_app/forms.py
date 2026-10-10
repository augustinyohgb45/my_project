from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NouvelUtilisateurForm(UserCreationForm):
    """Création d'un compte par un administrateur."""
    email = forms.EmailField(
        required=False,
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={'placeholder': 'prenom.nom@exemple.com'}),
    )
    est_admin = forms.BooleanField(
        required=False,
        label="Administrateur",
        help_text="Peut ajouter des utilisateurs et accéder à l'administration Django.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
        labels = {'username': "Nom d'utilisateur"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = "Mot de passe"
        self.fields['password2'].label = "Confirmation du mot de passe"
        for nom, champ in self.fields.items():
            if nom != 'est_admin':
                champ.widget.attrs['class'] = 'form-control'

    def full_clean(self):
        super().full_clean()
        for nom in self.errors:
            if nom in self.fields and nom != 'est_admin':
                self.fields[nom].widget.attrs['class'] += ' is-invalid'

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        if self.cleaned_data.get('est_admin'):
            utilisateur.is_staff = True
            utilisateur.is_superuser = True
        if commit:
            utilisateur.save()
        return utilisateur
