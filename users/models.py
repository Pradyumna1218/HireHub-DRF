from django.db import models
from django.contrib.auth.models import AbstractUser
from services.models import Skill, Category
from django.conf import settings
from django.utils import timezone
class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Fields:
        email (EmailField): Unique email address for the user.
        phone (CharField): Phone number, required.
        groups (ManyToManyField): Custom relation to Django auth groups.
        user_permissions (ManyToManyField): Custom relation to user permissions.
    """

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=False, null=False)

    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set', 
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='custom_user_permissions_set', 
        blank=True
    )

    def __str__(self):
        return self.username

class Freelancer(models.Model):
    """
    Model representing a freelancer profile.

    Fields:
        user (OneToOneField): Links to the custom User model.
        profile (TextField): Optional bio/description.
        skills (ManyToManyField): Skills the freelancer has.
        rating (DecimalField): Average freelancer rating (0.0 to 9.9).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile = models.TextField(blank=True, null= True)
    skills = models.ManyToManyField(Skill, blank=True) 
    rating = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)

    def __str__(self):
        return self.user.username

class Client(models.Model):
    """
    Model representing a client profile.

    Fields:
        user (OneToOneField): Links to the custom User model.
        preferred_categories (ManyToManyField): Categories the client is interested in.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    preferred_categories = models.ManyToManyField(Category, blank=True, related_name="clients")

    def __str__(self):
        return self.user.username
    

class PasswordResetToken(models.Model):
    """
    Token model for handling password reset functionality.

    Fields:
        user (ForeignKey): Linked user the token is for.
        token (CharField): The actual reset token.
        created_at (DateTimeField): When the token was generated.
        used (BooleanField): Whether the token has already been used.
    """
     
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null = True,
        blank=True,
        related_name="reset_token"
    )
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default= timezone.now)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Token for {self.user} - Used: {self.used}"