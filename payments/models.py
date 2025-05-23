from django.db import models
from users.models import Client, User, Freelancer
from services.models import Service, Proposal
from django.utils import timezone


class Order(models.Model):

    status_choices = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name= 'orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name= 'orders')
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE, related_name='order', null=True, blank=True)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE, null=True, blank=True)
    
    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=status_choices, default="Pending") 

class Payment(models.Model):
    status_choices = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")

    status = models.CharField(max_length=50, choices=status_choices, default="Pending")
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)

    khalti_token = models.CharField(max_length=255, blank=True, null = True)
    khalti_transaction_id = models.CharField(max_length=255, blank=True, null = True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment #{self.id} for Order #{self.order.id}"
    
