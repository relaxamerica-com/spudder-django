import logging
from django.core import mail
from django.conf import settings
from spudderdomain.models import FanPage
from spudderaccounts.wrappers import RoleFan
from spudderdomain.controllers import SpudsController
from spuddersocialengine.atpostspud.models import AtPostSpudTwitterAuthentication, AtPostSpudTwitterCounter
from spuddersocialengine.atpostspud.models import AtPostSpudServiceConfiguration
from spuddersocialengine.atpostspud.utils import parse_spud_for_fan, parse_spud_for_unknown_fan


def get_latest_at_post_spuds(dev=False):
    service_config = AtPostSpudServiceConfiguration.GetForSite()
    twitter_auth = AtPostSpudTwitterAuthentication.GetForSite()
    if (service_config.active and twitter_auth.authorized()) or dev:
        # The service is running and twitter is authenticated
        api = twitter_auth.api()
        since_id = AtPostSpudTwitterCounter.GetLastProcessedId()
        statuses = api.mentions_timeline(since_id=since_id)
        for s in statuses:
            AtPostSpudTwitterCounter.SetLastProcessedId(s.id)
            twitter_user_id = s.user.screen_name
            media = s.entities.get('media', None)
            if not media:
                continue
            photo = None
            for m in media:
                if m.get('type', None) == 'photo':
                    photo = m
            if not photo:
                logging.debug(
                    "atpostspud/api/get_latest_at_post_spuds: sending message "
                    "to %s - text only spud" % twitter_user_id)
                status_message = "@%s We got your SPUD. At the moment we can only " \
                                 "take SPUDs with images, sorry! %s" % (twitter_user_id, s.id)
                api.update_status(status_message, s.id)
                continue
            fans = FanPage.objects.filter(twitter=twitter_user_id)
            if not fans.count():
                fans = FanPage.objects.filter(twitter="@%s" % twitter_user_id)
            if fans.count():
                logging.debug(
                    "atpostspud/api/get_latest_at_post_spuds: creating spud "
                    "for %s" % twitter_user_id)
                fan = fans[0]
                spud = parse_spud_for_fan(s, fan)
                SpudsController(RoleFan(fan)).add_spud_from_fan(spud)
            else:
                logging.debug(
                    "atpostspud/api/get_latest_at_post_spuds: sending message to "
                    "%s - no matching account" % twitter_user_id)
                spud = parse_spud_for_unknown_fan(s)
                spud_id = spud.id
                url = "%s/s/%s" % (settings.SPUDMART_BASE_URL, spud_id)
                status_message = "@%s We got your SPUD go here %s to claim it!" % (twitter_user_id, url)
                api.update_status(status_message, s.id)
    elif service_config.active:
        # Here the service is active twitter is not authenticated
        logging.error(
            "atpostspud/api/get_latest_at_post_spuds: Twitter auth failed, the service will be shut down "
            "and a support email sent.")
        service_config.deactivate()
        message = "The twitter authentication in the @postspudservice for %s is out of " \
            "date and the service is not running" % settings.SPUDMART_BASE_URL
        mail.send_mail(
            "@postspud service error - Twitter authentication",
            message,
            settings.SUPPORT_EMAIL,
            [settings.SUPPORT_EMAIL])
    else:
        # Here the service is not active, assume an email has been sent and quit
        logging.warning("atpostspud/api/get_latest_at_post_spuds: The service is not active.")
        pass
