from django.contrib import admin
from .models import management, PasswordResetToken

# Register your models here.
admin.site.register(management)
admin.site.register(PasswordResetToken)
