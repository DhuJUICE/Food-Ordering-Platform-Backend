from django.db import models
from django.contrib.auth.models import User
from tenant_management.models import TENANT
from product_management.models import PRODUCT
from django.utils import timezone

class ORDER(models.Model):
	tenant = models.ForeignKey(TENANT, on_delete=models.CASCADE)
	
	session_key = models.CharField(max_length=40)
	
	# Guest details
	customer_name = models.CharField(max_length=100, null=True, blank=True)
	customer_phone = models.CharField(max_length=20)
	
	order_number = models.IntegerField(unique=True, blank=True, null=True)

	# Automatically store when the order was created/updated
	updated_at = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(default=timezone.now)

	# Payment method used for the order
	paymentMethod = models.CharField(
		max_length=10,
		choices=[("cash", "Cash"), ("card", "Card")],
		default="card",
		help_text="Payment method used for this order"
	)

	# Current status of the order in the workflow
	ORDER_STATUS_CHOICES = [
		("waiting", "Waiting"),       # Order just placed, not yet started
		("preparing", "Preparing"),   # Kitchen/vendor started preparing
		("done", "Done"),             # Order ready/completed
	]
	status = models.CharField(
		max_length=15,
		choices=ORDER_STATUS_CHOICES,
		default="waiting",
		help_text="Current status of the order"
	)

	is_collected = models.BooleanField(
		default=False,
		help_text="True if the customer has collected this order"
	)

	total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	def save(self, *args, **kwargs):
		if not self.order_number:
			# Get the highest existing order number
			last_number = ORDER.objects.aggregate(models.Max('order_number'))['order_number__max'] or 0
			self.order_number = last_number + 1
		super().save(*args, **kwargs)

class ORDERITEM(models.Model):
	order = models.ForeignKey(ORDER, on_delete=models.CASCADE)
	product = models.ForeignKey(PRODUCT, on_delete=models.CASCADE)

	quantity = models.IntegerField()
	price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

	class Meta:
		unique_together = ('order', 'product')