from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from spudmart.sponsors.models import SponsorPage
from spudmart.upload.models import UploadedFile
from djangotoolbox.fields import ListField
from spudmart.CERN.rep import deleted_venue
from spudmart.CERN.models import Student, STATES

SPORTS = settings.SPORTS


class Venue(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, related_name="owner_user", null=True)
    student = models.ForeignKey(Student, null=True)
    renter = models.ForeignKey(SponsorPage, null=True)
    name = models.CharField(max_length=200, default="venuetagname")
    aka_name = models.CharField(max_length=200, default="Venue yet to be Named")
    sport = models.CharField(max_length=100)
    logo = models.ForeignKey(UploadedFile, null=True, related_name="logo_file")
    speciality = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    coordinates = models.CharField(max_length=100)
    latitude = models.DecimalField(null=True, decimal_places=6, max_digits=9)
    longitude = models.DecimalField(null=True, decimal_places=6, max_digits=9)
    parking_details = models.CharField(max_length=200)
    parking_pics = ListField()
    # parking_tips = models.CharField(max_length=200)
    video = models.CharField(max_length=300)
    venue_pics = ListField()
    restroom_pics = ListField()
    playing_surface_pics = ListField()
    playing_surface_details = models.CharField(max_length=200)
    restroom_details = models.CharField(max_length=200)
    concession_pics = ListField()
    concession_details = models.CharField(max_length=200)
    admission_pics = ListField()
    admission_details = models.CharField(max_length=200)
    # shelter_details = models.CharField(max_length=200)
    medical_address = models.CharField(max_length=200)
    handicap_details = models.CharField(max_length=200)
    handicap_pics = ListField()
    phone = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    website = models.CharField(max_length=200)
    price = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    fax = models.CharField(max_length=200)
    cover_image = models.ForeignKey(UploadedFile, null=True, related_name="cover_image")
    state = models.CharField(max_length=2)
    location_has_been_changed = models.BooleanField(default=False)

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

    def is_renter(self, role):
        if role is None or self.renter is None:
            return False

        return self.renter.sponsor.id == role.user.id

    def is_groundskeeper(self, role):
        if not role or not self.student:
            return False

        return self.student.id == role.entity.id

    def delete(self, using=None):
        """
        Deleting a venue punishes the owner for deleting it.

        This removes all of the points that the user has owned for the
            venue, before deleting the venue.
        """
        deleted_venue(self)
        super(Venue, self).delete(using)

    def __unicode__(self):
        return unicode(self.aka_name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def verbose_state(self):
        return STATES[self.state]


class PendingVenueRental(models.Model):
    venue = models.ForeignKey(Venue)


class TempVenue(models.Model):
    """
    A temporary model of a venue, used to model some venue properties
    """
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, related_name="temp_venue_owner_user", null=True)
    student = models.ForeignKey(Student, null=True)
    name = models.CharField(max_length=200, default="venuetagname")
    aka_name = models.CharField(max_length=200, default="Venue yet to be Named")
    sport = models.CharField(max_length=100)
    logo = models.ForeignKey(UploadedFile, null=True, related_name="temp_venue_logo_file")
    latitude = models.DecimalField(null=True, decimal_places=6, max_digits=9)
    longitude = models.DecimalField(null=True, decimal_places=6, max_digits=9)
    parking_details = models.CharField(max_length=200)
    parking_pics = ListField()
    video = models.CharField(max_length=300)
    venue_pics = ListField()
    restroom_pics = ListField()
    playing_surface_pics = ListField()
    playing_surface_details = models.CharField(max_length=200)
    restroom_details = models.CharField(max_length=200)
    concession_pics = ListField()
    concession_details = models.CharField(max_length=200)
    admission_pics = ListField()
    admission_details = models.CharField(max_length=200)
    medical_address = models.CharField(max_length=200)
    handicap_details = models.CharField(max_length=200)
    handicap_pics = ListField()
    cover_image = models.ForeignKey(UploadedFile, null=True, related_name="temp_venue_cover_image")
    state = models.CharField(max_length=2)
    location_has_been_changed = models.BooleanField(default=False)
    rep = models.IntegerField(default=0)

    def translate_to_real_venue(self):
        venue = Venue(
            created_date=self.created_date,
            user=self.user,
            student=self.student,
            name=self.name,
            aka_name=self.aka_name,
            sport=self.sport,
            logo=self.logo,
            latitude=self.latitude,
            longitude=self.longitude,
            parking_details=self.parking_details,
            parking_pics=self.parking_pics,
            video=self.video,
            venue_pics=self.venue_pics,
            restroom_pics=self.restroom_pics,
            playing_surface_pics=self.playing_surface_pics,
            playing_surface_details=self.playing_surface_details,
            restroom_details=self.restroom_details,
            concession_pics=self.concession_pics,
            concession_details=self.concession_details,
            admission_pics=self.admission_pics,
            admission_details=self.admission_details,
            medical_address=self.medical_address,
            handicap_details=self.handicap_details,
            handicap_pics=self.handicap_pics,
            cover_image=self.cover_image,
            state=self.state,
            location_has_been_changed=self.location_has_been_changed,
            rep=self.rep)
        venue.save()
        self.delete()

        return venue