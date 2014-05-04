from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.venues.views',
    (r'^$', 'index'),
    (r'^view/(?P<venue_id>\d+)$', 'view'),
    (r'^save_coordinates/(?P<venue_id>\d+)$', 'save_coordinates'),
    (r'^save_parking_details/(?P<venue_id>\d+)$', 'save_parking_details'),
    (r'^save_venue_pics/(?P<venue_id>\d+)$', 'save_venue_pics'),
    (r'^save_logo_and_name/(?P<venue_id>\d+)$', 'save_logo_and_name'),
    (r'^save_playing_surface_pics/(?P<venue_id>\d+)$', 'save_playing_surface_pics'),
    (r'^save_video_url/(?P<venue_id>\d+)$', 'save_video_url'),
    (r'^save_restroom_details/(?P<venue_id>\d+)$', 'save_restroom_details'),
    (r'^save_concession_details/(?P<venue_id>\d+)$', 'save_concession_details'),
    (r'^save_admission_details/(?P<venue_id>\d+)$', 'save_admission_details'),
    (r'^save_shelter_details/(?P<venue_id>\d+)$', 'save_shelter_details'),
    (r'^save_medical_details/(?P<venue_id>\d+)$', 'save_medical_details'),
    (r'^save_handicap_details/(?P<venue_id>\d+)$', 'save_handicap_details'),
    (r'^create$', 'create'),
    (r'^list', 'list_view'),
    (r'^login$', 'login_view'),
    (r'^register$', 'register'),
)