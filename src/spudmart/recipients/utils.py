from spudmart.recipients.models import Recipient


def get_or_create_recipient(team, user):
    recipients = Recipient.objects.filter(team=team)
    if len(recipients) == 0:
        recipient = Recipient(team=team, registered_by=user)
        recipient.save()
    else:
        recipient = recipients[0]

    return recipient