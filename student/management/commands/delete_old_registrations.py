from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from student.models import hosteler_reg

class Command(BaseCommand):
    help = 'Delete bus registrations older than 24 hours'

    def handle(self, *args, **options):
        # Calculate the time 24 hours ago
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        # Delete registrations older than 24 hours
        deleted_count, _ = hosteler_reg.objects.filter(time__lt=twenty_four_hours_ago).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} old registrations')
        )
