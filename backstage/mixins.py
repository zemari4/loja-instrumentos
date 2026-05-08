from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import AccessMixin


class BackstagePermissionMixin(AccessMixin):
    login_url = "/usuario/entrar"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect_to_login(
                request.get_full_path(), self.login_url, self.redirect_field_name
            )
        return super().dispatch(request, *args, **kwargs)
