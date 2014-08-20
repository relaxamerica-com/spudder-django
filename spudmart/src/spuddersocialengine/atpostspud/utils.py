import json
from spuddersocialengine.models import SpudFromSocialMedia


def parse_spud_for_fan(status, fan):
    media = [m for m in status.entities['media'] if m.get('type', None) == 'photo'][0]
    spud = SpudFromSocialMedia(
        entity_type="FAN",
        entity_id=fan.id,
        originating_service='TWITTER',
        unique_id_from_source=status.id_str,
        state=SpudFromSocialMedia.STATE_ACCEPTED,
        type=SpudFromSocialMedia.TYPE_IMAGE,
        data=json.dumps({
            'service': 'TWITTER',
            'user': {
                'username': status.user.screen_name,
                'id': status.id_str,
                'profile_picture': status.user.profile_image_url_https
            },
            'text': [status.text],
            'image': {
                'standard_resolution': {
                    'url': media.get('media_url_https', ''),
                    'width': media.get('sizes', {}).get('large', {}).get('w', 0),
                    'height': media.get('sizes', {}).get('large', {}).get('h', 0),
                }
            }
        }))
    return spud


def parse_spud_for_unknown_fan(status):
    media = [m for m in status.entities['media'] if m.get('type', None) == 'photo'][0]
    spud = SpudFromSocialMedia(
        entity_type="FAN",
        originating_service='TWITTER',
        unique_id_from_source=status.id_str,
        state=SpudFromSocialMedia.STATE_ACCEPTED,
        type=SpudFromSocialMedia.TYPE_IMAGE,
        data=json.dumps({
            'service': 'TWITTER',
            'user': {
                'username': status.user.screen_name,
                'id': status.id_str,
                'profile_picture': status.user.profile_image_url_https
            },
            'text': [status.text],
            'image': {
                'standard_resolution': {
                    'url': media.get('media_url_https', ''),
                    'width': media.get('sizes', {}).get('large', {}).get('w', 0),
                    'height': media.get('sizes', {}).get('large', {}).get('h', 0),
                }
            }
        }))
    spud.save()
    return spud