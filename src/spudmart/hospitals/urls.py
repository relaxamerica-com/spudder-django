from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.hospitals.views',
    (r'^trigger_convert$', 'trigger_convert'),
    (r'^convert_json_hospital_list_async$', 'convert_json_hospital_list_async'),
    (r'^convert_xml_hospital_list_async$', 'convert_xml_hospital_list_async'),
    (r'^get_hospitals_within_bounds$', 'get_hospitals_within_bounds'),
)