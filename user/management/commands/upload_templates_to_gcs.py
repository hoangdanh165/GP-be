from django.core.management.base import BaseCommand
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
import os

class Command(BaseCommand):
    help = 'Uploads all valid templates to Google Cloud Storage'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Start uploading templates to GCS...'))

        storage = GoogleCloudStorage()
        template_dirs = set()

        project_template_dir = os.path.join(settings.BASE_DIR, 'templates')
        if os.path.exists(project_template_dir):
            template_dirs.add(project_template_dir)

        for app in settings.INSTALLED_APPS:
            try:
                module = __import__(app)
                app_path = os.path.dirname(module.__file__)
                app_template_dir = os.path.join(app_path, 'templates')

                if os.path.exists(app_template_dir):
                    template_dirs.add(app_template_dir)
            except Exception:
                continue

        for template_dir in template_dirs:
            for root, _, files in os.walk(template_dir):
                if any(x in root for x in ['.venv', 'site-packages']):
                    continue

                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, settings.BASE_DIR) 

                    # Upload file
                    with open(file_path, 'rb') as f:
                        storage.save(f"templates/{relative_path}", f)

                    self.stdout.write(self.style.SUCCESS(f'Uploaded: {relative_path}'))

        self.stdout.write(self.style.SUCCESS('Upload templates successfully!'))
