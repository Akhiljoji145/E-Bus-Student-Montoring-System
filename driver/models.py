from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Create your models here.
class Bus(models.Model):
    bus_no=models.IntegerField()
    bus_starting_point=models.CharField(max_length=50)
    bus_plate=models.CharField(max_length=50)
    bus_photo=models.ImageField(upload_to='bus',blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    def __str__(self):
        return str(self.bus_no)
    
class Busdriver(models.Model):
    bus_driver=models.CharField(max_length=50)
    email=models.EmailField()
    password=models.CharField(max_length=128,blank=True)
    ph_no=models.CharField(max_length=50)
    bus_id=models.OneToOneField(Bus,on_delete=models.CASCADE)
    status=models.CharField(default='permanent',max_length=50)
    bus_photo=models.ImageField(upload_to='change bus',blank=True)
    def __str__(self):
        return self.bus_driver

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class StudentBoarding(models.Model):
    student = models.ForeignKey('student.student_details', on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(null=True, blank=True)
    morning_scan = models.BooleanField(default=False)
    morning_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    morning_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    evening_scan = models.BooleanField(default=False)
    evening_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    evening_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('boarded', 'Boarded'), ('not_boarded', 'Not Boarded'), ('departed', 'Departed')], default='not_boarded')
    alert_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = [['student', 'bus', 'date']]

    def __str__(self):
        return f"{self.student.name} - {self.status} - Morning Scan: {self.morning_scan} - Evening Scan: {self.evening_scan}"


class BusMessage(models.Model):
    driver = models.ForeignKey(Busdriver, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    audience = models.CharField(max_length=20, choices=[('all_parents', 'All Parents'), ('school_admin', 'School Admin'), ('specific_parent', 'Specific Parent')])
    parent_contact = models.CharField(max_length=100, blank=True)
    sent_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.subject
