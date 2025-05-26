from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetToken
from django.utils import timezone

@shared_task
def send_password_reset_email(email, reset_link):
    """
    Sends a password reset email to the specified address.

    This Celery task is responsible for delivering a reset link,
    allowing them to reset their password securely.

    Args:
        email (str): The recipient's email address.
        reset_link (str): The URL link that the user can use to reset their password.
    """

    send_mail(
        subject='Password Reset Request',
        message=f'Click the link below to reset your password:\n\n{reset_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )

@shared_task
def delete_expired_tokens():
    """
    Deletes expired password reset tokens from the database.

    This task runs periodically (you should schedule it via Celery beat or cron)
    and removes all tokens older than 30 minutes to prevent reuse and database clutter.
    """
    
    expiration_time = timezone.now() - timezone.timedelta(minutes=30)
    PasswordResetToken.objects.filter(
        created_at__lt=expiration_time, 
    ).delete()