from django.template.defaulttags import register


@register.simple_tag
def link_to_twitter_profile(twitter_username):
    return 'http://twitter.com/%s' % ((twitter_username or '').replace('@', ''))


@register.simple_tag
def link_to_facebook_profile(facebook_username):
    return 'http://facebook.com/%s' % (facebook_username or '')
