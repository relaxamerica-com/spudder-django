from spudmart.utils.cache import get_key
from spudmart.donations.models import Donation, DonationState, RentVenue
from django.core.cache import cache
from spudmart.CERN.models import Student
from django.core.exceptions import ObjectDoesNotExist

CACHE_TIME = 24 * 60 * 60


def is_sponsor(user):
    cache_key = get_key(user, 'is_sponsor')
    is_user_sponsor = cache.get(cache_key)

    if is_user_sponsor is None:
        donations_count = Donation.objects.filter(donor=user, state=DonationState.FINISHED).count()
        rents_count = RentVenue.objects.filter(donor=user, state=DonationState.FINISHED).count()

        is_user_sponsor = donations_count > 0 or rents_count > 0
        cache.set(cache_key, is_sponsor, CACHE_TIME)

    return is_user_sponsor


def is_student(user):
    try:
        Student.objects.get(user=user)
    except ObjectDoesNotExist:
        return False
    else:
        return True