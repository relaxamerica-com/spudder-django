

class EventsMiddleware:
    EVENTS_ATTR_NAME = 'events'

    def _add_events_to_request(self, request):
        if not hasattr(request, self.EVENTS_ATTR_NAME):
            setattr(request, self.EVENTS_ATTR_NAME, [])

    def process_request(self, request):
        self._add_events_to_request(request)
