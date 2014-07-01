from django.contrib.auth.models import User
from django.db import models
from spudmart.upload.models import UploadedFile
from djangotoolbox.fields import ListField
from spudmart.CERN.rep import deleted_venue

SPORTS = ['Baseball', 'Basketball', 'Field Hockey', 'Football',
          'Ice Hockey', 'Lacrosse', 'Rugby', 'Soccer', 'Softball',
          'Swimming', 'Tennis', 'Track and Field', 'Volleyball',
          'Waterpolo', 'Wrestling']


class Venue(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, related_name="owner_user")
    renter = models.ForeignKey(User, null=True, related_name="renter_user")
    name = models.CharField(max_length=200, default="Sponsor's Name for Venue")
    aka_name = models.CharField(max_length=200, default="Common Venue Name")
    sport = models.CharField(max_length=100)
    logo = models.ForeignKey(UploadedFile, null=True)
    speciality = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    coordinates = models.CharField(max_length=100)
    latitude = models.DecimalField(null=True, decimal_places=6, max_digits=9)
    longitude = models.DecimalField(null=True, decimal_places=6, max_digits=9)
    parking_details = models.CharField(max_length=200)
    parking_tips = models.CharField(max_length=200)
    video = models.CharField(max_length=300)
    venue_pics = ListField()
    restroom_pics = ListField()
    playing_surface_pics = ListField()
    playing_surface_details = models.CharField(max_length=200)
    restroom_details = models.CharField(max_length=200)
    concession_details = models.CharField(max_length=200)
    admission_details = models.CharField(max_length=200)
    shelter_details = models.CharField(max_length=200)
    medical_address = models.CharField(max_length=200)
    handicap_details = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    website = models.CharField(max_length=200)
    price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    fax = models.CharField(max_length=200)

    # Just to stay consistent with fcns created in spuddercern.rep
    rep = models.IntegerField(default=0)
    

    def __eq__(self, other):
        return self.pk == other.pk

    def is_available(self):
        if self.price <= 0.0:
            return False

        if PendingVenueRental.objects.filter(venue=self).count() > 0:
            return False

        return self.renter is None

    def is_renter(self, user):
        if self.renter is None:
            return False

        return self.renter.id == user.id

    def is_groundskeeper(self, user):
        return self.user.id == user.id

    def delete(self, using=None):
        """
        Deleting a venue punishes the owner for deleting it.

        This removes all of the points that the user has owned for the
            venue, before deleting the venue.
        """
        deleted_venue(self)
        super(Venue, self).delete(using)


class PendingVenueRental(models.Model):
    venue = models.ForeignKey(Venue)