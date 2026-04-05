from django.db import models
from django.contrib.auth.models import User
from tenant_management.models import TENANT

# Create your models here.
class PRODUCT(models.Model):
    tenant = models.ForeignKey(TENANT, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)

    name = models.CharField(max_length = 100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=255, blank=True, null=True)
    
    is_available = models.BooleanField(default='True')