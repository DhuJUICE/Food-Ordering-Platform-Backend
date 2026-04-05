from django.db import models
from django.contrib.auth.models import User
from tenant_management.models import TENANT
from product_management.models import PRODUCT

class CART(models.Model):
    tenant = models.ForeignKey(TENANT, on_delete=models.CASCADE)

	#link the cart of the customer to a browser session
    session_key = models.CharField(max_length=40)
    
    # Track the date and time the cart was last updated
    created_at = models.DateTimeField(auto_now_add=True)

class CARTITEM(models.Model):
    cart = models.ForeignKey(CART, on_delete=models.CASCADE)
    product = models.ForeignKey(PRODUCT, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    #ensures that one cart cannot have the same product more than once
    class Meta:
        unique_together = ('cart', 'product')
