from django.db import models

# Create your models here.
class report(models.Model):
    stud_id=models.CharField(max_length=50)
    bus_id=models.IntegerField()
    description=models.TextField()
    time=models.DateField(auto_now=True)
    teacher_id=models.IntegerField()
class teacher(models.Model):
    teacher_name=models.CharField(max_length=50)
    email=models.models.EmailField(max_length=254)
    password=models.CharField(max_length=50,blank=True)
    class_no=models.IntegerField()
    branch=models.CharField(max_length=50)
    sem=models.CharField(max_length=50)

