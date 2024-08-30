from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Incident, Changement
from .form import IncidentForm, ChangementForm
from .utils import send_email_u
import logging
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

@login_required(login_url="connexion")
def acceuil(request):
    nb_incidents_clotures = Incident.objects.filter(statut='C').count()
    nb_changements_clotures = Changement.objects.filter(statut='C').count()
    nb_incident_en_cours = Incident.objects.filter(statut = 'E').count()
    nb_changement_en_cours = Changement.objects.filter(statut = 'E').count()
    
    context = {
        
        'is_superuser': request.user.is_superuser,
        'nb_incidents_clotures': nb_incidents_clotures,
        'nb_changements_clotures': nb_changements_clotures,
        'nb_incident_en_cours' : nb_incident_en_cours,
        'nb_changement_en_cours' : nb_changement_en_cours,
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def incident(request):
    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.user = request.user
            incident.save()
            
            # Collecter les emails des destinataires
            emails = []
            if incident.destinataire_nouveau:
                emails.append(incident.destinataire_nouveau)

            service_impacte = incident.services_impacte
            date_incident = incident.date_enregistrement.strftime("%d/%m/%Y")
            
            subject = 'Notification Incident'
            message_html = ""
            
            # URL de l'image
            image_url = "https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-for-development/wp-content/uploads/2019/04/LOGO-MTN-MFS-CI-1-01.png"
            # image_url2 = "https://attachments.office.net/owa/Yoh.Gbetibouo%40mtn.com/service.svc/s/GetAttachmentThumbnail?id=AAMkADA2ODYzZTFkLTExMjktNDFlNC05MTIyLTA4NmRmNzdmMmZkYwBGAAAAAABJi%2FG7cwEeRqmru44PYNQhBwAK8QQnPWhTT6hQhIhzzm0qAAAAAAEMAAAK8QQnPWhTT6hQhIhzzm0qAAAykJoUAAABEgAQAL13esNbkFJDsQRV%2BdXhQs0%3D&thumbnailType=2&token=eyJhbGciOiJSUzI1NiIsImtpZCI6IkU1RDJGMEY4REE5M0I2NzA5QzQzQTlFOEE2MTQzQzAzRDYyRjlBODAiLCJ0eXAiOiJKV1QiLCJ4NXQiOiI1ZEx3LU5xVHRuQ2NRNm5vcGhROEE5WXZtb0EifQ.eyJvcmlnaW4iOiJodHRwczovL291dGxvb2sub2ZmaWNlLmNvbSIsInVjIjoiZjQ1ZThhY2U1MDVkNDA2MDk2ZTFkNTVjOWNhNmQ2NzkiLCJzaWduaW5fc3RhdGUiOiJrbXNpIiwidmVyIjoiRXhjaGFuZ2UuQ2FsbGJhY2suVjEiLCJhcHBjdHhzZW5kZXIiOiJPd2FEb3dubG9hZEBjOWI5Y2I1MC0zNjQ0LTRkYjQtYTI2Ny1mYTg0ZGYyZjRjZWIiLCJpc3NyaW5nIjoiV1ciLCJhcHBjdHgiOiJ7XCJtc2V4Y2hwcm90XCI6XCJvd2FcIixcInB1aWRcIjpcIjExNTM4MDExMjkyNjc4MzMyNjNcIixcInNjb3BlXCI6XCJPd2FEb3dubG9hZFwiLFwib2lkXCI6XCI1Y2I0ODAyYy00MGUyLTQzMjItODM4OC00ZTZmYzcyMDFkYjNcIixcInByaW1hcnlzaWRcIjpcIlMtMS01LTIxLTI0Mjc1MTU1NDktODQ0ODgzODgtMzY5OTAxNTgzNy00NDczMDkxNFwifSIsIm5iZiI6MTcyNTAyNDIzNSwiZXhwIjoxNzI1MDI0NTM1LCJpc3MiOiIwMDAwMDAwMi0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDBAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiYXVkIjoiMDAwMDAwMDItMDAwMC0wZmYxLWNlMDAtMDAwMDAwMDAwMDAwL2F0dGFjaG1lbnRzLm9mZmljZS5uZXRAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiaGFwcCI6Im93YSJ9.UT2dgdK5DKl-MtpxubyNWe0bpJXE3xXa5w-h_HIdEcfothkj1DU6iCZFS6tNrrp4o2Je4lZ2Nd1CSUPgUdvHnnsTdbr9fKRNTXPSgOtEnYMXKm1lcH56UEhB9WrXkzY6UTiPOPMtsZasb1Ek9raGtwvoX_OTZHii9n8GWOqZg2JILf-UdsiTAtK_OomIHCRLs9H_7VqAUM6Ri9X8fwDNOS44s28WXpIjny-J58Orf2TRQf4Bmrw9SrFE5Mk3-ojAujJO2ASTORArnbyUFmdGCZjL8RHKCQlX9p6j9vMvD-TEgqfdyYNeKTHVgs9C_7rVblDMuhjfZf3gRmQnhNuX8A&X-OWA-CANARY=bdvoV20F57YAAAAAAAAAAMAI9RX3yNwYfcACiODr9TiUZjHaTnPEP_m_1dvZ64xXSL5uEZe4288.&owa=outlook.office.com&scriptVer=20240816003.15&clientId=7F90C63FA8F24489B8ECA1D98477B826&animation=true"
            if incident.Type_requette_id.Nom_requette == 'indisponibilite':
                emails.append('julienkadjakassi@gmail.com')
                message_html = f"""
                <html>
                    <body>
                        <!-- Image en haut -->
                        <div style="text-align: center;">
                            <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
                        </div>
                        <p>Y’ello MTNers,</p>
                        <p>Nous observons une indisponibilité du service {service_impacte} depuis {date_incident}. Les équipes sont mobilisées pour le rétablissement des services dans les plus brefs délais.</p>
                        <p>Merci pour votre compréhension.</p>
                        <p>LA DSI</p>
                        <!-- Image en bas -->
                        <div style="text-align: center;">
                            <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
                        </div>
                    </body>
                </html>
                """
            elif incident.Type_requette_id.Nom_requette == 'instabilite':
                emails.append('gerardyeboua35@gmail.com')
                message_html = f"""
                <html>
                    <body>
                        <!-- Image en haut -->
                        <div style="text-align: center;">
                            <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
                        </div>
                        <p>Y’ello MTNers,</p>
                        <p>Nous observons une perturbation du service {service_impacte} depuis {date_incident}. Les équipes sont mobilisées pour le rétablissement des services dans les plus brefs délais.</p>
                        <p>Merci pour votre compréhension.</p>
                        <p>IT-MFS</p>
                        <!-- Image en bas -->
                        <div style="text-align: center;">
                            <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
                        </div>
                    </body>
                </html>
                """
            
            # Envoi de l'email avec rendu HTML
            try:
                email = EmailMultiAlternatives(subject, '', to=emails)
                email.attach_alternative(message_html, "text/html")
                email.send()
            except Exception as e:
                logger.error(f'Error sending email: {e}')
                
            return redirect("acceuil")  
    else:
        form = IncidentForm()

    return render(request, 'dashboard/incident.html', {'form': form})


def changement(request):
    form = ChangementForm()
    if request.method == "POST":
        form = ChangementForm(request.POST)
        if form.is_valid():
            print("formulaire valide.")
            # Sauvegarder le changement sans encore le commettre
            changement = form.save(commit=False)
            changement.user = request.user
            
            # Gestion de la sauvegarde
            try:
                changement.save()
            except Exception as e:
                print("chamgement non valide.")
                messages.error(request, f"Erreur lors de la sauvegarde du changement : {e}")
                return redirect("changement")  # Retourne à la page de changement pour afficher l'erreur

            # Préparer les données pour l'email
            service_impacte = changement.services_impacte
            date_changement = changement.date_changement.strftime("%d/%m/%Y")
            fin_changement = changement.fin_changement.strftime("%d/%m/%Y")
            nom_plateforme = changement.nom_plateforme
            heure_debut = changement.heure_debut
            heure_fin = changement.heure_fin
            
            message = ""
            emails = []

            # Déterminer le message et l'email en fonction du type de requête
            if changement.Type_requette_changement_id.Nom_requette_changement == 'Upgrade OS NA':
                emails.append('sekongoismael0@gmail.com')
                message = f"Y’ello MTNers, une opération de maintenance sur la base de données <nom de la BD et {nom_plateforme} est prévue dans la nuit du {date_changement} au {fin_changement}. Cette opération n'aura aucun impact sur {service_impacte}. IT-MFS."
                print("email valide.")
            elif changement.Type_requette_changement_id.Nom_requette_changement == 'Upgrade OS Downtime':
                emails.append('julienkadjakassi@gmail.com')
                message = f"Y’ello MTNers   Une opération de maintenance sur la plateforme {nom_plateforme} est prévue dans la nuit du {date_changement} au  {fin_changement} de {heure_debut}  à  {heure_fin}. Les canaux {nom_plateforme} ci-dessous seront indisponibles de {heure_debut} à  {heure_fin}  •  Nous excusons pour les désagréments occasionnés. IT-MFS"
                
            elif changement.Type_requette_changement_id.Nom_requette_changement == 'Upgrade BD NA':
                emails.append('gerardyeboua35@gmail.com')
                message = f"Y’ello MTNers   Une opération de maintenance sur la base de données  < nom de la BD et {nom_plateforme} est prévue dans la nuit du  {date_changement} au  {fin_changement} de  {heure_debut} à {heure_fin} . Cette opération n'aura aucun impact sur  {service_impacte}"
            
            elif changement.Type_requette_changement_id.Nom_requette_changement == 'Upgrade BD Downtime':
                emails.append('julienkadjakassi@gmail.com')
                message = f"Y’ello MTNers   Une opération de maintenance sur la plateforme {nom_plateforme} est prévue dans la nuit du {date_changement} au  {fin_changement} de {heure_debut} à  {heure_fin}. Les canaux {nom_plateforme} ci-dessous seront indisponibles de {heure_debut} à  {heure_fin} .Nous excusons pour les désagréments occasionnés. IT-MFS"
            elif changement.Type_requette_changement_id.Nom_requette_changement == 'Configuration NA':
                emails.append('gerardyeboua35@gmail.com')
                message = f"Nous effectuerons des travaux de maintenance planifiée sur {nom_plateforme} , le {date_changement} au {fin_changement}, de {heure_debut} à {heure_fin} . Pendant cet intervalle, les utilisateurs peuvent s'attendre à < impact attendu >. IT-MFS"
            
            elif changement.Type_requette_changement_id.Nom_requette_changement == 'Configuration Downtime':
                emails.append('gerardyeboua35@gmail.com')
                message = f"Y’ello MTNers   Une opération de maintenance sur la plateforme {nom_plateforme} est prévue dans la nuit du {date_changement} au  {fin_changement} de  {heure_debut} à  {heure_fin}. Les canaux {nom_plateforme} ci-dessous seront indisponibles de {heure_debut} et {heure_fin}•  Nous excusons pour les désagréments occasionnés. IT-MFS"
            
            elif changement.Type_requette_changement_id.Nom_requette_changement == 'Maintenance planifiée NA':
                emails.append('gerardyeboua35@gmail.com')
                message = f"Nous effectuerons des travaux de maintenance planifiée sur {service_impacte}, le {date_changement} au {fin_changement} de {heure_debut} à {heure_fin}. Pendant cet intervalle, les utilisateurs peuvent s'attendre à < impact attendu >."
            
            elif changement.Type_requette_changement_id.Nom_requette_changement == 'Maintenance planifiée Downtime':
                emails.append('gerardyeboua35@gmail.com')
                message = f"Y’ello MTNers   Une opération de maintenance sur la plateforme {nom_plateforme} est prévue dans la nuit du {date_changement} au  {fin_changement} de  {heure_debut} à  {heure_fin}. Les canaux {nom_plateforme} ci-dessous seront indisponibles de {heure_debut} à  {heure_fin}.  Nous excusons pour les désagréments occasionnés. IT-MFS"
            
            

            # Ajoutez les autres conditions ici...
            
            # Vérifier si des emails sont disponibles
            if not emails and not changement.destinataire_nouveau:
                
                messages.error(request, "Aucun destinataire n'a été trouvé pour l'envoi de l'email.")
                return redirect("changement")

            # Ajouter l'email d'un nouveau destinataire s'il est fourni
            if changement.destinataire_nouveau:
                emails.append(changement.destinataire_nouveau)

            # Vérification de la composition du message
            if not message:
                print("message non valide.")
                messages.error(request, "Aucun message n'a été généré pour le changement.")
                return redirect("changement")

            # Envoyer l'email
            email_status = send_email_u('Notification de Changement', message, emails)

            if email_status:  # Supposons que send_email_u retourne un boolean pour indiquer le succès ou l'échec
                messages.success(request, "L'email a été envoyé avec succès.")
            else:
                messages.error(request, "Une erreur s'est produite lors de l'envoi de l'email.")
            print(" Tout est bon.")
            # Redirection après succès
            return redirect("acceuil")
    else:
        form = ChangementForm()
        print("Grave error .")
    return render(request, 'dashboard/changement.html', {'form': form})
 


def listeincident(request):
    incidents = Incident.objects.select_related('user').all()
    incidents_en_cours = Incident.objects.filter(statut='E')
    return render(request, 'dashboard/listeincident.html', {
        'incidents': incidents,
        'incidents_en_cours': incidents_en_cours 
    })

def listechangement(request):
    changements = Changement.objects.select_related('user')
    changement_en_cours = Changement.objects.filter(statut='E')
    return render(request, 'dashboard/listechangement.html', {
        'changements': changements,
        'changement_en_cours': changement_en_cours
    })
    
    

def action_statut(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    
    if request.method == 'POST':
        # Mettre à jour le statut de l'incident
        incident.en_cours = False
        incident.statut = 'C'
        incident.save()
        
        # Collecter les emails des destinataires
        emails = []
        if incident.destinataire_nouveau:
            emails.append(incident.destinataire_nouveau)

        # Préparer les informations pour le message
        service_impacte = incident.services_impacte
        date_incident = incident.date_enregistrement.strftime("%d/%m/%Y")
        
        subject = 'Notification mise à jour incident'
        message_html = ""
        
        # URL de l'image
        image_url = "https://attachments.office.net/owa/Yoh.Gbetibouo%40mtn.com/service.svc/s/GetAttachmentThumbnail?id=AAMkADA2ODYzZTFkLTExMjktNDFlNC05MTIyLTA4NmRmNzdmMmZkYwBGAAAAAABJi%2FG7cwEeRqmru44PYNQhBwAK8QQnPWhTT6hQhIhzzm0qAAAAAAEMAAAK8QQnPWhTT6hQhIhzzm0qAAAykJoUAAABEgAQABy%2BEW1x6ClOjHtM7%2BMz%2Fxo%3D&thumbnailType=2&token=eyJhbGciOiJSUzI1NiIsImtpZCI6IkU1RDJGMEY4REE5M0I2NzA5QzQzQTlFOEE2MTQzQzAzRDYyRjlBODAiLCJ0eXAiOiJKV1QiLCJ4NXQiOiI1ZEx3LU5xVHRuQ2NRNm5vcGhROEE5WXZtb0EifQ.eyJvcmlnaW4iOiJodHRwczovL291dGxvb2sub2ZmaWNlLmNvbSIsInVjIjoiZjQ1ZThhY2U1MDVkNDA2MDk2ZTFkNTVjOWNhNmQ2NzkiLCJzaWduaW5fc3RhdGUiOiJrbXNpIiwidmVyIjoiRXhjaGFuZ2UuQ2FsbGJhY2suVjEiLCJhcHBjdHhzZW5kZXIiOiJPd2FEb3dubG9hZEBjOWI5Y2I1MC0zNjQ0LTRkYjQtYTI2Ny1mYTg0ZGYyZjRjZWIiLCJpc3NyaW5nIjoiV1ciLCJhcHBjdHgiOiJ7XCJtc2V4Y2hwcm90XCI6XCJvd2FcIixcInB1aWRcIjpcIjExNTM4MDExMjkyNjc4MzMyNjNcIixcInNjb3BlXCI6XCJPd2FEb3dubG9hZFwiLFwib2lkXCI6XCI1Y2I0ODAyYy00MGUyLTQzMjItODM4OC00ZTZmYzcyMDFkYjNcIixcInByaW1hcnlzaWRcIjpcIlMtMS01LTIxLTI0Mjc1MTU1NDktODQ0ODgzODgtMzY5OTAxNTgzNy00NDczMDkxNFwifSIsIm5iZiI6MTcyNTAyNjkzNiwiZXhwIjoxNzI1MDI3MjM2LCJpc3MiOiIwMDAwMDAwMi0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDBAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiYXVkIjoiMDAwMDAwMDItMDAwMC0wZmYxLWNlMDAtMDAwMDAwMDAwMDAwL2F0dGFjaG1lbnRzLm9mZmljZS5uZXRAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiaGFwcCI6Im93YSJ9.luU0B3GJjfSdlRZjy-kBmJxVUkmKnhvoNRVI7S3QAVIwjw8evMn170yoJLdIk_WZ9jReBVK8dQ845BRFnFM3yz7Y_Xw63D1vKMnBW5wpfyx_icqEGZy_Bm9MblYk6JuWJgdLbw1lAfXDpjmdFvoW2paE5sNPLJf248DB8iMLtsb4qSHkAoHSc_0AoUISgPo6LBpL8d7SM2-tSZTBcKZJxwK8jPVq81kWpeEid2ZPodsKJpqxEgaWyOYEYNP3vhe_xznv28k0AumeZ8SvUvL_CvpOfSujDxHRRX--JS5yKyeoucSifiqXjkSI1Ys7iWPy7NTU-_x2enHVm2RTIDQrmQ&X-OWA-CANARY=bdvoV20F57YAAAAAAAAAALCkdGj9yNwYjHnEMnrY_31vHJkCJ3NgV2ResknKoadhN0fuvAJMfOA.&owa=outlook.office.com&scriptVer=20240816003.15&clientId=7F90C63FA8F24489B8ECA1D98477B826&animation=true"
        image_url2 = "https://attachments.office.net/owa/Yoh.Gbetibouo%40mtn.com/service.svc/s/GetAttachmentThumbnail?id=AAMkADA2ODYzZTFkLTExMjktNDFlNC05MTIyLTA4NmRmNzdmMmZkYwBGAAAAAABJi%2FG7cwEeRqmru44PYNQhBwAK8QQnPWhTT6hQhIhzzm0qAAAAAAEMAAAK8QQnPWhTT6hQhIhzzm0qAAAykJoUAAABEgAQAL13esNbkFJDsQRV%2BdXhQs0%3D&thumbnailType=2&token=eyJhbGciOiJSUzI1NiIsImtpZCI6IkU1RDJGMEY4REE5M0I2NzA5QzQzQTlFOEE2MTQzQzAzRDYyRjlBODAiLCJ0eXAiOiJKV1QiLCJ4NXQiOiI1ZEx3LU5xVHRuQ2NRNm5vcGhROEE5WXZtb0EifQ.eyJvcmlnaW4iOiJodHRwczovL291dGxvb2sub2ZmaWNlLmNvbSIsInVjIjoiZjQ1ZThhY2U1MDVkNDA2MDk2ZTFkNTVjOWNhNmQ2NzkiLCJzaWduaW5fc3RhdGUiOiJrbXNpIiwidmVyIjoiRXhjaGFuZ2UuQ2FsbGJhY2suVjEiLCJhcHBjdHhzZW5kZXIiOiJPd2FEb3dubG9hZEBjOWI5Y2I1MC0zNjQ0LTRkYjQtYTI2Ny1mYTg0ZGYyZjRjZWIiLCJpc3NyaW5nIjoiV1ciLCJhcHBjdHgiOiJ7XCJtc2V4Y2hwcm90XCI6XCJvd2FcIixcInB1aWRcIjpcIjExNTM4MDExMjkyNjc4MzMyNjNcIixcInNjb3BlXCI6XCJPd2FEb3dubG9hZFwiLFwib2lkXCI6XCI1Y2I0ODAyYy00MGUyLTQzMjItODM4OC00ZTZmYzcyMDFkYjNcIixcInByaW1hcnlzaWRcIjpcIlMtMS01LTIxLTI0Mjc1MTU1NDktODQ0ODgzODgtMzY5OTAxNTgzNy00NDczMDkxNFwifSIsIm5iZiI6MTcyNTAyNDIzNSwiZXhwIjoxNzI1MDI0NTM1LCJpc3MiOiIwMDAwMDAwMi0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDBAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiYXVkIjoiMDAwMDAwMDItMDAwMC0wZmYxLWNlMDAtMDAwMDAwMDAwMDAwL2F0dGFjaG1lbnRzLm9mZmljZS5uZXRAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiaGFwcCI6Im93YSJ9.UT2dgdK5DKl-MtpxubyNWe0bpJXE3xXa5w-h_HIdEcfothkj1DU6iCZFS6tNrrp4o2Je4lZ2Nd1CSUPgUdvHnnsTdbr9fKRNTXPSgOtEnYMXKm1lcH56UEhB9WrXkzY6UTiPOPMtsZasb1Ek9raGtwvoX_OTZHii9n8GWOqZg2JILf-UdsiTAtK_OomIHCRLs9H_7VqAUM6Ri9X8fwDNOS44s28WXpIjny-J58Orf2TRQf4Bmrw9SrFE5Mk3-ojAujJO2ASTORArnbyUFmdGCZjL8RHKCQlX9p6j9vMvD-TEgqfdyYNeKTHVgs9C_7rVblDMuhjfZf3gRmQnhNuX8A&X-OWA-CANARY=bdvoV20F57YAAAAAAAAAAMAI9RX3yNwYfcACiODr9TiUZjHaTnPEP_m_1dvZ64xXSL5uEZe4288.&owa=outlook.office.com&scriptVer=20240816003.15&clientId=7F90C63FA8F24489B8ECA1D98477B826&animation=true"
        if incident.Type_requette_id.Nom_requette == 'indisponibilite':       
            message_html = f"""
            <html>
                <body>
                    <!-- Image en haut -->
                    <div style="text-align: center;">
                        <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
                    </div>
                    <p>Y’ello MTNers,</p>
                    <p>L'indisponibilité survenue sur le service {service_impacte} depuis {date_incident} est résolue.</p>
                    <p>Merci pour votre compréhension.</p>
                    <!-- Image en bas -->
                    <div style="text-align: center;">
                        <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
                    </div>
                </body>
            </html>
            """
        elif incident.Type_requette_id.Nom_requette == 'instabilite':
            message_html = f"""
            <html>
                <body>
                    <!-- Image en haut -->
                    <div style="text-align: center;">
                        <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
                    </div>
                    <p>Y’ello MTNers,</p>
                    <p>La perturbation survenue sur le service {service_impacte} depuis {date_incident} est résolue.</p>
                    <p>Merci pour votre compréhension.</p>
                    <p>IT-MFS</p>
                    <!-- Image en bas -->
                    <div style="text-align: center;">
                        <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
                    </div>
                </body>
            </html>
            """
    
        # Envoi de l'email avec rendu HTML
        try:
            email = EmailMultiAlternatives(subject, '', to=emails)
            email.attach_alternative(message_html, "text/html")
            email.send()
        except Exception as e:
            logger.error(f'Error sending email: {e}')
        
    return redirect('listeincident')



def action_statut_change(request, changement_id):
    changement = get_object_or_404(Changement, id=changement_id)
    if request.method == 'POST':
        changement.en_cours = False
        changement.statut = 'C'
        changement.save()
        
        emails = []
        if changement.destinataire_nouveau:
            emails.append(changement.destinataire_nouveau)
        
        #definition des variables
        nom_plateforme = changement.nom_plateforme
        date_changement = changement.date_changement.strftime("%d/%m/%Y")
        fin_changement = changement.fin_changement.strftime("%d/%m/%Y")
        
        
        
        subject = 'notification mise à jour changement'
        message = ''
        if changement.Type_requette_id.Nom_requette == 'Upgrade OS NA':
            message = f"Yello MTNers  Prière de noter l’annulation du changement planifié qui était prévu sur la plateforme {nom_plateforme} du {date_changement} et de fin > de < heure de début et de fin >.  Merci pour votre compréhension    IT-MFS"
        elif changement.Type_requette_id.Nom_requette == 'Upgrade OS Downtime':
            message = f"Yello MTNers  Prière de noter l’annulation du changement planifié qui était prévu sur la plateforme {nom_plateforme} du {date_changement} et {fin_changement} > de < heure de début et de fin >.  Merci pour votre compréhension    IT-MFS"
        
        elif changement.Type_requette_id.Nom_requette == 'Upgrade BD NA':
            message = f"Yello MTNers  Prière de noter l’annulation du changement planifié qui était prévu sur la plateforme {nom_plateforme} du {date_changement} et {fin_changement} de < heure de début et de fin >.  Merci pour votre compréhension    La DSI"
        
        elif changement.Type_requette_id.Nom_requette == 'Upgrade BD Downtime':
            message = f"Yello MTNers  Prière de noter l’annulation du changement planifié qui était prévu sur la plateforme {nom_plateforme} du {date_changement} et {fin_changement} de < heure de début et de fin >.  Merci pour votre compréhension    IT-MFS"

        elif changement.Type_requette_id.Nom_requette == 'Configuration NA':
            message = f"Yello MTNers  Prière de noter l’annulation du changement planifié qui était prévu sur la plateforme {nom_plateforme} du {date_changement} et {fin_changement} de < heure de début et de fin >.  Merci pour votre compréhension    IT-MFS"
        
        elif changement.Type_requette_id.Nom_requette == 'Configuration Downtime':
            message = f"Yello MTNers  Prière de noter l’annulation du changement planifié qui était prévu sur la plateforme {nom_plateforme} du {date_changement} de < heure de début et de fin >.  Merci pour votre compréhension    IT-MFS"
        
        elif changement.Type_requette_id.Nom_requette == 'Maintenance planifiée NA':
            message = f"Yello MTNers  Prière de noter l’annulation du changement planifié qui était prévu sur la plateforme {nom_plateforme} du {date_changement} et {fin_changement} de < heure de début et de fin >.  Merci pour votre compréhension    IT-MFS"
        
        send_email_u(subject, message, emails)
      
    return redirect('listechangement')