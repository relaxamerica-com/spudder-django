from django.core import mail
from django.core.mail.message import EmailMultiAlternatives
from django.utils.html import strip_tags


def send_email(sender, recipient, subject, body):
    connection = mail.get_connection()
    connection.open()

    email_message = EmailMultiAlternatives(subject=subject, body=strip_tags(body), from_email=sender, to=[recipient])
    if body != strip_tags(body):
        email_message.attach_alternative(body, "text/html")

    connection.send_messages([email_message])
    connection.close()