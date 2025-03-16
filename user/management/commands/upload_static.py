import os
from django.core.management.base import BaseCommand
import boto3
from django.conf import settings

class Command(BaseCommand):
    help = 'Upload Django static files to S3'

    def handle(self, *args, **kwargs):
        # Cấu hình kết nối S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        folder_name = 'static'  # Thư mục trên S3
        local_static_dir = settings.STATIC_ROOT  # Django static root

        if not os.path.exists(local_static_dir):
            self.stdout.write(self.style.ERROR(f'Error: Static root {local_static_dir} does not exist!'))
            return

        # Duyệt qua static files và upload lên S3
        for root, dirs, files in os.walk(local_static_dir):
            for file in files:
                file_path = os.path.join(root, file)
                s3_file_path = os.path.relpath(file_path, local_static_dir)  # Đường dẫn trên S3
                s3_client.upload_file(file_path, bucket_name, f'{folder_name}/{s3_file_path}')
                self.stdout.write(self.style.SUCCESS(f'Successfully uploaded {file_path} to {folder_name}/{s3_file_path}'))
