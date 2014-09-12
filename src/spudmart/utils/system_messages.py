from spudmart.utils.models import SystemMessage


def add_system_message(body, user=None):
    message = SystemMessage(body=body)

    if user:
        message.user = user

    message.save()


def get_messages_for_user(user):
    if user.is_anonymous():
        return []

    system_messages = SystemMessage.objects.filter(user=user, delivered=False)
    messages = []

    for message in system_messages:
        message.delivered = True
        message.save()

        messages.append(message)

    return messages