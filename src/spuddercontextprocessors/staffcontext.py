def staff_context(request):
    return {
        'is_staff_context': bool(request.session.get('staff', False))
    }
