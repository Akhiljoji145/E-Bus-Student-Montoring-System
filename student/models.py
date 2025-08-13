from django.db import models

class student_details(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    password=models.CharField(max_length=70,blank=True)
    phone_no=models.CharField(max_length=10)
    stud_class=models.CharField(max_length=50)
    branch=models.CharField(max_length=50)
    accommodation_type=models.CharField(default='Day Scholar',max_length=50)
class registery(models.Model):
    FN=models.CharField(max_length=20)
    AN=models.CharField(max_length=20)
    student_id=models.IntegerField()
class student_complaints(models.Model):
    student_id=models.IntegerField()
    complaint=models.TextField()
    bus=models.IntegerField()
    complaint_by=models.CharField(default='Student',max_length=10,blank=True)
    date=models.DateTimeField(auto_now=True)
    status=models.CharField(max_length=50,blank=True)
    action_taken=models.TextField(blank=True)
class hosteler_reg(models.Model):
    student_name=models.CharField(max_length=50)
    pickup_point=models.CharField(max_length=50)
    bus_id=models.CharField(max_length=50)
    status=models.CharField(max_length=50,blank=True)