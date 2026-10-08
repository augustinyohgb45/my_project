from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import *
from .form import IncidentForm, ChangementForm
from .utils import send_email_u, construire_email_changement, envoyer_email_changement
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
# from django.http import JsonResponse


logger = logging.getLogger(__name__)

@login_required(login_url="connexion")
def acceuil(request):
    nb_incidents_clotures = Incident.objects.filter(statut='C').count()
    nb_changements_clotures = Changement.objects.filter(statut='C').count()
    nb_incident_en_cours = Incident.objects.filter(statut = 'E').count()
    nb_changement_en_cours = Changement.objects.filter(statut = 'E').count()
    # nb_total_incident = nb_incident_en_cours + nb_incidents_clotures
    # nb_total_changement = nb_changements_clotures + nb_changement_en_cours
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
        print("++++++++++++++++++++++++++++++++")
        if form.is_valid():
            print("=========================")

            incident = form.save(commit=False)
            incident.user = request.user
            incident.save()
            form.save_m2m()  # Sauvegarder les relations many-to-many
            
            # Collecter les emails des destinataires
            emails = []
            if incident.destinataire_nouveau:
                emails.append(incident.destinataire_nouveau)

            services_impacte = incident.services_impacte
            date_incident = incident.date_enregistrement.strftime("%d/%m/%Y")
            
            subject = 'Notification Incident'
            message = ''

                        
            # URL de l'image
            image_url = "https://www.mtn.co.ug/wp-content/uploads/sites/7/2023/02/Logo-cobranding_Artboard-3.jpg"
            
            if incident.type_requette.nom_requette == 'indisponibilite':
                emails.append('julienkadjakassi@gmail.com')
                message = f"""
                <html>
                    <body>
                        <div style="text-align: center;">
                            <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
                        </div>
                        <p style="color: blue;">Y’ello MTNers,</P>
                        <p style="color: blue;">Nous observons une indisponibilité du service {services_impacte} depuis {date_incident}. Les équipes sont mobilisées pour le rétablissement des services dans les plus brefs délais.</p>
                        <p style="color: blue;">Merci pour votre compréhension.</p>
                        <p style="color: blue;">LA DSI</p>
                        <div style="text-align: center;">
                            <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
                        </div>
                    </body>
                </html>
                """
            elif incident.type_requette.nom_requette == 'instabilite':
                emails.append('gerardyeboua35@gmail.com')
                message = f"""
                <html>
                    <body>
                        <div style="text-align: center;">
                            <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
                        </div>
                        <p style="color: blue;">Y’ello MTNers,</p>
                        <p style="color: blue;">Nous observons une perturbation du service {services_impacte} depuis {date_incident}. Les équipes sont mobilisées pour le rétablissement des services dans les plus brefs délais.</p>
                        <p style="color: blue;">Merci pour votre compréhension.</p>
                        <p style="color: blue;">IT-MFS</p>
                        <div style="text-align: center;">
                            <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
                        </div>
                    </body>
                </html>
                """
            
            # Envoi de l'email avec rendu HTML
            if emails and message:
                try:
                    email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, emails)
                    email.attach_alternative(message, "text/html")
                    email.send()
                except Exception as e:
                    logger.error(f'Erreur lors de l\'envoi de l\'email : {e}')
                
            # Redirection après la soumission réussie du formulaire
            print("Redirection vers la page d'accueil...")
            return redirect("acceuil")
        else:
            print("Erreurs du formulaire :", form.errors)  # Afficher les erreurs du formulaire
    else:
        form = IncidentForm()

    return render(request, 'dashboard/incident.html', {'form': form})


# @login_required
# def incident(request):
#     if request.method == "POST":
#         form = IncidentForm(request.POST)
#         print("++++++++++++++++++++++++++++++++")
#         if form.is_valid():
#             print("=========================")
        
#             incident = form.save(commit=False)
#             incident.user = request.user
#             incident.save()
#             form.save_m2m() # pour manytomany
            
#             # Collecter les emails des destinataires
#             emails = []
#             if incident.destinataire_nouveau:
#                 emails.append(incident.destinataire_nouveau)

#             services_impacte = incident.services_impacte
#             date_incident = incident.date_enregistrement.strftime("%d/%m/%Y")
            
#             curent_date = incident.date_enregistrement
#             date_envoie = incident.date_envoie
#             subject = 'Notification Incident'
#             message = ''
#             email_status = send_email_if_due(curent_date, date_envoie, subject, message, emails)
                        
#             # URL de l'image
            
#             image_url = "https://www.mtn.co.ug/wp-content/uploads/sites/7/2023/02/Logo-cobranding_Artboard-3.jpg"
#             # image_url2 = "https://attachments.office.net/owa/Yoh.Gbetibouo%40mtn.com/service.svc/s/GetAttachmentThumbnail?id=AAMkADA2ODYzZTFkLTExMjktNDFlNC05MTIyLTA4NmRmNzdmMmZkYwBGAAAAAABJi%2FG7cwEeRqmru44PYNQhBwAK8QQnPWhTT6hQhIhzzm0qAAAAAAEMAAAK8QQnPWhTT6hQhIhzzm0qAAAykJoUAAABEgAQAL13esNbkFJDsQRV%2BdXhQs0%3D&thumbnailType=2&token=eyJhbGciOiJSUzI1NiIsImtpZCI6IkU1RDJGMEY4REE5M0I2NzA5QzQzQTlFOEE2MTQzQzAzRDYyRjlBODAiLCJ0eXAiOiJKV1QiLCJ4NXQiOiI1ZEx3LU5xVHRuQ2NRNm5vcGhROEE5WXZtb0EifQ.eyJvcmlnaW4iOiJodHRwczovL291dGxvb2sub2ZmaWNlLmNvbSIsInVjIjoiZjQ1ZThhY2U1MDVkNDA2MDk2ZTFkNTVjOWNhNmQ2NzkiLCJzaWduaW5fc3RhdGUiOiJrbXNpIiwidmVyIjoiRXhjaGFuZ2UuQ2FsbGJhY2suVjEiLCJhcHBjdHhzZW5kZXIiOiJPd2FEb3dubG9hZEBjOWI5Y2I1MC0zNjQ0LTRkYjQtYTI2Ny1mYTg0ZGYyZjRjZWIiLCJpc3NyaW5nIjoiV1ciLCJhcHBjdHgiOiJ7XCJtc2V4Y2hwcm90XCI6XCJvd2FcIixcInB1aWRcIjpcIjExNTM4MDExMjkyNjc4MzMyNjNcIixcInNjb3BlXCI6XCJPd2FEb3dubG9hZFwiLFwib2lkXCI6XCI1Y2I0ODAyYy00MGUyLTQzMjItODM4OC00ZTZmYzcyMDFkYjNcIixcInByaW1hcnlzaWRcIjpcIlMtMS01LTIxLTI0Mjc1MTU1NDktODQ0ODgzODgtMzY5OTAxNTgzNy00NDczMDkxNFwifSIsIm5iZiI6MTcyNTAyNDIzNSwiZXhwIjoxNzI1MDI0NTM1LCJpc3MiOiIwMDAwMDAwMi0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDBAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiYXVkIjoiMDAwMDAwMDItMDAwMC0wZmYxLWNlMDAtMDAwMDAwMDAwMDAwL2F0dGFjaG1lbnRzLm9mZmljZS5uZXRAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiaGFwcCI6Im93YSJ9.UT2dgdK5DKl-MtpxubyNWe0bpJXE3xXa5w-h_HIdEcfothkj1DU6iCZFS6tNrrp4o2Je4lZ2Nd1CSUPgUdvHnnsTdbr9fKRNTXPSgOtEnYMXKm1lcH56UEhB9WrXkzY6UTiPOPMtsZasb1Ek9raGtwvoX_OTZHii9n8GWOqZg2JILf-UdsiTAtK_OomIHCRLs9H_7VqAUM6Ri9X8fwDNOS44s28WXpIjny-J58Orf2TRQf4Bmrw9SrFE5Mk3-ojAujJO2ASTORArnbyUFmdGCZjL8RHKCQlX9p6j9vMvD-TEgqfdyYNeKTHVgs9C_7rVblDMuhjfZf3gRmQnhNuX8A&X-OWA-CANARY=bdvoV20F57YAAAAAAAAAAMAI9RX3yNwYfcACiODr9TiUZjHaTnPEP_m_1dvZ64xXSL5uEZe4288.&owa=outlook.office.com&scriptVer=20240816003.15&clientId=7F90C63FA8F24489B8ECA1D98477B826&animation=true"
#             if incident.Type_requette_id.Nom_requette == 'indisponibilite':
#                 # requete = Type_requette.objects.get(Nom_requette = 'indisponibilite')
#                 # image1 = f'../../media/{requete.image1}'
#                 # image2 = f'../../media/{requete.image2}' 
#                 emails.append('julienkadjakassi@gmail.com')
#                 message = f"""
#                 <html>
#                     <body>
#                         <!-- Image en haut -->
#                         <div style="text-align: center;">
#                             <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
#                         </div>
#                         <p style="color: blue;">Y’ello MTNers,</P>
#                         <p style="color: blue;">Nous observons une indisponibilité du service {services_impacte} depuis {date_incident}. Les équipes sont mobilisées pour le rétablissement des services dans les plus brefs délais.</p>
#                         <p style="color: blue;">Merci pour votre compréhension.</p>
#                         <p style="color: blue;">LA DSI</p>
#                         <!-- Image en bas -->
#                         <div style="text-align: center;">
#                             <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
#                         </div>
#                     </body>
#                 </html>
#                 """
#             elif incident.Type_requette_id.Nom_requette == 'instabilite':
#                 emails.append('gerardyeboua35@gmail.com')
#                 message = f"""
#                 <html>
#                     <body>
#                         <!-- Image en haut -->
#                         <div style="text-align: center;">
#                             <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
#                         </div>
#                         <p style="color: blue;">Y’ello MTNers,</p>
#                         <p style="color: blue;">Nous observons une perturbation du service {services_impacte} depuis {date_incident}. Les équipes sont mobilisées pour le rétablissement des services dans les plus brefs délais.</p>
#                         <p style="color: blue;">Merci pour votre compréhension.</p>
#                         <p style="color: blue;">IT-MFS</p>
#                         <!-- Image en bas -->
#                         <div style="text-align: center;">
#                             <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
#                         </div>
#                     </body>
#                 </html>
#                 """
            
#             # Envoi de l'email avec rendu HTML
#             try:
#                 email = EmailMultiAlternatives(subject, '', to=emails)
#                 email.attach_alternative(message, "text/html")
#                 email.send()
#             except Exception as e:
#                 logger.error(f'Error sending email: {e}')
                
#             return redirect("acceuil")  
#     else:
#         form = IncidentForm()

#     return render(request, 'dashboard/incident.html', {'form': form})

@login_required
def changement(request):
    form = ChangementForm()
    if request.method == "POST":
        form = ChangementForm(request.POST)
        if form.is_valid():
            print("formulaire valide.")
            # Sauvegarder le changement sans encore le commettre
            changement = form.save(commit=False)
            changement.user = request.user
            
            # Vérification si un nouveau service est ajouté
            service_value = request.POST.get('services_impacte')
            print(f"Service sélectionné: {service_value}")
            if service_value == 'add_new_service':
                new_service = request.POST.get('new_service')
                print(f"Nouveau service saisi: {new_service}")
                if new_service:
                    # Ajouter le nouveau service au modèle
                    service, created = Service.objects.get_or_create(nom=new_service)
                    print(f"Nouveau service créé: {service}, créé: {created}")
                    changement.services_impacte = service
                else:
                    messages.error(request, "Veuillez entrer un nouveau service.")
                    return redirect("changement")
            else:
                changement.services_impacte_id = service_value  
                
            # Vérification si un nouveau type de changement est ajouté
            type_requette_value = request.POST.get('Type_requette_changement')
            print(f"Type de requête sélectionné: {type_requette_value}")
            if type_requette_value == 'add_new':
                new_type = request.POST.get('new_type')
                print(f"Nouveau type saisi: {new_type}")
                if new_type:        
                    # Ajouter le nouveau type au modèle
                    type_requette, created = Type_requette_changemen.objects.get_or_create(nom_requette_changement=new_type)
                    print(f"Nouveau type créé: {type_requette}, créé: {created}")
                    changement.Type_requette_changement = type_requette
                else:
                    messages.error(request, "Veuillez entrer un nouveau type de changement.")
                    return redirect("changement")
            else:
                changement.Type_requette_changement = Type_requette_changemen.objects.get(pk=type_requette_value)
            
            # Sauvegarder le changement
            try:
                changement.save()
            except Exception as e:
                messages.error(request, f"Erreur lors de la sauvegarde du changement : {e}")
                return redirect("changement")

            # Vérifier que la notification peut être construite
            emails, message = construire_email_changement(changement)
            if not emails:
                messages.error(request, "Aucun destinataire n'a été trouvé pour l'envoi de l'email.")
                return redirect("changement")
            if not message:
                messages.error(request, "Aucun message n'a été généré pour le changement.")
                return redirect("changement")

            # Envoyer maintenant si la date d'envoi est atteinte, sinon laisser
            # la commande envoyer_emails_planifies s'en charger
            if changement.date_envoie <= timezone.now():
                if envoyer_email_changement(changement):
                    messages.success(request, "L'email a été envoyé avec succès.")
                else:
                    messages.error(request, "Une erreur s'est produite lors de l'envoi de l'email.")
            else:
                date_envoi = timezone.localtime(changement.date_envoie).strftime("%d/%m/%Y à %H:%M")
                messages.success(request, f"L'email sera envoyé le {date_envoi}.")

            # Redirection après succès
            return redirect("acceuil")
    else:
        form = ChangementForm()

    return render(request, 'dashboard/changement.html', {'form': form})


@login_required
def listeincident(request):
    incidents = Incident.objects.select_related('user').all()
    incidents_en_cours = Incident.objects.filter(statut='E')
    return render(request, 'dashboard/listeincident.html', {
        'incidents': incidents,
        'incidents_en_cours': incidents_en_cours 
    })

@login_required
def listechangement(request):
    changements = Changement.objects.select_related('user')
    changement_en_cours = Changement.objects.filter(statut='E')
    return render(request, 'dashboard/listechangement.html', {
        'changements': changements,
        'changement_en_cours': changement_en_cours
    })
    
    

@login_required
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
        services_impacte = incident.services_impacte
        date_incident = incident.date_enregistrement.strftime("%d/%m/%Y")
        
        subject = 'Notification mise à jour incident'
        message = ""
        
        # URL de l'image
        image_url = "https://www.mtn.co.ug/wp-content/uploads/sites/7/2023/02/Logo-cobranding_Artboard-3.jpg"        
        # image_url2 = "https://attachments.office.net/owa/Yoh.Gbetibouo%40mtn.com/service.svc/s/GetAttachmentThumbnail?id=AAMkADA2ODYzZTFkLTExMjktNDFlNC05MTIyLTA4NmRmNzdmMmZkYwBGAAAAAABJi%2FG7cwEeRqmru44PYNQhBwAK8QQnPWhTT6hQhIhzzm0qAAAAAAEMAAAK8QQnPWhTT6hQhIhzzm0qAAAykJoUAAABEgAQAL13esNbkFJDsQRV%2BdXhQs0%3D&thumbnailType=2&token=eyJhbGciOiJSUzI1NiIsImtpZCI6IkU1RDJGMEY4REE5M0I2NzA5QzQzQTlFOEE2MTQzQzAzRDYyRjlBODAiLCJ0eXAiOiJKV1QiLCJ4NXQiOiI1ZEx3LU5xVHRuQ2NRNm5vcGhROEE5WXZtb0EifQ.eyJvcmlnaW4iOiJodHRwczovL291dGxvb2sub2ZmaWNlLmNvbSIsInVjIjoiZjQ1ZThhY2U1MDVkNDA2MDk2ZTFkNTVjOWNhNmQ2NzkiLCJzaWduaW5fc3RhdGUiOiJrbXNpIiwidmVyIjoiRXhjaGFuZ2UuQ2FsbGJhY2suVjEiLCJhcHBjdHhzZW5kZXIiOiJPd2FEb3dubG9hZEBjOWI5Y2I1MC0zNjQ0LTRkYjQtYTI2Ny1mYTg0ZGYyZjRjZWIiLCJpc3NyaW5nIjoiV1ciLCJhcHBjdHgiOiJ7XCJtc2V4Y2hwcm90XCI6XCJvd2FcIixcInB1aWRcIjpcIjExNTM4MDExMjkyNjc4MzMyNjNcIixcInNjb3BlXCI6XCJPd2FEb3dubG9hZFwiLFwib2lkXCI6XCI1Y2I0ODAyYy00MGUyLTQzMjItODM4OC00ZTZmYzcyMDFkYjNcIixcInByaW1hcnlzaWRcIjpcIlMtMS01LTIxLTI0Mjc1MTU1NDktODQ0ODgzODgtMzY5OTAxNTgzNy00NDczMDkxNFwifSIsIm5iZiI6MTcyNTAyNDIzNSwiZXhwIjoxNzI1MDI0NTM1LCJpc3MiOiIwMDAwMDAwMi0wMDAwLTBmZjEtY2UwMC0wMDAwMDAwMDAwMDBAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiYXVkIjoiMDAwMDAwMDItMDAwMC0wZmYxLWNlMDAtMDAwMDAwMDAwMDAwL2F0dGFjaG1lbnRzLm9mZmljZS5uZXRAYzliOWNiNTAtMzY0NC00ZGI0LWEyNjctZmE4NGRmMmY0Y2ViIiwiaGFwcCI6Im93YSJ9.UT2dgdK5DKl-MtpxubyNWe0bpJXE3xXa5w-h_HIdEcfothkj1DU6iCZFS6tNrrp4o2Je4lZ2Nd1CSUPgUdvHnnsTdbr9fKRNTXPSgOtEnYMXKm1lcH56UEhB9WrXkzY6UTiPOPMtsZasb1Ek9raGtwvoX_OTZHii9n8GWOqZg2JILf-UdsiTAtK_OomIHCRLs9H_7VqAUM6Ri9X8fwDNOS44s28WXpIjny-J58Orf2TRQf4Bmrw9SrFE5Mk3-ojAujJO2ASTORArnbyUFmdGCZjL8RHKCQlX9p6j9vMvD-TEgqfdyYNeKTHVgs9C_7rVblDMuhjfZf3gRmQnhNuX8A&X-OWA-CANARY=bdvoV20F57YAAAAAAAAAAMAI9RX3yNwYfcACiODr9TiUZjHaTnPEP_m_1dvZ64xXSL5uEZe4288.&owa=outlook.office.com&scriptVer=20240816003.15&clientId=7F90C63FA8F24489B8ECA1D98477B826&animation=true"
        if incident.type_requette.nom_requette == 'indisponibilite':       
            message = f"""
           <html>
                <body>
                    <!-- Image en haut -->
                    <div style="text-align: center;">
                        <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
                    </div>
                    <p style="color: blue;">Y’ello MTNers,</p>
                    <p style="color: blue;">L'indisponibilité survenue sur le service {services_impacte} depuis {date_incident} est résolue.</p>
                    <p style="color: blue;">Merci pour votre compréhension.</p>
                    <!-- Image en bas -->
                    <div style="text-align: center;">
                        <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
                    </div>
                </body>
            </html>
            """
        elif incident.type_requette.nom_requette == 'instabilite':
            message = f"""
            <html>
                <body>
                    <!-- Image en haut -->
                    <div style="text-align: center;">
                        <img src="{image_url}" alt="Image en haut" style="width: 100%; height: auto;">
                    </div>
                    <p style="color: blue;">Y’ello MTNers,</p>
                    <p style="color: blue;">La perturbation survenue sur le service {services_impacte} depuis {date_incident} est résolue.</p>
                    <p style="color: blue;">Merci pour votre compréhension.</p>
                    <p style="color: blue;">IT-MFS</p>
                    <!-- Image en bas -->
                    <div style="text-align: center;">
                        <img src="{image_url}" alt="Image en bas" style="width: 100%; height: auto;">
                    </div>
                </body>
            </html>
            """
    
        # Envoi de l'email avec rendu HTML
        if emails and message:
            try:
                email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, emails)
                email.attach_alternative(message, "text/html")
                email.send()
            except Exception as e:
                logger.error(f'Error sending email: {e}')
        
        
        
        
    return redirect('listeincident')



@login_required
def action_statut_change(request, changement_id):
    changement = get_object_or_404(Changement, id=changement_id)
    
    if request.method == 'POST':
        # Mettre à jour l'état du changement
        changement.en_cours = False
        changement.statut = 'C'
        changement.save()
        
        emails, _ = construire_email_changement(changement)

        # Définition des variables
        nom_plateforme = changement.nom_plateforme
        date_changement = changement.date_changement.strftime("%d/%m/%Y")
        fin_changement = changement.fin_changement.strftime("%d/%m/%Y")
        heure_debut = changement.heure_debut.strftime("%H:%M")
        heure_fin = changement.heure_fin.strftime("%H:%M")

        subject = 'Notification de mise à jour de changement'
        signature = "La DSI" if changement.Type_requette_changement.nom_requette_changement == 'Upgrade BD NA' else "IT-MFS"
        message = f"Yello MTNers, veuillez noter que le changement planifié sur la plateforme {nom_plateforme} du {date_changement} au {fin_changement}, de {heure_debut} à {heure_fin}, est terminé. Merci pour votre compréhension. {signature}"

        if emails:
            send_email_u(subject, message, emails)
        else:
            messages.error(request, "Aucun destinataire d'email n'est défini.")
    
    return redirect('listechangement')

    