import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slangspot.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

print("=========================================")
print("Testing Cloudinary upload...")
print("Current default storage class:", type(default_storage).__name__)
print("Current default storage module:", default_storage.__module__)

try:
    path = default_storage.save('test_cloudinary_upload.txt', ContentFile(b'test content'))
    print("Successfully saved to:", path)
    url = default_storage.url(path)
    print("File URL:", url)
except Exception as e:
    print("Error uploading to Cloudinary:", e)
print("=========================================")
