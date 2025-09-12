from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from driver.models import Busdriver

class Command(BaseCommand):
    help = 'Hash plain text passwords for Busdriver model'

    def handle(self, *args, **options):
        drivers = Busdriver.objects.all()
        for driver in drivers:
            if driver.password and not driver.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
                driver.password = make_password(driver.password)
                driver.save()
                self.stdout.write(f'Hashed password for driver: {driver.bus_driver}')
        self.stdout.write('Password hashing completed.')
