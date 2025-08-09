from django.db import models

class student_details(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    password=models.CharField(max_length=70)
    phone_no=models.IntegerField()
    key=models.CharField(max_length=100)