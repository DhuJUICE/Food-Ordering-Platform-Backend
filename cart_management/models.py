from django.db import models
from django.contrib.auth.models import User
from tenant_management.models import TENANT

class CART(models.Model):
    tenant = models.ForeignKey(TENANT, on_delete=models.CASCADE)

	#link the cart of the customer to a browser session
    session_key = models.CharField(max_length=40)
    
	# Store cart items with their quantities as a JSON object
    menuCartItems = models.JSONField(
        default=dict,
        help_text="Dictionary where keys are MENU item IDs and values are quantities"
    )
    
    # Track the date and time the cart was last updated
    datetimeUpdated = models.DateTimeField(auto_now=True)
