from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

class management(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    phone_no = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class PasswordResetToken(models.Model):
    management_user = models.ForeignKey(management, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Token valid for 1 hour
        return timezone.now() < self.created_at + timedelta(hours=1)
