from django.db import models

# Create your models here.
class Bus(models.Model):
    bus_no=models.IntegerField()
    driver_name=models.CharField(max_length=50)
    bus_starting_point=models.CharField(max_length=50)
    bus_stoping_point=models.CharField(max_length=50)
    bus_plate=models.CharField(max_length=50)
    bus_change=models.CharField(max_length=50)
    