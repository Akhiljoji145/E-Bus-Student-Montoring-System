from django.db import models
from django.contrib.auth.hashers import make_password
import uuid
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class teacher(models.Model):
    teacher_name=models.CharField(max_length=50)
    email=models.EmailField(max_length=254)
    password=models.CharField(max_length=128,blank=True)
    class_no=models.CharField(max_length=10)
    branch=models.CharField(max_length=50)
    sem=models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class MissingStudentAlert(models.Model):
    student_name = models.CharField(max_length=100)
    bus_route = models.CharField(max_length=100)
    last_seen = models.TextField()
    parent_contact = models.CharField(max_length=100)
    reported_by = models.ForeignKey(teacher, on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')  # active, resolved

    def __str__(self):
        return f"Missing: {self.student_name} - {self.bus_route}"

class StudentStatusOverride(models.Model):
    student_name = models.CharField(max_length=100)
    bus_route = models.CharField(max_length=100)
    action = models.CharField(max_length=20)  # boarded, departed, absent
    applied_by = models.ForeignKey(teacher, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Override: {self.student_name} - {self.action}"

class PasswordResetToken(models.Model):
    teacher_user = models.ForeignKey(teacher, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Token valid for 1 hour
        return timezone.now() < self.created_at + timedelta(hours=1)
