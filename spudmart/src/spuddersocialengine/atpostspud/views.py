import json
from django.http import HttpResponse
from google.appengine.api.taskqueue import taskqueue
from spuddersocialengine.atpostspud.api import get_latest_at_post_spuds


def tick(request):
    queue = taskqueue.Queue('atpostspud-getspuds')
    task = taskqueue.Task(url='/socialengine/postspud/get_latest_at_post_spuds', method='GET')
    queue.add(task)
    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
        
        
def get_latest_at_post_spuds_view(request):
    dev = request.GET.get('dev', None)
    if dev:
        get_latest_at_post_spuds(dev)
    else:
        get_latest_at_post_spuds()
        queue = taskqueue.Queue('atpostspud-getspuds')
        queue.purge()
        return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')


