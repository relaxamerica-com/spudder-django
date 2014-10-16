import datetime
import json
from django.conf import settings

from django.contrib.auth.models import User
from django.db import models
from djangotoolbox.fields import ListField
from spudderaffiliates.models import Affiliate
from spudmart.recipients.models import AmazonRecipient
from spudmart.upload.models import UploadedFile
from spudmart.venues.models import Venue


class LinkedServiceTypeExistsForThisRole(Exception):
    pass


class LinkedService(models.Model):
    """
    Model that hold the configuration of any linked services such as Amazon, LinkedIn, Facebook etc

    *Should not be created directly, in stead, please use the Create class method provided
    """
    STATE_UNCONFIGURED = "unconfigured"
    STATE_CONFIGURED = "configured"

    LinkedServiceTypeExistsForThisRole = LinkedServiceTypeExistsForThisRole

    state = models.CharField(max_length=256, default=STATE_UNCONFIGURED)
    role_id = models.CharField(max_length=256)
    role_type = models.CharField(max_length=256)
    service_type = models.CharField(max_length=256)
    unique_service_id = models.CharField(max_length=1024)
    created = models.DateTimeField()
    _service_configuration = models.TextField()

    @classmethod
    def Create(cls, role, service_type, unique_service_id, configuration):
        """
        Creates a new LinkedService instance for the given role and service_type

        * Raises LinkedService.LinkedServiceTypeExistsForThisRole if this role is already linked to a service of this
        type

        :type service_type: enumerate spudderdomain.controllers.RoleController.ENTITY_TYPES
        :type unique_service_id: str
        :type configuration: dict
        :type role: spudderaccounts.wrappers.RoleBase
        :param cls: Class LinkedService
        :param role: Instance of the RoleBase wrapper
        :param service_type: Enum taken from LinkedServiceController.SERVICE_TYPES
        :param unique_service_id:
        :param configuration:
        :return: New instance of LinkedService
        """
        query = LinkedService.objects.filter(
            role_id=role.entity.id,
            role_type=role.entity_type,
            unique_service_id=unique_service_id,
            service_type=service_type)
        if query.count():
            raise LinkedServiceTypeExistsForThisRole
        service = LinkedService(
            role_id=role.entity.id,
            role_type=role.entity_type,
            service_type=service_type,
            unique_service_id=unique_service_id,
            created=datetime.datetime.now(),
            _service_configuration=json.dumps(configuration))
        service.save()
        return service

    @property
    def configuration(self):
        return json.loads(self._service_configuration or '{}')

    @configuration.setter
    def configuration(self, config_object):
        self._service_configuration = json.dumps(config_object or '{}')


class SpudType():
    TEXT = 1
    VIDEO = 2
    IMAGE = 3


class Comment(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User)  # what user should be used here?
    text = models.TextField()


class Spud(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    tags = ListField()
    type = models.IntegerField(choices = ((SpudType.TEXT, 'Text'),
                                          (SpudType.VIDEO, 'Video'),
                                          (SpudType.IMAGE, 'Image')), default = SpudType.TEXT)
    comments = ListField(Comment)
    content = models.TextField()
    image = models.ForeignKey(UploadedFile, null=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    author = models.ForeignKey(User)  # what user should be used here?

    def tags_to_string(self):
        return ' '.join(self.tags)
    
    
class FanPage(models.Model):
    fan = models.ForeignKey(User)
    username = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    avatar = models.ForeignKey(UploadedFile, blank=True, null=True, related_name='fanpage_avatar')
    cover_image = models.ForeignKey(UploadedFile, blank=True, null=True, related_name='fanpage_cover_image')
    free_text = models.CharField(max_length=1024, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    facebook = models.CharField(max_length=255, blank=True)
    twitter = models.CharField(max_length=255, blank=True)
    google_plus = models.CharField(max_length=255, blank=True)
    instagram = models.CharField(max_length=255, blank=True)
    linkedin = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=2, blank=True)

    info_messages_dismissed = models.TextField(blank=True, null=True)

    affiliate = models.ForeignKey(Affiliate, blank=True, null=True)

    def was_edited(self):
        return self.email is not None and self.email != ""

    def hidden_info_messages(self):
        return (self.info_messages_dismissed or '').split(',')

    def dismiss_info_message(self, message_id):
        self.info_messages_dismissed = "%s,%s" % (self.info_messages_dismissed or '', message_id)
        self.save()


class _TeamWithNameAlreadyExistsError(Exception):
    pass


def _update_location_from_post_data(location, post_data):
    """
        :param location: Location entity for update
        :param post_data: string containing comma separated data (lat;lng;info_window;address)
        :return: updated Location entity
    """

    location.post_data = post_data

    if post_data:
        lng, lat, info_window, address = post_data.split(';')

        location.latitude = float(lat)
        location.longitude = float(lng)
        location.info_window = info_window
        location.address = address

    location.save()

    return location


class Location(models.Model):
    latitude = models.FloatField(default=0, null=True, blank=True)
    longitude = models.FloatField(default=0, null=True, blank=True)
    post_data = models.CharField(max_length=255, default='', blank=True)
    info_window = models.CharField(max_length=255, default='', blank=True)
    address = models.CharField(max_length=255, default='', blank=True)

    @staticmethod
    def from_post_data(post_data):
        location = Location()
        location = _update_location_from_post_data(location, post_data)

        return location

    def update_from_post_data(self, post_data):
        _update_location_from_post_data(self, post_data)

    @property
    def external_link(self):
        start_index = self.info_window.index('href="') + 6
        end_index = self.info_window.index(' target') - 1

        return self.info_window[start_index:end_index]

    def __unicode__(self):
        return unicode(self.address)

    def __str__(self):
        return unicode(self).encode('utf-8')


class TeamPage(models.Model):
    name = models.CharField(max_length=255)
    at_name = models.CharField(max_length=255)
    location = models.ForeignKey(Location, null=True, blank=True)
    contact_details = models.CharField(max_length=255, blank=True)
    free_text = models.TextField(blank=True)
    sport = models.CharField(max_length=100)
    image = models.ForeignKey(UploadedFile, null=True, blank=True)
    cover_image = models.ForeignKey(UploadedFile, blank=True, null=True, related_name='team_page_cover_image')
    state = models.CharField(max_length=2)

    facebook = models.CharField(max_length=255, blank=True)
    twitter = models.CharField(max_length=255, blank=True)
    google_plus = models.CharField(max_length=255, blank=True)
    instagram = models.CharField(max_length=255, blank=True)
    linkedin = models.CharField(max_length=255, blank=True)

    affiliate = models.ForeignKey(Affiliate, blank=True, null=True)

    TeamWithNameAlreadyExistsError = _TeamWithNameAlreadyExistsError

    def update_location(self, location_info):
        if not location_info:
            self.location = None
            return

        if not self.location:
            self.location = Location.from_post_data(location_info)
        else:
            self.location.update_from_post_data(location_info)

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')


class TeamAdministrator(models.Model):
    entity_type = models.CharField(max_length=255)
    entity_id = models.CharField(max_length=255)
    team_page = models.ForeignKey(TeamPage, related_name='team_administrator_team_page')


class TeamVenueAssociation(models.Model):
    team_page = models.ForeignKey(TeamPage, related_name='team_venue_team_page')
    venue = models.ForeignKey(Venue, related_name='team_venue_venue')


class Club(models.Model):
    name = models.CharField(max_length=255)
    amazon_email = models.CharField(max_length=255, default='', blank=True)
    amazon_id = models.CharField(max_length=255, default='', blank=True)
    address = models.CharField(max_length=255, default='', blank=True)
    description = models.TextField(blank=True)
    thumbnail = models.ForeignKey(UploadedFile, blank=True, null=True, related_name='club_thumbnail')
    cover_image = models.ForeignKey(UploadedFile, blank=True, null=True, related_name='club_cover_image')
    location = models.ForeignKey(Location, null=True, blank=True, related_name='club_location')
    state = models.CharField(max_length=2)

    # Flags
    hidden = models.BooleanField(default=False)

    # Social media
    facebook = models.CharField(max_length=255, blank=True)
    twitter = models.CharField(max_length=255, blank=True)
    google_plus = models.CharField(max_length=255, blank=True)
    instagram = models.CharField(max_length=255, blank=True)
    linkedin = models.CharField(max_length=255, blank=True)

    affiliate = models.ForeignKey(Affiliate, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def update_location(self, location_info):
        if not location_info:
            self.location = None
            return

        if not self.location:
            self.location = Location.from_post_data(location_info)
        else:
            self.location.update_from_post_data(location_info)

    def has_stripe_recipient(self):
        return bool(StripeRecipient.objects.filter(club=self).count())

    def is_fully_activated(self):
        if not self.has_stripe_recipient():
            return False

        return StripeUser.objects.filter(club=self).count() > 0

    def next_activation_step(self):
        if self.is_fully_activated():
            return None

        if StripeRecipient.objects.filter(club=self).count() < 1:
            return 'recipient'

        return 'stripe'

    def is_hidden(self):
        return self.hidden


class TempClub(models.Model):
    """
    A simple model to hold basics about a club.
    """
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    email = models.CharField(max_length=255)
    affiliate = models.ForeignKey(Affiliate, blank=True, null=True)


class TeamClubAssociation(models.Model):
    team_page = models.ForeignKey(TeamPage, related_name='team_club_team_page')
    club = models.ForeignKey(Club, related_name='team_club_club')


class ClubRecipient(AmazonRecipient):
    registered_by = models.ForeignKey(User)
    club = models.ForeignKey(Club)


class StripeRecipient(models.Model):
    registered_by = models.ForeignKey(User)
    club = models.ForeignKey(Club)
    recipient_id = models.CharField(max_length=255)


class StripeUser(models.Model):
    club = models.ForeignKey(Club)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    publishable_key = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    scope = models.CharField(max_length=255)
    token_type = models.CharField(max_length=255)


class ClubAdministrator(models.Model):
    club = models.ForeignKey(Club, related_name='club_administrator_club')
    admin = models.ForeignKey(User, related_name='club_administrator_admin')

    def __unicode__(self):
        return unicode(self.club.name)

    def __str__(self):
        return unicode(self).encode('utf-8')


class ChallengeTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ForeignKey(UploadedFile, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    slug = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')


class Challenge(models.Model):
    template = models.ForeignKey(ChallengeTemplate, null=True, default=None)
    parent = models.ForeignKey('Challenge', null=True, default=None)
    name = models.CharField(max_length=255)
    description = models.TextField()
    creator_entity_id = models.CharField(max_length=255)
    creator_entity_type = models.CharField(max_length=255)
    recipient_entity_id = models.CharField(max_length=255, null=True, blank=True, default=None)
    recipient_entity_type = models.CharField(max_length=255, null=True, blank=True, default=None)
    proposed_donation_amount = models.FloatField(default=0.0)
    proposed_donation_amount_decline = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    image = models.ForeignKey(UploadedFile, null=True, default=None, related_name='challenge_image')
    youtube_video_id = models.CharField(max_length=255, default='', null=True, blank=True)
    creating_participant = models.ForeignKey(
        'ChallengeParticipation',
        null=True,
        default=None,
        related_name='creating_participant')

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_recipient(self):
        from spudderdomain.controllers import EntityController
        from spudderdomain.wrappers import EntityBase
        for entity_type in [EntityController.ENTITY_TEMP_CLUB, EntityController.ENTITY_CLUB]:
            if self.recipient_entity_type == entity_type:
                return EntityController.GetWrappedEntityByTypeAndId(
                    entity_type,
                    self.recipient_entity_id,
                    EntityBase.EntityWrapperByEntityType(entity_type))
        return None

    def as_dict(self):
        data = {
            'template': self.template_id,
            'parent': self.parent_id if self.parent else None,
            'name': self.name,
            'description': self.description,
            'creator_entity_id': self.creator_entity_id,
            'creator_entity_type': self.creator_entity_type,
            'recipient_entity_id': self.recipient_entity_id,
            'recipient_entity_type': self.recipient_entity_type,
            'proposed_donation_amount': self.proposed_donation_amount,
            'proposed_donation_amount_decline': self.proposed_donation_amount_decline,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'image': '/file/serve/%s' % self.image.id if self.image else None,
            'youtube_video_id': self.youtube_video_id,
            'participations': []
        }
        return data

    def as_json(self):
        return json.dumps(self.as_dict())

    @property
    def link(self):
        return "%s/challenges/%s" % (settings.SPUDMART_BASE_URL, self.id)

    @property
    def accept_challenge_link(self):
        return "%s/challenges/%s/accept/notice" % (settings.SPUDMART_BASE_URL, self.id)


class ChallengeParticipation(models.Model):
    PRE_ACCEPTED_STATE = '00'
    DECLINED_STATE = '01'
    DONATE_ONLY_STATE = '02'
    AWAITING_PAYMENT = 'AP'
    ACCEPTED_STATE = '03'

    STATES = (PRE_ACCEPTED_STATE, DECLINED_STATE, DONATE_ONLY_STATE, ACCEPTED_STATE, AWAITING_PAYMENT)

    STATES_CHOICES = (
        (PRE_ACCEPTED_STATE, 'Pre accepted state'),
        (DECLINED_STATE, 'Declined State'),
        (DONATE_ONLY_STATE, 'Donate Only State'),
        (ACCEPTED_STATE, 'Accepted State'),
        (AWAITING_PAYMENT, 'Awaiting Payment'),
    )

    challenge = models.ForeignKey(Challenge)
    participating_entity_id = models.CharField(max_length=255)
    participating_entity_type = models.CharField(max_length=255)
    donation_amount = models.FloatField(null=True, blank=True, default=None)
    state = models.CharField(max_length=255, choices=STATES_CHOICES, null=True, blank=True)
    image = models.ForeignKey(UploadedFile, null=True, default=None, related_name='challenge_participation_image')
    message = models.TextField(default='', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    youtube_video_id = models.CharField(max_length=255, default='', null=True, blank=True)
    state_engine = models.CharField(max_length=256, default=None, null=True)
    state_engine_state = models.CharField(max_length=256, default=None, null=True)

    def is_accepted(self):
        return self.state == self.ACCEPTED_STATE

    def is_donated_only(self):
        return self.state == self.DONATE_ONLY_STATE

    def is_declined(self):
        return self.state == self.DECLINED_STATE

    def as_dict(self):
        data = {
            'challenge': self.challenge_id,
            'participating_entity_id': self.participating_entity_id,
            'participating_entity_type': self.participating_entity_type,
            'donation_amount': self.donation_amount,
            'state': self.state,
            'message': self.message,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'youtube_video_id': self.youtube_video_id,
            'state_engine': self.state_engine,
            'state_engine_state': self.state_engine_state,
            'id': self.id,
        }
        return data

    def as_json(self):
        return json.dumps(self.as_dict())

    def link(self):
        """
        Gets a link to resume the challenge, or review submission
        :return: a rel link in the form of a string
        """
        if self.state == self.PRE_ACCEPTED_STATE:
            return '/challenges/%s/accept/notice?just_pledged=True' % self.challenge.id
        if self.state == self.ACCEPTED_STATE:
            recipient_state = self.challenge.get_recipient().state
            return '/challenges/%s/beneficiary/%s' % (self.challenge.id, recipient_state)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        from spudderadmin.templatetags.featuretags import feature_is_enabled
        if feature_is_enabled('challenge_tree'):
            ChallengeTree.AddOrUpdateParticipationToTree(self.challenge, self.as_json())
        return self.save(force_insert, force_update, using, update_fields)


class ChallengeChallengeParticipation(models.Model):
    STATE_PRE_COMPLETE = '01'
    STATE_COMPLETE = '02'

    STATES = (STATE_PRE_COMPLETE, STATE_COMPLETE)

    state = models.CharField(max_length=2, default=STATE_PRE_COMPLETE)
    participating_entity_id = models.CharField(max_length=255)
    participating_entity_type = models.CharField(max_length=255)
    recipient_entity_id = models.CharField(max_length=255, null=True, blank=True, default=None)
    recipient_entity_type = models.CharField(max_length=255, null=True, blank=True, default=None)
    youtube_video_id = models.CharField(max_length=255, default='', null=True, blank=True)
    image = models.ForeignKey(
        UploadedFile, null=True, default=None, related_name='challenge_challenge_participation_image')
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=2056, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ChallengeTree(models.Model):
    base_challenge = models.ForeignKey(Challenge)

    @classmethod
    def GetChallengeTree(cls, challenge):
        challenge_tree_challenge = _ChallengeTreeChallenge.objects.get(challenge_id=challenge.id)
        return challenge_tree_challenge.challenge_tree

    @classmethod
    def CreateNewTree(cls, challenge_with_no_parent):
        tree, created = ChallengeTree.objects.get_or_create(base_challenge=challenge_with_no_parent)
        tree._add_challenge(challenge_with_no_parent)
        return tree

    @classmethod
    def AddChallengeToTree(cls, challenge):
        parent = challenge.parent
        challenge_tree = cls.GetChallengeTree(parent)
        challenge_tree._add_challenge(challenge)

    @classmethod
    def AddOrUpdateParticipationToTree(cls, challenge, challenge_participation):
        tree = cls.GetChallengeTree(challenge)  # get the right tree
        tree._add_participation_to_challenge(challenge, challenge_participation)

    def _add_challenge(self, challenge):
        ctc = _ChallengeTreeChallenge.CreateForChallengeAndTree(challenge=challenge, tree=self)
        ctc.save()

    def _add_participation_to_challenge(self, challenge, participation):
        ctc = _ChallengeTreeChallenge.objects.get(challenge_tree=self, challenge_id=challenge.id)
        ctc.update_participation(participation)

    def get_tree(self):
        raise DeprecationWarning("this is no longer a valid way to use the tree")
        # ctcs = _ChallengeTreeChallenge.objects.filter(challenge_tree=self)
        # ctcs_list = list(ctcs)
        # parent = None
        # for ctc in ctcs_list:
        #     ctc.json_data = json.loads(ctc.challenge_json)
        #     if ctc.json_data['parent'] is None:
        #         parent = ctc
        # ctcs_list.remove(parent)
        # tree = ChallengeTreeHelper(id=parent.challenge_id, children={}, **parent.json_data)
        # while ctcs_list:
        #     ctcs_list_copy = ctcs_list[:]
        #     for ctc in ctcs_list_copy:
        #         element = TreeElement(ctc.challenge_id, children={}, **ctc.json_data)
        #         if tree.add_element(element, ctc.json_data['parent']):
        #             ctcs_list.remove(ctc)
        #
        # return tree


class _ChallengeTreeChallenge(models.Model):
    challenge_id = models.CharField(max_length=255)
    challenge_json = models.TextField()
    challenge_tree = models.ForeignKey(ChallengeTree)

    @classmethod
    def CreateForChallengeAndTree(cls, challenge, tree):
        ctc, created = _ChallengeTreeChallenge.objects.get_or_create(
            challenge_id=challenge.id,
            challenge_tree=tree)
        ctc.challenge_json = challenge.as_json()
        ctc.save()
        return ctc

    def update_participation(self, participation):
        challenge = json.loads(self.challenge_json)
        if not 'participations' in challenge:
            challenge['participations'] = []
        new_participations = []
        for p in challenge['participations']:
            if p['id'] != participation:
                new_participations.append(p)
        new_participations.append(participation)
        challenge['participations'] = new_participations
        self.challenge_json = json.dumps(challenge)
        self.save()