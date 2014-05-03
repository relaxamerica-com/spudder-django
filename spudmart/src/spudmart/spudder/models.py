from django.db import models


class Team(models.Model):
    spudder_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def update_from_json(self, json_data):
        self.name = json_data['name']
        self.save()

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return self.name


class TeamOffer(models.Model):
    spudder_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    donation = models.FloatField(default=0)
    quantity = models.IntegerField(default=0)
    team = models.ForeignKey(Team)

    def update_from_json(self, json_data):
        self.title = json_data['title']
        self.donation = float(json_data['donation'])
        self.details = json_data['details']
        self.quantity = int(json_data['quantity'])

        self.save()

    def __unicode__(self):
        return u'%s' % self.title

    def __str__(self):
        return self.title