import json
from django.db import models
from spudderdomain.models import TempClub, Challenge
from spudderspuds.challenges.utils import Tree, TreeElement


class TempClubOtherInformation(models.Model):
    temp_club = models.ForeignKey(TempClub)
    other_information = models.TextField()
    website = models.URLField(blank=True)
    contact_number = models.CharField(blank=True)


class ChallengeTree(models.Model):
    base_challenge = models.ForeignKey(Challenge)

    @classmethod
    def GetChallengeTree(cls, challenge):
        challenge_tree_challenge = _ChallengeTreeChallenge.objects.get(challenge_id=challenge.id)
        return challenge_tree_challenge.challenge_tree

    @classmethod
    def CreateNewTree(cls, challenge_with_no_parent):
        tree = ChallengeTree(base_challenge=challenge_with_no_parent)
        tree.save()
        tree._add_challenge(challenge_with_no_parent)
        return tree

    @classmethod
    def AddChallengeToTree(cls, challenge):
        parent = challenge.parent
        challenge_tree = cls.GetChallengeTree(parent)
        challenge_tree._add_challenge(challenge)

    @classmethod
    def AddParticipationToTree(cls, challenge, challenge_participation):
        tree = cls.GetChallengeTree(challenge)  # get the right tree
        tree._add_participation_to_challenge(challenge, challenge_participation)
        pass

    def _add_challenge(self, challenge):
        ctc = _ChallengeTreeChallenge.CreateForChallengeAndTree(challenge=challenge, tree=self)
        ctc.save()

    def _add_participation_to_challenge(self, challenge, participation):
        ctc = _ChallengeTreeChallenge.objects.get(challenge_tree=self, challenge_id=challenge.id)
        ctc.add_participation(participation)

    def get_tree(self):
        ctcs = _ChallengeTreeChallenge.objects.filter(challenge_tree=self)
        ctcs_list = list(ctcs)
        parent = None
        for ctc in ctcs_list:
            ctc.json_data = json.loads(ctc.challenge_json)
            if ctc.json_data['parent'] is None:
                parent = ctc
        ctcs_list.remove(parent)
        tree = Tree(id=parent.challenge_id, children={}, **parent.json_data)
        while ctcs_list:
            ctcs_list_copy = ctcs_list[:]
            for ctc in ctcs_list_copy:
                element = TreeElement(ctc.challenge_id, children={}, **ctc.json_data)
                if tree.add_element(element, ctc.json_data['parent']):
                    ctcs_list.remove(ctc)

        return tree.to_dict()


class _ChallengeTreeChallenge(models.Model):
    challenge_id = models.CharField(max_length=255)
    challenge_json = models.TextField()
    challenge_tree = models.ForeignKey(ChallengeTree)

    @classmethod
    def CreateForChallengeAndTree(cls, challenge, tree):
        ctc = _ChallengeTreeChallenge(
            challenge_id=challenge.id,
            challenge_json=challenge.as_json(),
            challenge_tree=tree)
        return ctc

    def add_participation(self, participation):
        challenge = json.loads(self.challenge_json)
        if not 'participations' in challenge:
            challenge['participations'] = []
        # this is not enought as we need to get user details and store them here to
        challenge['participations'].append(participation.as_dict())
        self.challenge_json = json.dumps(challenge)
        self.save()
