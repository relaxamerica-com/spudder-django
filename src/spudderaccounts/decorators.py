import urlparse
from django.conf import settings
from django.utils.decorators import available_attrs
from django.utils.functional import wraps


def role_required(roles_list=[], redirect_field_name='next', redirect_url=None):
    """
    Decorator for views that checks that the user is logged in
    and current role is in roles_list, redirecting
    to the log-in page if necessary.
    """

    def _role_required(request, roles):
        return request.user.is_authenticated() and request.current_role and request.current_role.entity_type in roles

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):

            if _role_required(request, roles_list):
                return view_func(request, *args, **kwargs)

            path = request.build_absolute_uri()
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse.urlparse(redirect_url or settings.LOGIN_URL)[:2]
            current_scheme, current_netloc = urlparse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()

            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(path, redirect_url, redirect_field_name)
        return _wrapped_view
    return decorator
