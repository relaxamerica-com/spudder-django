from hashlib import md5


def encoded_admin_session_variable_name():
    return md5('ADMIN_SESSION').hexdigest()
