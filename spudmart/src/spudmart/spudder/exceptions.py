class SpudderAPIError(Exception):
    def __init__(self, code):
        self.code = code


class SponsorshipSynchronizationErrorCode():
    def __init__(self):
        pass

    # ST - SPONSORED TEAM
    ST_QUERY_DEADLINE = 100
    ST_CREATION_DEADLINE = 101
    ST_RELATION_ADD_DEADLINE = 102

    # TS - TEAM SPONSORS
    TS_QUERY_DEADLINE = 200
    TS_CREATION_DEADLINE = 201
    TS_RELATION_ADD_DEADLINE = 202

    # TOS - TEAM OFFER SPONSORS
    TOS_QUERY_DEADLINE = 300
    TOS_CREATION_DEADLINE = 301
    TOS_RELATION_ADD_DEADLINE = 302

    error_messages = {
        ST_QUERY_DEADLINE: "queering for SponsoredTeam entity",
        ST_CREATION_DEADLINE: "trying to create SponsoredTeam entity",
        ST_RELATION_ADD_DEADLINE: "trying to add team relation to SponsoredTeam entity",
        TS_QUERY_DEADLINE: "queering for TeamSponsors entity",
        TS_CREATION_DEADLINE: "trying to create TeamSponsors entity",
        TS_RELATION_ADD_DEADLINE: "trying to add sponsor relation to TeamSponsors entity",
        TOS_QUERY_DEADLINE: "queering for TeamOfferSponsors entity",
        TOS_CREATION_DEADLINE: "trying to create TeamOfferSponsors entity",
        TOS_RELATION_ADD_DEADLINE: "trying to add sponsor relation to TeamOfferSponsors entity"
    }

    @staticmethod
    def get_message(code):
        prefix = 'Deadline exceeded error while'

        error_message = "%s %s" % (prefix, SponsorshipSynchronizationErrorCode.error_messages[code])

        return error_message


class SponsorshipSynchronizationError(SpudderAPIError):
    def __str__(self):
        return SponsorshipSynchronizationErrorCode.get_message(self.code)


class UserErrorCode():
    def __init__(self):
        pass

    GET_USER_DATA_DEADLINE = 10
    SIGNUP_USER_DEADLINE = 11
    SIGN_IN_USER_DEADLINE = 12
    SET_USER_IS_SPONSOR_DEADLINE = 13

    error_messages = {
        GET_USER_DATA_DEADLINE: "fetching user data",
        SIGNUP_USER_DEADLINE: "trying to create User entity",
        SIGN_IN_USER_DEADLINE: "trying to sign in user",
        SET_USER_IS_SPONSOR_DEADLINE: "trying to set isSponsor flag for User entity"
    }

    @staticmethod
    def get_message(code):
        prefix = 'Deadline exceeded error while'

        error_message = "%s %s" % (prefix, SponsorshipSynchronizationErrorCode.error_messages[code])

        return error_message


class UserError(SpudderAPIError):
    def __str__(self):
        return UserErrorCode.get_message(self.code)