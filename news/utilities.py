from django.core.signing import Signer
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import AdvUser, Subscribe


def get_or_create_subscribers(user):
    """Получить или создать подписчиков"""

    try:
        subscribers = Subscribe.objects.get(user=user.pk)
    except Subscribe.DoesNotExist:
        subscribers = Subscribe(user=user.pk)
        subscribers.save()
        subscribers = Subscribe.objects.get(user=user.pk)

    return subscribers


def get_subscribes(user):
    """Получить подписки"""

    subscribes = []

    for i in Subscribe.objects.all():
        if AdvUser.objects.get(pk=user) in i.subscribers.all():
            subscribes.append(AdvUser.objects.get(pk=i.user))

    return subscribes


def send_activation(user, why):
    """Отправить письмо для активации"""

    signer = Signer()

    if settings.ALLOWED_HOSTS:
        host = 'https://' + settings.ALLOWED_HOSTS[0]
    else:
        host = 'http://127.0.0.1:8000'

    context = {
        'user': user,
        'host': host,
        'sign': signer.sign(user.username)
    }

    subject = render_to_string('email/activation_letter_subject.txt', context)

    if why == 'register':
        body_text = render_to_string('email/activation_letter_body.txt', context)
    elif why == 'edited':
        body_text = render_to_string('email/activation_edit_body.txt', context)
    else:
        body_text = render_to_string('email/activation_body.txt', context)

    send_mail(subject, body_text, settings.EMAIL_HOST_USER, (user.email,))


def send_deleted_notification(user, why):
    """Отправить письмо при удалении профиля"""

    signer = Signer()

    if settings.ALLOWED_HOSTS:
        address = 'https://' + settings.ALLOWED_HOSTS[0]
    else:
        address = 'http://127.0.0.1:8000'

    context = {
        'user': user,
        'address': address,
        'sign': signer.sign(user.username),
    }

    subject = None
    body = None

    if why == 'deleted':
        subject = render_to_string('email/delete_profile_subject.txt', context)
        body = render_to_string('email/delete_profile_body.txt', context)
    elif why == 'recovery':
        subject = render_to_string('email/recovery_profile_subject.txt', context)
        body = render_to_string('email/recovery_profile_body.txt', context)

    send_mail(subject, body, settings.EMAIL_HOST_USER, (user.email,))
