from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3 import S3Storage


class AliyunMediaStorage(S3Storage):
    location = "media"
    file_overwrite = False
    default_acl = "public-read"
    querystring_auth = False

    def __init__(self, **settings_overrides):
        settings_overrides.setdefault("access_key", settings.OSS_ACCESS_KEY_ID)
        settings_overrides.setdefault("secret_key", settings.OSS_SECRET_ACCESS_KEY)
        settings_overrides.setdefault("bucket_name", settings.OSS_BUCKET_NAME)
        settings_overrides.setdefault("endpoint_url", settings.OSS_ENDPOINT_URL)
        settings_overrides.setdefault("custom_domain", settings.OSS_CUSTOM_DOMAIN)
        settings_overrides.setdefault("region_name", None)
        super().__init__(**settings_overrides)


def build_media_storage():
    if settings.USE_OSS:
        return AliyunMediaStorage()
    return FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)

