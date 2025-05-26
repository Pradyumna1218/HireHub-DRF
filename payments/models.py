from django.db import models
from users.models import Client, User, Freelancer
from services.models import Service, Proposal
from django.utils import timezone


class Order(models.Model):
    """
    Represents an order placed by a client for a service provided by a freelancer.
    
    Attributes:
        client (ForeignKey): The client who placed the order.
        service (ForeignKey): The service being ordered.
        proposal (OneToOneField): The proposal associated with this order, if any.
        freelancer (ForeignKey): The freelancer fulfilling the order.
        order_date (DateTimeField): When the order was created.
        delivery_date (DateTimeField): Expected delivery date for the service.
        total_amount (DecimalField): Total price of the order.
        status (CharField): Current status of the order (Pending, In Progress, Completed).
    """

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
    """
    Tracks payment transactions for orders.

    Attributes:
        order (ForeignKey): The order this payment belongs to.
        user (ForeignKey): The user who made the payment.
        status (CharField): Payment status (Pending, In Progress, Completed).
        payment_amount (DecimalField): Amount paid.
        payment_date (DateTimeField): Timestamp of the payment.
        khalti_token (CharField): Token returned from Khalti payment gateway.
        khalti_transaction_id (CharField): Transaction ID from Khalti after verification.
        is_verified (BooleanField): Whether the payment was verified successfully.
    """
    
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
    
