from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    
    
class SuperuserRedirectMixin(AccessMixin):
    """Asegura que el usuario sea un superusuario, de lo contrario redirige a la página de inicio."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            # Redirige al usuario a la URL que desees
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)