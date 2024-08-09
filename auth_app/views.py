from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .form import CustomUserCreationForm  # Assurez-vous que ce chemin est correct
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


#vue acceuil
@login_required
def accueil(request):
    return render(request, 'dashboard/accueil.html')

# Vue pour l'inscription
def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form = CustomUserCreationForm()

    return render(request, 'auth/inscription.html', {'form': form})



# Vue pour la connexion
def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Les champs nom d\'utilisateur et mot de passe sont requis.')
            return render(request, 'auth/connexion.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('acceuil')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            print('Mot de passe ou nom d\'utilisateur incorrect')

    return render(request, 'auth/connexion.html')

# Vue pour la déconnexion
def deconnexion(request):
    logout(request)
    return redirect('connexion')
