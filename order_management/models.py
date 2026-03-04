from django.db import models
from django.contrib.auth.models import User

class ORDER(models.Model):
    """
    Represents a customer order in the system.
    Stores what was ordered, by whom, payment info, and order status.
    """

    # Reference to the user who made the order
    user = models.ForeignKey(User, on_delete=models.CASCADE)

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

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} - {self.orderStatus}"