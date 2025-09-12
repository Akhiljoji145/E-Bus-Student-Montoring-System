from django.contrib import admin
from .models import teacher, MissingStudentAlert, StudentStatusOverride, PasswordResetToken

# Register your models here.
admin.site.register(teacher)
admin.site.register(MissingStudentAlert)
admin.site.register(StudentStatusOverride)
admin.site.register(PasswordResetToken)
