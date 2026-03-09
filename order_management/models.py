from django.db import models
from django.contrib.auth.models import User

class ORDER(models.Model):
    # Guest details
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20)
    
    order_number = models.IntegerField(unique=True, blank=True, null=True)

    # Store order items with their quantities as a JSON object
    # Example: { "product_id_1": 2, "product_id_2": 1 }
    menuCartItems = models.JSONField(
        default=dict,
        help_text="Dictionary where keys are PRODUCT IDs and values are quantities"
    )

    # Automatically store when the order was created/updated
    datetimeUpdated = models.DateTimeField(auto_now=True)

    # Payment method used for the order
    paymentMethod = models.CharField(
        max_length=10,
        choices=[("cash", "Cash"), ("card", "Card")],
        default="card",
        help_text="Payment method used for this order"
    )

    # Current status of the order in the workflow
    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),       # Order just placed, not yet started
        ("preparing", "Preparing"),   # Kitchen/vendor started preparing
        ("done", "Done"),             # Order ready/completed
        ("cancelled", "Cancelled"),   # Order cancelled/failure
    ]
    orderStatus = models.CharField(
        max_length=15,
        choices=ORDER_STATUS_CHOICES,
        default="pending",
        help_text="Current status of the order"
    )

    collected = models.BooleanField(
        default=False,
        help_text="True if the customer has collected this order"
    )

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Get the highest existing order number
            last_number = ORDER.objects.aggregate(models.Max('order_number'))['order_number__max'] or 0
            self.order_number = last_number + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} - {self.orderStatus}"