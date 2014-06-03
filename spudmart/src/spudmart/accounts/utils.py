from spudmart.utils.cache import get_key
from spudmart.donations.models import Donation, DonationState, RentVenue
from django.core.cache import cache

CACHE_TIME = 24 * 60 * 60

def is_sponsor(user):
    cache_key = get_key(user, 'is_sponsor')
    is_sponsor = cache.get(cache_key)

    if is_sponsor is None:
        donations = Donation.objects.filter(
            donor=user,
            state=DonationState.FINISHED
        )
        rents = RentVenue.objects.filter(
            donor=user,
            state=DonationState.FINISHED
        )

        is_sponsor = len(donations) > 0 or len(rents) > 0
        cache.set(cache_key, is_sponsor, CACHE_TIME)
    
    return is_sponsor