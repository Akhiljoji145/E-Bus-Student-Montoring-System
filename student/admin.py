from django.contrib import admin
from .models import student_details,student_complaints,hosteler_reg,registery, PasswordResetToken
# Register your models here.
admin.site.register(student_details)
admin.site.register(student_complaints)
admin.site.register(hosteler_reg)
admin.site.register(registery)
admin.site.register(PasswordResetToken)
