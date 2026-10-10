from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ModifierUtilisateurForm, NouveauMotDePasseForm, NouvelUtilisateurForm


def superadmin_requis(vue):
    """Réserve la vue aux administrateurs connectés (403 pour les autres)."""
    @login_required
    @wraps(vue)
    def vue_protegee(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return vue(request, *args, **kwargs)
    return vue_protegee


@login_required
def accueil(request):
    return redirect('acceuil')


@superadmin_requis
def utilisateurs(request):
    comptes = User.objects.order_by('-is_active', '-is_superuser', 'username')
    return render(request, 'auth/utilisateurs.html', {
        'comptes': comptes,
        'nb_actifs': sum(1 for c in comptes if c.is_active),
        'nb_admins': sum(1 for c in comptes if c.is_superuser and c.is_active),
    })


@superadmin_requis
def inscription(request):
    if request.method == 'POST':
        form = NouvelUtilisateurForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            messages.success(request, f"L'utilisateur « {utilisateur.username} » a été créé.")
            return redirect('utilisateurs')
    else:
        form = NouvelUtilisateurForm()

    return render(request, 'auth/inscription.html', {'form': form})


@superadmin_requis
def modifier_utilisateur(request, utilisateur_id):
    compte = get_object_or_404(User, pk=utilisateur_id)
    form = ModifierUtilisateurForm(instance=compte, utilisateur_connecte=request.user)
    form_mdp = NouveauMotDePasseForm(compte)

    if request.method == 'POST':
        if 'mot_de_passe' in request.POST:
            form_mdp = NouveauMotDePasseForm(compte, request.POST)
            if form_mdp.is_valid():
                form_mdp.save()
                if compte == request.user:
                    # Garder l'administrateur connecté après avoir changé son propre mot de passe
                    update_session_auth_hash(request, compte)
                messages.success(request, f"Le mot de passe de « {compte.username} » a été modifié.")
                return redirect('utilisateurs')
        else:
            form = ModifierUtilisateurForm(request.POST, instance=compte, utilisateur_connecte=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, f"Le compte « {compte.username} » a été mis à jour.")
                return redirect('utilisateurs')

    return render(request, 'auth/utilisateur_modifier.html', {
        'compte': compte,
        'form': form,
        'form_mdp': form_mdp,
    })


@superadmin_requis
@require_POST
def activer_utilisateur(request, utilisateur_id):
    compte = get_object_or_404(User, pk=utilisateur_id)
    if compte == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('utilisateurs')

    compte.is_active = not compte.is_active
    compte.save(update_fields=['is_active'])
    etat = "activé" if compte.is_active else "désactivé"
    messages.success(request, f"Le compte « {compte.username} » a été {etat}.")
    return redirect('utilisateurs')


def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Les champs nom d'utilisateur et mot de passe sont requis.")
            return render(request, 'auth/connexion.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Revenir à la page demandée avant la connexion, si elle appartient au site
            suivant = request.GET.get('next')
            if suivant and url_has_allowed_host_and_scheme(suivant, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(suivant)
            return redirect('acceuil')
        messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'auth/connexion.html')


def deconnexion(request):
    logout(request)
    return redirect('connexion')
