from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def superadmin_requis(vue):
    """Réserve la vue aux administrateurs connectés (403 pour les autres)."""
    @login_required
    @wraps(vue)
    def vue_protegee(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return vue(request, *args, **kwargs)
    return vue_protegee
