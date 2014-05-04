def get_key(user, name):
    return '%(name)s_%(user)s' % {'name': name, 'user': user.username}