from django.contrib import admin
from .models import admin_main, PasswordResetToken

# Register your models here.
admin.site.register(admin_main)
admin.site.register(PasswordResetToken)
