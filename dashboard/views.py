import csv
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from auth_app.decorators import superadmin_requis

from .form import IncidentForm, ChangementForm
from .models import Incident, Changement, JournalAudit
from .utils import (
    envoyer_email_changement, envoyer_email_cloture_changement, envoyer_email_incident,
)

logger = logging.getLogger(__name__)

NOMS_MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def _douze_derniers_mois():
    """Premiers jours des 12 derniers mois, du plus ancien au mois en cours."""
    mois = timezone.localdate().replace(day=1)
    resultat = []
    for _ in range(12):
        resultat.append(mois)
        mois = (mois - timedelta(days=1)).replace(day=1)
    return list(reversed(resultat))


def _nombre_par_mois(queryset, mois):
    """Nombre d'enregistrements par mois, pour chacun des mois donnés."""
    lignes = (
        queryset.filter(date_enregistrement__date__gte=mois[0])
        .annotate(mois=TruncMonth('date_enregistrement'))
        .values('mois')
        .annotate(total=Count('id'))
    )
    comptes = {timezone.localtime(ligne['mois']).date(): ligne['total'] for ligne in lignes}
    return [comptes.get(m, 0) for m in mois]


@login_required
def acceuil(request):
    mois = _douze_derniers_mois()
    context = {
        'nb_incidents_clotures': Incident.objects.filter(statut='C').count(),
        'nb_changements_clotures': Changement.objects.filter(statut='C').count(),
        'nb_incident_en_cours': Incident.objects.filter(statut='E').count(),
        'nb_changement_en_cours': Changement.objects.filter(statut='E').count(),
        'graphique': {
            'mois': [f"{NOMS_MOIS[m.month - 1]} {m.year}" for m in mois],
            'incidents': _nombre_par_mois(Incident.objects.all(), mois),
            'changements': _nombre_par_mois(Changement.objects.all(), mois),
        },
        'derniers_incidents': Incident.objects.select_related('services_impacte', 'type_requette').order_by('-date_enregistrement')[:5],
        'derniers_changements': Changement.objects.select_related('services_impacte', 'Type_requette_changement').order_by('-date_enregistrement')[:5],
    }
    if request.user.is_superuser:
        context['dernieres_activites'] = JournalAudit.objects.select_related('utilisateur')[:8]
    return render(request, 'dashboard/index.html', context)


@login_required
def incident(request):
    if request.method == "POST":
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.user = request.user
            incident.save()

            if envoyer_email_incident(incident):
                messages.success(request, "L'incident a été enregistré et notifié.")
            else:
                messages.warning(request, "L'incident a été enregistré, mais aucun e-mail n'a été envoyé.")
            return redirect("acceuil")
    else:
        form = IncidentForm()

    return render(request, 'dashboard/incident.html', {'form': form})


@login_required
def changement(request):
    if request.method == "POST":
        form = ChangementForm(request.POST)
        if form.is_valid():
            changement = form.save(commit=False)
            changement.user = request.user
            changement.save()

            # Envoyer maintenant si la date d'envoi est atteinte, sinon laisser
            # la commande envoyer_emails_planifies s'en charger
            if changement.date_envoie <= timezone.now():
                if envoyer_email_changement(changement):
                    messages.success(request, "Le changement a été enregistré et l'email a été envoyé.")
                else:
                    messages.error(request, "Le changement a été enregistré, mais l'envoi de l'email a échoué.")
            else:
                date_envoi = timezone.localtime(changement.date_envoie).strftime("%d/%m/%Y à %H:%M")
                messages.success(request, f"Le changement a été enregistré. L'email sera envoyé le {date_envoi}.")
            return redirect("acceuil")
    else:
        form = ChangementForm()

    return render(request, 'dashboard/changement.html', {'form': form})


@login_required
def listeincident(request):
    incidents = Incident.objects.select_related('user', 'services_impacte', 'type_requette').order_by('-date_enregistrement')
    return render(request, 'dashboard/listeincident.html', {'incidents': incidents})


@login_required
def listechangement(request):
    changements = (
        Changement.objects.select_related('user', 'services_impacte', 'Type_requette_changement')
        .prefetch_related('Type_requette_changement__destinataires')
        .order_by('-date_enregistrement')
    )
    return render(request, 'dashboard/listechangement.html', {'changements': changements})


@login_required
@require_POST
def action_statut(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    incident.statut = 'C'
    incident.save()

    if envoyer_email_incident(incident, resolu=True):
        messages.success(request, "L'incident a été clôturé et la résolution notifiée.")
    else:
        messages.warning(request, "L'incident a été clôturé, mais aucun e-mail n'a été envoyé.")
    return redirect('listeincident')


@login_required
@require_POST
def action_statut_change(request, changement_id):
    changement = get_object_or_404(Changement, id=changement_id)
    changement.statut = 'C'
    changement.save()

    if envoyer_email_cloture_changement(changement):
        messages.success(request, "Le changement a été clôturé et la fin notifiée.")
    else:
        messages.warning(request, "Le changement a été clôturé, mais aucun e-mail n'a été envoyé.")
    return redirect('listechangement')


PERIODES_AUDIT = {
    'jour': ("Aujourd'hui", 0),
    '7j': ("7 derniers jours", 7),
    '30j': ("30 derniers jours", 30),
    'tout': ("Tout l'historique", None),
}


def _journal_filtre(request):
    """Entrées du journal correspondant aux filtres de la requête, et les filtres appliqués."""
    filtres = {
        'periode': request.GET.get('periode') if request.GET.get('periode') in PERIODES_AUDIT else '7j',
        'utilisateur': request.GET.get('utilisateur', ''),
        'action': request.GET.get('action', ''),
        'type_objet': request.GET.get('type_objet', ''),
        'q': request.GET.get('q', '').strip(),
    }
    journal = JournalAudit.objects.select_related('utilisateur')

    jours = PERIODES_AUDIT[filtres['periode']][1]
    if jours is not None:
        debut = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=jours)
        journal = journal.filter(date__gte=debut)
    if filtres['utilisateur'] == 'systeme':
        journal = journal.filter(nom_utilisateur='')
    elif filtres['utilisateur']:
        journal = journal.filter(nom_utilisateur=filtres['utilisateur'])
    if filtres['action']:
        journal = journal.filter(action=filtres['action'])
    if filtres['type_objet']:
        journal = journal.filter(type_objet=filtres['type_objet'])
    if filtres['q']:
        journal = journal.filter(
            Q(objet__icontains=filtres['q']) | Q(details__icontains=filtres['q']) | Q(nom_utilisateur__icontains=filtres['q'])
        )
    return journal, filtres


def _export_csv(journal):
    reponse = HttpResponse(content_type='text/csv; charset=utf-8')
    reponse['Content-Disposition'] = f'attachment; filename="audit-it-mfs-{timezone.localdate():%Y-%m-%d}.csv"'
    reponse.write('\ufeff')  # BOM : accents corrects à l'ouverture dans Excel
    ecrivain = csv.writer(reponse, delimiter=';')
    ecrivain.writerow(['Date', 'Utilisateur', 'Action', 'Élément', 'Objet', 'Détails', 'Adresse IP'])
    for entree in journal.iterator():
        ecrivain.writerow([
            timezone.localtime(entree.date).strftime('%d/%m/%Y %H:%M:%S'),
            entree.nom_utilisateur or 'Système',
            entree.get_action_display(),
            entree.type_objet,
            entree.objet,
            entree.details.replace('\n', ' | '),
            entree.adresse_ip or '',
        ])
    return reponse


@superadmin_requis
def audit(request):
    journal, filtres = _journal_filtre(request)
    if request.GET.get('export') == 'csv':
        return _export_csv(journal)

    page = Paginator(journal, 25).get_page(request.GET.get('page'))
    debut_jour = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    aujourdhui = JournalAudit.objects.filter(date__gte=debut_jour)
    parametres = request.GET.copy()
    parametres.pop('page', None)

    return render(request, 'dashboard/audit.html', {
        'page_journal': page,
        'filtres': filtres,
        'parametres': parametres.urlencode(),
        'periodes': [(cle, libelle) for cle, (libelle, _) in PERIODES_AUDIT.items()],
        'actions': JournalAudit.ACTIONS,
        'types_objet': JournalAudit.objects.exclude(type_objet='').values_list('type_objet', flat=True).distinct().order_by('type_objet'),
        'utilisateurs': User.objects.order_by('username').values_list('username', flat=True),
        'nb_connexions_jour': aujourdhui.filter(action=JournalAudit.CONNEXION).count(),
        'nb_connectes_jour': aujourdhui.filter(action=JournalAudit.CONNEXION).values('nom_utilisateur').distinct().count(),
        'nb_actions_jour': aujourdhui.exclude(action__in=[JournalAudit.CONNEXION, JournalAudit.DECONNEXION, JournalAudit.ECHEC_CONNEXION]).count(),
        'nb_echecs_7j': JournalAudit.objects.filter(action=JournalAudit.ECHEC_CONNEXION, date__gte=debut_jour - timedelta(days=7)).count(),
    })
