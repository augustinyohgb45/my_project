from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .form import *
from .utils import send_email_u
import logging


# Create your views here.

def acceuil(request):
    context = {
        'is_superuser' : request.user.is_superuser
    }
    return render(request, 'dashboard/index.html')
    


# views.py



logger = logging.getLogger(__name__)

@login_required
def incident(request):
    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.user = request.user
            incident.save()
            
            # Récupérer les destinataires sélectionnés
            destinataires = form.cleaned_data['destinataires']
            emails = [d.email for d in destinataires.all()]

            subject = 'Notification Incident'
            message = "Chers clients, nous rencontrons un souci qui affecte votre service."
            try:
                send_email_u(subject, message, emails)
            except Exception as e:
                logger.error(f'Error sending email: {e}')
                # Handle the error as needed

            return redirect("acceuil")  # Remplacez par l'URL de succès réelle
    else:
        form = IncidentForm()

    return render(request, 'dashboard/incident.html', {'form': form})
from .form import ChangementForm

def changement(request):
    if request.method == "POST":
        form = ChangementForm(request.POST)
        if form.is_valid():
            changement = form.save(commit=False)
            changement.user = request.user
            changement.save()
            
            
            desti = changement.destinataires.email
            
            subject = 'notification Changement'
            message = "Chers client nous effectuerons un changement"
            destinataire = [desti,]
            
            send_email_u(subject,message,destinataire)
            return redirect("acceuil")  # Rediriger vers une page de succès ou une autre vue pertinente
    else:
        form = ChangementForm()

    return render(request, 'dashboard/changement.html', {'form': form})


def listeincident(request):
    incidents = Incident.objects.select_related('user').prefetch_related('destinataires').all()
    incidents_en_cours = Incident.objects.filter(statut='E').count()
    return render(request, 'dashboard/listeincident.html', {
        'incidents': incidents,
        'incidents_en_cours': incidents_en_cours
    })


def listechangement(request):
    changements = Changement.objects.select_related('user').prefetch_related('destinataires').all() #récuperer les champs et le nom user
    return render(request, 'dashboard/listechangement.html', {'changements': changements})