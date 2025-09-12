from django.db import models
from driver.models import Bus
import uuid
from django.utils import timezone
from datetime import timedelta

class student_details(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    password=models.CharField(max_length=128)
    phone_no=models.CharField(max_length=10)
    stud_class=models.CharField(max_length=50)
    branch=models.CharField(max_length=50)
    accommodation_type=models.CharField(default='Day Scholar',max_length=50)
    bus=models.ForeignKey(Bus,on_delete=models.CASCADE,null=True,blank=True)
    parent = models.ForeignKey('parent.parent', on_delete=models.CASCADE, null=True, blank=True)
    is_boarded = models.BooleanField(default=False)
    boarding_time = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from django.contrib.auth.hashers import make_password
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class registery(models.Model):
    FN=models.CharField(max_length=20)
    AN=models.CharField(max_length=20)
    student_id=models.ForeignKey(student_details,on_delete=models.CASCADE)

class student_complaints(models.Model):
    student_id=models.IntegerField()
    complaint=models.TextField()
    bus=models.CharField(max_length=50)
    complaint_by=models.CharField(default='Student',max_length=10,blank=True)
    date=models.DateTimeField(auto_now=True)
    status=models.CharField(max_length=50,blank=True)
    action_taken=models.TextField(blank=True)

class hosteler_reg(models.Model):
    student_id=models.ForeignKey(student_details,null=True,blank=True,on_delete=models.CASCADE)
    pickup_time=models.CharField(max_length=50)
    pickup_point=models.CharField(max_length=50)
    bus=models.ForeignKey(Bus,on_delete=models.CASCADE)
    status=models.CharField(max_length=50,blank=True)
    time=models.DateTimeField(auto_now=True)

class PasswordResetToken(models.Model):
    student = models.ForeignKey(student_details, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Token valid for 1 hour
        return timezone.now() < self.created_at + timedelta(hours=1)
