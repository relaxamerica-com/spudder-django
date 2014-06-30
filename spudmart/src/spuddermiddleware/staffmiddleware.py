class StaffMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.session.get('staff', False):
            request.session['staff'] = bool(request.GET.get('staff', False) == "true")
