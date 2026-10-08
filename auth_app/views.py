from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme


@login_required
def accueil(request):
    return redirect('acceuil')


def inscription(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form = UserCreationForm()

    return render(request, 'auth/inscription.html', {'form': form})


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
