import tweepy
from django.db import models


class AtPostSpudServiceConfiguration(models.Model):
    SITE_UNIQUE_ID = "01"
    site_unique_id = models.CharField(max_length=256)
    active = models.BooleanField(default=False)

    @classmethod
    def GetForSite(cls):
        return AtPostSpudServiceConfiguration.objects.get_or_create(site_unique_id=cls.SITE_UNIQUE_ID)[0]

    def activate(self):
        self.active = True
        self.save()

    def deactivate(self):
        self.active = False
        self.save()


class AtPostSpudTwitterAuthentication(models.Model):
    SITE_UNIQUE_ID = "01"
    site_unique_id = models.CharField(max_length=256)
    api_key = models.CharField(max_length=256)
    api_secret = models.CharField(max_length=256)
    access_key = models.CharField(max_length=256)
    access_secret = models.CharField(max_length=256)

    @classmethod
    def GetForSite(cls):
        return AtPostSpudTwitterAuthentication.objects.get_or_create(site_unique_id=cls.SITE_UNIQUE_ID)[0]

    def authorized(self):
        if not self.api_key or not self.api_secret:
            return False
        if not self.access_key or not self.access_secret:
            return False
        try:
            return bool(self.api().rate_limit_status())  # We user ratelimit to check as the limit for this call is high
        except:
            return False

    def api(self):
        auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
        auth.secure = True
        auth.set_access_token(self.access_key, self.access_secret)
        return tweepy.API(auth)

    def reset(self):
        self.api_key = ''
        self.api_secret = ''
        self.access_key = ''
        self.access_secret = ''
        self.save()

    def get_authorization_url_and_request_token(self):
        auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
        auth.secure = True
        try:
            return auth.get_authorization_url(), auth.request_token.key, auth.request_token.secret
        except:
            return None, None, None

    def update_with_pin(self, pin, key, secret):
        auth = tweepy.OAuthHandler(self.api_key, self.access_secret)
        auth.set_request_token(key, secret)
        auth.get_access_token(pin)
        self.access_key = auth.access_token.key
        self.access_secret = auth.access_token.secret
        self.save()


class AtPostSpudTwitterCounter(models.Model):
    SITE_UNIQUE_ID = "01"
    site_unique_id = models.CharField(max_length=2)
    last_processed_id = models.IntegerField()

    @classmethod
    def GetForSite(cls):
        counter, created = AtPostSpudTwitterCounter.objects.get_or_create(
            site_unique_id=cls.SITE_UNIQUE_ID, defaults={'last_processed_id': 1})
        return counter

    @classmethod
    def SetLastProcessedId(cls, last_processed_id):
        counter = cls.GetForSite()
        counter.last_processed_id = last_processed_id
        counter.save()

    @classmethod
    def GetLastProcessedId(cls):
        counter = cls.GetForSite()
        return counter.last_processed_id