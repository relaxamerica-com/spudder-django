from spudderaccounts.models import Invitation, Notification

# This can't go in settings.py because it would cause a circular import
# bc settings.py is referenced in Invitation, so instead it's

"""
'MESSAGES' is a dict of all the messages sent with invitations. It is organized
into further dicts, with the following structure:
{
<invitation_type>: {
                    <invitation_status>: {
                                         'subject': <message subject>,
                                         'message': <message body>
                                         }
                   }
}

You can expand it as needed, just be sure to follow this structure - it's referenced
this way in the InvitationController. Also be sure to implement all status types for
your new invitation type!

IMPORTANT LOCATION NOTE: This cannot be moved to settings.py because it calls types
seen only in the Invitation model, which in turn references settings.py -- adding it
to settings.py would cause a circular import and break EVERYTHING. (Learned the hard way)
"""
MESSAGES = {
    Invitation.ADMINISTRATE_TEAM_INVITATION: {
        Invitation.PENDING_STATUS: {
            'subject': 'Spudder - You have been invited to administer a team',
            'message': """
You have been invited to administer team "%s".

Please follow the link bellow to accept.
%s

Kind regards, team Spudder.
"""

        },
        Invitation.CANCELED_STATUS: {
            'subject': 'Spudder - Your invitation has expired',
            'message': """
Your invitation to administer team "%s" has expired.


Kind regards, team Spudder.
"""
        },
        Invitation.REVOKED_STATUS: {
            'subject': 'Spudder - Your invitation has been revoked',
            'message': """
Your invitation to administer team "%s" has been revoked.


Kind regards, team Spudder.
"""
        }
    },
    Invitation.REGISTER_AND_ADMINISTRATE_TEAM_INVITATION: {
        'subject': 'Spudder - You have been invited to administer a team',
        'message': """
You have been invited to administer team "%s" at Spudder.

Please follow the link bellow to accept.
%s

Kind regards, team Spudder.
"""
    },
    Invitation.AFFILIATE_INVITE_CLUB_ADMINISTRATOR: {
        Invitation.PENDING_STATUS: {
            'subject': '%s - You have been invited to administer a club on Spudder',
            'message': """
%s has invited you to create and manage the club "%s".

Please follow the link bellow to accept. If you do not have an account on Spudder, you can register at the same time.
%s

Kind regards, team Spudder.
"""

        },
        Invitation.CANCELED_STATUS: {
            'subject': '%s - Your Spudder invitation has expired',
            'message': """
Your invitation to create club "%s" has expired.


Kind regards, team Spudder.
"""
        },
        Invitation.REVOKED_STATUS: {
            'subject': '%s - Your Spudder invitation has been revoked',
            'message': """
Your invitation to manage club "%s" has been revoked.


Kind regards, team Spudder.
"""
        }
    }
}


"""
'NOTIFICATIONS' is a dict of all the messages sent with notifications. It is organized
into further dicts, with the following structure:
{
    <notification_type>: {
        'subject': <message subject>,
        'message': <message body>
    }
}

You can expand it as needed, just be sure to follow this structure - it's referenced
this way in the NotificationController. Also be sure to implement all status types for
your new notification type!

IMPORTANT LOCATION NOTE: This cannot be moved to settings.py because it calls types
seen only in the Notification model, which in turn references settings.py -- adding it
to settings.py would cause a circular import and break EVERYTHING. (Learned the hard way)
"""
NOTIFICATIONS = {
    Notification.COMPLETE_CHALLENGE_NOTIFICATION: {
        'subject': 'Spudder - You have a challenge to complete!',
        'message': ""
    }
}