from google.appengine.api import mail
from django.shortcuts import render
from spudmart.utils.queues import trigger_backend_task
import simplejson
from django.http import HttpResponseRedirect, HttpResponse
from google.appengine.api import urlfetch
from spudmart.hospitals.models import Hospital
import logging
from django.contrib.auth.decorators import login_required
from xml.dom import minidom
from django.template.loader import render_to_string

@login_required
def trigger_convert(request):
    trigger_backend_task('/hospitals/convert_xml_hospital_list_async', target='payments')
    return HttpResponseRedirect('/')

def convert_json_hospital_list_async(request):
    url = "http://data.medicare.gov/resource/v287-28n3.json"
    result = urlfetch.fetch(url)
    Hospital.objects.all().delete()
    if result.status_code == 200:
        items = simplejson.loads(result.content, 'utf-8')
        for item in items:
            hospital = Hospital()
            hospital.name = item['hospital_name']
            hospital.address1 = item['address_1']
            hospital.address2 = item['address_2'] if 'address_2' in item else ''
            hospital.city = item['city']
            hospital.state = item['state']
            hospital.zip = item['zip_code']
            hospital.county_name = item['county_name'] if 'county_name' in item else ''
            hospital.phone = item['phone_number']['phone_number']
            hospital.longitude = float(item['location']['longitude'])
            hospital.latitude = float(item['location']['latitude'])
            hospital.save()
    return HttpResponse('OK')

def convert_xml_hospital_list_async(request):
    doc = minidom.parseString(render_to_string('hospitals/rows.xml'))
    Hospital.objects.all().delete()
    for row in doc.getElementsByTagName('row'):
        try:
            children = row.childNodes
            hospital = Hospital()
            hospital.name = _get_child(children, 'hospital_name')
            hospital.address1 = _get_child(children, 'address_1')
            hospital.city = _get_child(children, 'city')
            hospital.state = _get_child(children, 'state')
            hospital.zip = _get_child(children, 'zip_code')
            hospital.county_name = _get_child(children, 'county_name')
            hospital.phone = _get_child(children, 'phone_number', 'phone_number')
            hospital.longitude = _get_child(children, 'location', 'longitude')
            hospital.latitude = _get_child(children, 'location', 'latitude')
            hospital.save()
        except Exception, e:
            logging.info(e)
    return HttpResponse('OK')

def _get_child(children, name, attr = None):
    for child in children:
        if child.nodeName == name:
            return child.childNodes[0].nodeValue if not attr else child.getAttribute(attr)
    return ''

@login_required
def get_hospitals_within_bounds(request):
    latitude_range = [float(value) for value in request.GET.getlist('latitude_range[]')]
    longitude_range = [float(value) for value in request.GET.getlist('longitude_range[]')]
    
    if longitude_range[0] < 0 and longitude_range[1] < 0:
        longitude_range.reverse()
    
    hospitals_in_latitude_range = Hospital.objects.filter(latitude__range = latitude_range)
    hospitals_in_longitude_range = Hospital.objects.filter(longitude__range = longitude_range)
    
    hospitals = []
    for hospital in hospitals_in_latitude_range:
        if hospital in hospitals_in_longitude_range:
            hospitals.append({
                'id' : hospital.id,
                'name' : hospital.name,
                'address' : hospital.address1,
                'latitude' : hospital.latitude,
                'longitude' : hospital.longitude,
                'state' : hospital.state,
                'city' : hospital.city,
                'zip' : hospital.zip
            })
    
    hospitals_dict = {
        'hospitals' : hospitals
    }
    
    return HttpResponse(simplejson.dumps(hospitals_dict))