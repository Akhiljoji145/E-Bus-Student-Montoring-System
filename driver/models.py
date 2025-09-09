from django.db import models

# Create your models here.
class Bus(models.Model):
    bus_no=models.IntegerField()
    bus_starting_point=models.CharField(max_length=50)
    bus_plate=models.CharField(max_length=50)
    bus_photo=models.ImageField(upload_to='bus',blank=True)
    def __str__(self):
        return str(self.bus_no)
    
class Busdriver(models.Model):
    bus_driver=models.CharField(max_length=50)
    email=models.EmailField()
    password=models.CharField(max_length=50,blank=True)
    ph_no=models.CharField(max_length=50)
    bus_id=models.ForeignKey(Bus,on_delete=models.CASCADE)
    status=models.CharField(default='permanent',max_length=50)
    bus_photo=models.ImageField(upload_to='change bus',blank=True)
    def __str__(self):
        return self.bus_driver
