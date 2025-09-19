from django.contrib import admin
from .models import Bus, Busdriver, StudentBoarding, BusMessage

# Register your models here.
admin.site.register(Bus)
admin.site.register(Busdriver)
admin.site.register(StudentBoarding)

admin.site.register(BusMessage)
