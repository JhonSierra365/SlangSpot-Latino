import os
import django
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slangspot.settings')
django.setup()

from django.conf import settings
import cloudinary
import cloudinary.uploader
from cloudinary_storage.storage import MediaCloudinaryStorage

print("--- DIAGNOSTIC ---")
print("Settings default backend:", settings.DEFAULT_FILE_STORAGE)
print("CLOUDINARY_STORAGE dict:", getattr(settings, 'CLOUDINARY_STORAGE', None))

print("\n--- Testing with direct config vs environment ---")
# Reset cloudinary config to simulate Railway where CLOUDINARY_URL might exist
os.environ['CLOUDINARY_URL'] = "cloudinary://123456789012345:abcdefghijklmnopqrstuvwxyz12@dummy_cloud_for_test"

# Let's see what happens to cloudinary.config()
print("Cloudinary config after dummy url:", cloudinary.config().cloud_name)
