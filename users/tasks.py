from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_password_reset_email(email, reset_link):
    send_mail(
        subject='Password Reset Request',
        message=f'Click the link below to reset your password:\n\n{reset_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )
