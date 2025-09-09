from django.db import models

# Create your models here.

class teacher(models.Model):
    teacher_name=models.CharField(max_length=50)
    email=models.EmailField(max_length=254)
    password=models.CharField(max_length=50,blank=True)
    class_no=models.IntegerField()
    branch=models.CharField(max_length=50)
    sem=models.CharField(max_length=50)

class MissingStudentAlert(models.Model):
    student_name = models.CharField(max_length=100)
    bus_route = models.CharField(max_length=100)
    last_seen = models.TextField()
    parent_contact = models.CharField(max_length=20)
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
