from google.appengine.api import mail
from django.shortcuts import render
from django.http import HttpResponse
import settings
from spudmart.flags.models import Flag, STATE_NEW
from django.contrib.auth.models import User
from datetime import datetime
import simplejson
from spudmart.upload.models import UploadedFile


def test(request):
    texts = {'Description': 'The page description', 'something':'something else'}
    imgs = {'Logo': 'The small image next to the page title', 'cover':'that big thing'}
    return render(request, 'components/flags/flag_test.html',{
        'text_fields': texts,
        'img_fields': imgs
    })


def flag_page(request):
    """
    Flags a page as containing inappropriate or incorrect content

    Sends an email to the page owner + ZenDesk account informing them
    that the page content needs management

    :param request: a POST request containing all of the data needed to
        create the Flag object
    :return: a blank HttpResponse on success
    """
    ownerid = request.POST.get('owner_id')
    owner = User.objects.get(id=ownerid)
    url = request.POST.get('url')
    try:
        custom_text = simplejson.loads(request.POST.get('text'))
    except TypeError:
        custom_text = None
    try:
        custom_imgs = simplejson.loads(request.POST.get('img'))
    except TypeError:
        custom_imgs = None
    else:
        temp_custom_imgs = dict()
        for key in custom_imgs:
            img = UploadedFile.objects.get(id=custom_imgs[key])
            temp_custom_imgs[key] = img
        custom_imgs = temp_custom_imgs
    flagger_name = request.POST.get('name', None)
    flagger_email = request.POST.get('email', None)
    user = request.POST.get('user_id', None)
    if user:
        user = User.objects.get(id=user)
    type = request.POST['type']
    comment = request.POST['comment']

    new_flag = Flag(url=url, owner=owner, state=STATE_NEW,
                    custom_text=custom_text, custom_imgs=custom_imgs,
                    time=datetime.utcnow(), flag_type=type, comment=comment,
                    flagger_email=flagger_email, flagger_name=flagger_name,
                    flagger_user=user)

    new_flag.save()

    send_owner_message(new_flag, request.META['HTTP_HOST'])
    send_zendesk_message(new_flag, request.META['HTTP_HOST'])

    return HttpResponse()


def send_owner_message(flag, host):
    """
    Sends a message to the person responsible for flagged content.
    :param flag: any Flag
    :type flag: Flag
    :param host: the site host as a string
    """

    message = ("Hello Spudder User!\n" +
               "The page that you manage (http://%s%s) " %
               (host, flag.url) +
               "has been marked as containing %s content" % type +
               ". Please review the following fields:\n")

    if flag.custom_imgs:
        message += "\nCustom image"
        if len(flag.custom_imgs) > 1:
            message += "s"
        message += ":\n"

        image_links = flag.get_images_as_links()
        for key in image_links:
            message += "%s (visible at http://%s%s)\n" % (
                key, host, image_links[key]
            )

    if flag.custom_text:
        message += "\nCustom text field"
        if len(flag.custom_text) > 1:
            message += "s"
        message += ":\n"

        for key in flag.custom_text:
            message += "%s: %s\n" % (key, flag.custom_text[key])

    message += "\nThe flagger left you the following comment: \n%s" % flag.comment

    subject = "Your page has been flagged with %s content" % flag.flag_type

    mail.send_mail(subject=subject, body=message,
                   sender=settings.SERVER_EMAIL, to=['thecoloryes@gmail.com'])


def send_zendesk_message(flag, host):
    """
    Sends a message to the zendesk account when a page is flagged
    :param flag: any Flag
    :type flag: Flag
    :param host: the site host as a string
    """

    message = ("Content on the page at http://%s%s has been marked as " %
              (host, flag.url) +
              "containing %s content. It was flagged by " % flag.flag_type)

    if flag.flagger_user:
        message += "Spudder User %s %s (%s)" % (
                   flag.flagger_user.first_name,
                   flag.flagger_user.last_name,
                   flag.flagger_user.email)
    else:
        message += "%s (%s)" % (flag.flagger_name, flag.flagger_email)

    message += (" at %s GMT on %s.\n" % (flag.time.time(), flag.time.date()) +
                "The following fields were flagged:\n")

    if flag.custom_imgs:
        message += "\nCustom image"
        if len(flag.custom_imgs) > 1:
            message += "s"
        message += ":\n"

        image_links = flag.get_images_as_links()
        for key in image_links:
            message += "%s (visible at http://%s%s)\n" % (
                key, host, image_links[key]
            )

    if flag.custom_text:
        message += "\nCustom text field"
        if len(flag.custom_text) > 1:
            message += "s"
        message += ":\n"

        for key in flag.custom_text:
            message += "%s: %s\n" % (key, flag.custom_text[key])

    message += "\nThe flagger left the following comment:\n%s" % flag.comment

    subject = "A page has been flagged with %s content" % flag.flag_type

    mail.send_mail(subject=subject, body=message,
                   sender=settings.SERVER_EMAIL, to=['thecoloryes@gmail.com'])

