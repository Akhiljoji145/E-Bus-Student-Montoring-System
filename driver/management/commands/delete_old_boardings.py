from django.core.management.base import BaseCommand
from driver.models import StudentBoarding
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete StudentBoarding records older than today'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        deleted_count, _ = StudentBoarding.objects.filter(date__lt=today).delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} old StudentBoarding records.'))
