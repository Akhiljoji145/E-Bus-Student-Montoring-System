from django.db import models
from django.contrib.auth.hashers import make_password
from driver.models import Bus
import uuid
from django.utils import timezone
from datetime import timedelta

class parent(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    phone_no = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class PasswordResetToken(models.Model):
    parent_user = models.ForeignKey(parent, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Token valid for 1 hour
        return timezone.now() < self.created_at + timedelta(hours=1)

class Complaint(models.Model):
    COMPLAINT_TYPES = [
        ('Late Pickup/Drop-off', 'Late Pickup/Drop-off'),
        ('Student Not Reached Home', 'Student Not Reached Home'),
        ('Overcrowding', 'Overcrowding'),
        ('Driver Behavior', 'Driver Behavior'),
        ('Bus Condition', 'Bus Condition'),
        ('Safety Concern', 'Safety Concern'),
        ('Route Issue', 'Route Issue'),
        ('Other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    parent = models.ForeignKey(parent, on_delete=models.CASCADE)
    complaint_type = models.CharField(max_length=50, choices=COMPLAINT_TYPES)
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint_type} - {self.parent.name}"
