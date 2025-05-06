from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="skills")

    def __str__(self):
        return self.name


class Service(models.Model):
    freelancer = models.ForeignKey("users.Freelancer", on_delete=models.CASCADE, related_name="services")
    categories = models.ManyToManyField('Category', related_name= "services")
    
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.freelancer.user.username}"


class Proposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    def get_models(self):
        from users.models import Freelancer, Client  
        return Freelancer, Client

    freelancer = models.ForeignKey('users.Freelancer', on_delete=models.CASCADE, related_name="freeproposal")
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name="cliproposal")
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='serproposal')

    proposal_date = models.DateTimeField(default=timezone.now)
    proposed_price = models.DecimalField(decimal_places=2, max_digits=10)

    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="pending")

    def __str__(self):
        return f"Proposal {self.id} - {self.freelancer.user.username} -> {self.client.user.username}"