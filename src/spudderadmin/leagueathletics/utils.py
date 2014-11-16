import httplib
import json
import urllib
import logging
from django.core.exceptions import MultipleObjectsReturned
from spudderdomain.models import Club


def fetch_programs_for_zip(zip_code):
    try:
        params = urllib.urlencode({
            'zip': zip_code
        })
        url = '/API/Registrations/NearMe/?%s' % params
        connection = httplib.HTTPSConnection('api.leagueathletics.com')
        connection.connect()
        connection.request('POST', url)
        resp = connection.getresponse()
        resp_data = resp.read()
        json_data = json.loads(resp_data)

        if 'error' in json_data:
            return None

        return json_data['Programs']
    except httplib.HTTPException:
        logging.info('HTTP connection exception')
        return None
    except KeyError:
        logging.info('Key error')
        return None
    except Exception as e:
        logging.info('Exception')
        logging.info(e)
        return None


def save_club_from_program_json_data(json_data):
    try:
        Club.objects.get(original_domain_name='leagueathletics', original_domain_id=json_data['id'])
    except Club.DoesNotExist:
        name = json_data['orgName']
        if not name:
            return False

        Club(
            name=name,
            website = json_data['url'],
            address=json_data['location'] + ', ' + json_data['zip'],
            original_domain_name='leagueathletics',
            original_domain_id=json_data['id']
        ).save()
        return True
    except MultipleObjectsReturned:
        # There are situations, where API returns multiple programs for same organisation (with same ID)
        # An example is zip code 01450 - it returns two programs for "LS Baseball" organisation (with ID = 1398).
        # In our case we just need to remove the duplicates
        # Locally it can occur because of eventual consistency in HRD (write occurs to close to next read)

        logging.info('#'*60)
        logging.info('Removing duplicates for "%s" (ID: %s, zip: %s)' % (json_data['orgName'], json_data['id'], json_data['zip']))
        logging.info('#'*60)

        clubs = list(Club.objects.filter(original_domain_name='leagueathletics', original_domain_id=json_data['id']))
        for club in clubs[1:]:
            club.delete()
    except KeyError, e:
        logging.info('Key error for "%s" (ID: %s, zip: %s)' % (json_data['orgName'], json_data['id'], json_data['zip']))
        logging.info(e)

    return False