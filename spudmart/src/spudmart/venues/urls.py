from django.conf.urls.defaults import patterns


urlpatterns = patterns('spudmart.venues.views',
    (r'^$', 'index'),
    (r'^login$', 'login_view'),
    (r'^view/(?P<venue_id>\d+)$', 'view'),
    (r'^save_coordinates/(?P<venue_id>\d+)$', 'save_coordinates'),
    (r'^save_parking_details/(?P<venue_id>\d+)$', 'save_parking_details'),
    (r'^save_venue_pics/(?P<venue_id>\d+)$', 'save_venue_pics'),
    (r'^save_logo_and_name/(?P<venue_id>\d+)$', 'save_logo_and_name'),
    (r'^save_playing_surface_pics/(?P<venue_id>\d+)$', 'save_playing_surface_pics'),
    (r'^save_video/(?P<venue_id>\d+)$', 'save_video'),
    (r'^save_restroom_details/(?P<venue_id>\d+)$', 'save_restroom_details'),
    (r'^save_concession_details/(?P<venue_id>\d+)$', 'save_concession_details'),
    (r'^save_admission_details/(?P<venue_id>\d+)$', 'save_admission_details'),
    (r'^save_shelter_details/(?P<venue_id>\d+)$', 'save_shelter_details'),
    (r'^save_medical_details/(?P<venue_id>\d+)$', 'save_medical_details'),
    (r'^save_handicap_details/(?P<venue_id>\d+)$', 'save_handicap_details'),
    (r'^send_message/(?P<venue_id>\d+)$', 'send_message'),
    (r'^recipient/(?P<venue_id>\d+)$', 'recipient'),
    (r'^recipient/(?P<venue_id>\d+)/complete$', 'complete'),
    (r'^recipient/(?P<venue_id>\d+)/thanks$', 'thanks'),
    (r'^recipient/(?P<venue_id>\d+)/error$', 'error'),
    (r'^rent_venue/(?P<venue_id>\d+)/complete$', 'rent_complete'),
    (r'^rent_venue/(?P<venue_id>\d+)/thanks$', 'rent_thanks'),
    (r'^rent_venue/(?P<venue_id>\d+)/error$', 'rent_error'),
    (r'^remove_pic/(?P<venue_id>\d+)$', 'remove_pic'),
    (r'^save_price/(?P<venue_id>\d+)$', 'save_price'),
    (r'^get_venues_within_bounds$', 'get_venues_within_bounds'),
    (r'^fix_venue_coordinates$', 'fix_venue_coordinates'),
    (r'^create$', 'create'),
    (r'^list', 'list_view'),
)