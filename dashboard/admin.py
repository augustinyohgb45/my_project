from django.contrib import admin
from .models import Incident, Destinataire, Service, Changement, Type_requette, Type_requette_changemen, JournalAudit


@admin.register(Service)
class AdminService(admin.ModelAdmin):
    list_display = ['nom']


@admin.register(Incident)
class AdminIncident(admin.ModelAdmin):
    list_display = [
        'numero_ticket', 'services_impacte', 'type_requette', 'date_enregistrement',
        'description', 'destinataire_nouveau', 'statut',
    ]
    list_filter = ['statut', 'type_requette']


@admin.register(Destinataire)
class AdminDestinataire(admin.ModelAdmin):
    list_display = ['nom', 'email', 'contact']


@admin.register(Changement)
class AdminChangement(admin.ModelAdmin):
    list_display = [
        'Numero_ticket', 'services_impacte', 'Type_requette_changement', 'date_changement',
        'fin_changement', 'heure_debut', 'heure_fin', 'date_envoie', 'email_envoye', 'statut',
    ]
    list_filter = ['statut', 'email_envoye', 'Type_requette_changement']


@admin.register(Type_requette)
class AdminTypeRequete(admin.ModelAdmin):
    list_display = ['nom_requette']
    filter_horizontal = ['destinataires']


@admin.register(Type_requette_changemen)
class AdminTypeRequeteChangement(admin.ModelAdmin):
    list_display = ['nom_requette_changement']
    filter_horizontal = ['destinataires']


@admin.register(JournalAudit)
class AdminJournalAudit(admin.ModelAdmin):
    """Consultation seule : le journal ne doit pas pouvoir être modifié."""
    list_display = ['date', 'nom_utilisateur', 'action', 'type_objet', 'objet', 'adresse_ip']
    list_filter = ['action', 'type_objet', 'date']
    search_fields = ['nom_utilisateur', 'objet', 'details']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
