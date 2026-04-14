from django.db import models
from tenant_management.models import TENANT

class CHECKOUT(models.Model):
	tenant = models.ForeignKey(TENANT, on_delete=models.CASCADE)

	#link the cart of the customer to a browser session
	session_key = models.CharField(max_length=40)
	customer_phone = models.CharField(max_length=20)

	customer_name = models.CharField(max_length=100, null=True, blank=True)



	total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	
	status = models.CharField(
		max_length=20,
		choices=[
			("pending", "Pending"),
			("paid", "Paid"),
			("failed", "Failed"),
		],
		default="pending"
	)
	
	# Track the date and time the checkout was made
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

