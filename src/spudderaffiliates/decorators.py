from django.shortcuts import redirect


def affiliate_login_required(function):
    def wrap(request, *args, **kwargs):

        if not request.session.get('affiliate', False):
            return redirect('/spudderaffiliates')
        return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
    return wrap