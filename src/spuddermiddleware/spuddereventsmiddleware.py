

class EventsMiddleware(object):
    EVENTS_KEY_NAME = 'events'

    @classmethod
    def add_events_to_session(cls, request):
        if cls.EVENTS_KEY_NAME not in request.session:
            request.session[cls.EVENTS_KEY_NAME] = []

    def process_request(self, request):
        EventsMiddleware.add_events_to_session(request)
