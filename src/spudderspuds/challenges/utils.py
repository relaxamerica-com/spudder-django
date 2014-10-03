from spudderdomain.controllers import RoleController, EntityController
from spudderdomain.models import FanPage, Club, TempClub


class TreeElement(object):
    parent_id = None

    def __init__(self, id, children={}, **kwargs):
        self.id = str(id)
        self.children = children
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def has_child(self, child):
        return child.id in self.children

    def add_child(self, child):
        self.children[child.id] = child

    def remove_child(self, child):
        self.children.pop(child)

    def to_dict(self):
        data = {self.id: self.__dict__.copy()}
        data[self.id]['children'] = []
        for child in self.children:
            data[self.id]['children'].append(self.children[child].to_dict())
        return data


class Tree(object):
    root = None

    def __init__(self, id, children={}, **kwargs):
        self.root = TreeElement(id, children, **kwargs)

    def add_element(self, element, parent_id):
        parent_id = str(parent_id)
        parent = self.find_element(parent_id)
        if parent is not None:
            parent.add_child(element)
            return True
        return False

    def remove_element(self, element):
        tree_element = self.find_element(element.id)
        if tree_element is not None:
            parent = self.find_element(tree_element.parent_id)
            parent.remove_child(element)
            return True
        return False

    def _find_element(self, element, element_id):
        if element_id in element.children:
            return element.children[element_id]
        else:
            for child_id, child in element.children.items():
                found_element = self._find_element(child, element_id)
                if found_element is not  None:
                    return found_element
        return None

    def find_element(self, element_id):
        element_id = str(element_id)
        if self.root.id == element_id:
            return self.root
        else:
            return self._find_element(self.root, element_id)

    def to_dict(self):
        return self.root.to_dict()


class ChallengeTreeHelper(Tree):
    beneficiaries = {}
    _participiants = {}

    def add_beneficiary(self, tree_element):
        recipient_entity_id = tree_element.recipient_entity_id
        recipient_entity_type = tree_element.recipient_entity_type
        if recipient_entity_id not in self.beneficiaries:
            self.beneficiaries[recipient_entity_id] = {
                'entity_id': recipient_entity_id,
                'entity_type': recipient_entity_type,
                'number_of_challenges': 0,
                'total_amount_raised': 0,
                'participants': [],
                'object': None
            }
        self.beneficiaries[recipient_entity_id]['number_of_challenges'] += 1
        for participation in tree_element.participations:
            self.beneficiaries[recipient_entity_id]['total_amount_raised'] += participation['donation_amount']
            participating_entity_id = str(participation['participating_entity_id'])
            participation_data = {
                'entity_id': participating_entity_id,
                'entity_type': participation['participating_entity_type']
            }
            if participation_data not in self.beneficiaries[recipient_entity_id]['participants']:
                self.beneficiaries[recipient_entity_id]['participants'].append(participation_data)
            self._participiants[participating_entity_id] = participation_data

    def __init__(self, id, children={}, **kwargs):
        self.beneficiaries = {}
        self._participiants = {}
        super(ChallengeTreeHelper, self).__init__(id, children, **kwargs)
        self.add_beneficiary(self.root)

    def add_element(self, element, parent_id):
        is_added = super(ChallengeTreeHelper, self).add_element(element, parent_id)
        if is_added:
            self.add_beneficiary(element)
        return is_added

    def update_beneficiaries_data(self):
        # get participiants objects
        # for now fans only
        fan_ids = [int(entity_id) for entity_id, data in self._participiants.items()
                   if data['entity_type'] == RoleController.ENTITY_FAN]
        fans = FanPage.objects.filter(id__in=fan_ids)
        for fan in fans:
            participating_entity_id = str(fan.id)
            self._participiants[participating_entity_id]['object'] = fan

        # get beneficiaries objects
        # for now clubs and temp clubs only
        club_ids = [int(entity_id) for entity_id, data in self.beneficiaries.items()
                    if data['entity_type'] == EntityController.ENTITY_CLUB]
        temp_club_ids = [int(entity_id) for entity_id, entity_type in self.beneficiaries.items()
                         if data['entity_type'] == EntityController.ENTITY_TEMP_CLUB]

        clubs = [c for c in Club.objects.filter(id__in=club_ids)]
        len(clubs)
        for club in clubs:
            club_id = str(club.id)
            self.beneficiaries[club_id]['object'] = club.__dict__
            for participiant_data in self.beneficiaries[club_id]['participants']:
                participating_entity_id = str(participiant_data['entity_id'])
                participiant_data['object'] = self._participiants[participating_entity_id]['object']

        temp_clubs = [tc for tc in TempClub.objects.filter(id__in=temp_club_ids)]
        len(temp_clubs)
        for temp_club in temp_clubs:
            temp_club_id = str(temp_club.id)
            self.beneficiaries[temp_club_id]['object'] = temp_club.__dict__
            for participiant_data in self.beneficiaries[temp_club_id]['participants']:
                participating_entity_id = str(participiant_data['entity_id'])
                participiant_data['object'] = self._participiants[participating_entity_id]['object']

        return self.beneficiaries
