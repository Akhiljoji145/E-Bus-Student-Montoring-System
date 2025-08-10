from django.db import models

# Create your models here.
class report(models.Model):
    stud_name=models.CharField(max_length=50)
    bus_id=models.IntegerField()
    description=models.TextField()
    time=models.DateField(auto_now=True)

    