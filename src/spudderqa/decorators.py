from django.http import Http404
from settings import Environments
from django.conf import settings
from django.shortcuts import redirect
from spudderadmin.utils import encoded_admin_session_variable_name


def qa_login_required(function):
    def wrap(request, *args, **kwargs):

        # if settings.ENVIRONMENT == Environments.LIVE:
        #     raise Http404

        if not request.session.get(encoded_admin_session_variable_name(), False):
            return redirect('/qa/signin')
        return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
    return wrap