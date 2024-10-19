import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Backup Odoo database'

    def handle(self, *args, **options):
        script_path = settings.ODOO_BACKUP_SCRIPT
        
        if not os.path.exists(script_path):
            self.stdout.write(self.style.ERROR(f'Backup script not found at {script_path}'))
            return

        try:
            # Use sudo to run the script as root
            result = subprocess.run(['sudo', 'bash', script_path], check=True, capture_output=True, text=True)
            self.stdout.write(self.style.SUCCESS(result.stdout))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Backup failed: {e.stderr}'))
