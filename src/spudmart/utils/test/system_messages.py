from django.contrib.auth.models import User
from nose_plugins.noseplugins import FormattedOutputTestCase
from spudmart.utils.models import SystemMessage
from spudmart.utils.system_messages import add_system_message, get_messages_for_user


class MockedRequest():
    def __init__(self):
        pass


class AddingMessages(FormattedOutputTestCase):
    def test_user_specified(self):
        user = User.objects.create(username='user1')

        add_system_message('Some body', user)

        messages = SystemMessage.objects.all()

        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].body, 'Some body')
        self.assertEquals(messages[0].user, user)
        self.assertFalse(messages[0].delivered)

        user.delete()

    def test_user_not_specified(self):
        add_system_message('Some body')

        messages = SystemMessage.objects.all()

        self.assertEquals(len(messages), 1)
        self.assertEquals(messages[0].body, 'Some body')
        self.assertIsNone(messages[0].user)
        self.assertFalse(messages[0].delivered)


class RetrievingMessages(FormattedOutputTestCase):
    def setUp(self):
        self.user = User.objects.create(username='user1')
        add_system_message('Body of first message', self.user)
        add_system_message('Body of second message', self.user)

    def tearDown(self):
        self.user.delete()
        SystemMessage.objects.all().delete()

    def test_get_messages_for_user(self):
        messages = get_messages_for_user(self.user)

        self.assertEquals(len(messages), 2)

        system_messages = SystemMessage.objects.all()
        self.assertEquals(len(system_messages), 2)
        self.assertTrue(system_messages[0])
        self.assertTrue(system_messages[1])

    def test_not_all_messages_are_for_specified_user(self):
        add_system_message('Body of message not for this user')

        messages = get_messages_for_user(self.user)

        self.assertEquals(len(messages), 2)

        system_messages = SystemMessage.objects.filter(user=self.user)
        self.assertEquals(len(system_messages), 2)
        for message in system_messages:
            self.assertTrue(message.delivered)