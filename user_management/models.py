from django.db import models
from django.contrib.auth.models import User
from tenant_management.models import TENANT

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey(TENANT, on_delete=models.CASCADE, null=True, blank=True)

    USER_ROLES_CHOICES = [
        ('staff', 'Staff'),
        ('admin', 'admin'),
    ]

    role = models.CharField(max_length=20, choices=USER_ROLES_CHOICES, default='staff')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
