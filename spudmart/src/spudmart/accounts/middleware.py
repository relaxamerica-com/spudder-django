from spudmart.donations.models import Donation, DonationState
from spudmart.utils.app_identity import get_application_version
from django.core.cache import cache
from spudmart.utils.cache import get_key

CACHE_TIME = 24 * 60 * 60


class SponsorMiddleware(object):
    @staticmethod
    def process_request(request):
        if not request.user.is_authenticated():
            return None

        cache_key = get_key(request.user, 'is_sponsor')
        is_sponsor = cache.get(cache_key)

        if is_sponsor is None:
            app_version = get_application_version()
            donations = Donation.objects.filter(
                donor=request.user,
                spudder_app=app_version,
                state=DonationState.FINISHED
            )

            is_sponsor = len(donations) > 0
            cache.set(cache_key, is_sponsor, CACHE_TIME)

        request.user.is_sponsor = is_sponsor

        return None