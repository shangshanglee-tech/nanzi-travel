from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase, override_settings

from catalog.storage import AliyunMediaStorage, build_media_storage


class MediaStorageTests(SimpleTestCase):
    @override_settings(USE_OSS=False)
    def test_local_mode_uses_filesystem_storage(self):
        self.assertIsInstance(build_media_storage(), FileSystemStorage)

    @override_settings(
        USE_OSS=True,
        OSS_ACCESS_KEY_ID="access-id",
        OSS_SECRET_ACCESS_KEY="secret",
        OSS_BUCKET_NAME="nanzi-media",
        OSS_ENDPOINT_URL="https://s3.oss-cn-chengdu.aliyuncs.com",
        OSS_CUSTOM_DOMAIN="media.nanzitravel.com",
    )
    def test_oss_mode_uses_public_read_urls_and_backend_only_credentials(self):
        storage = build_media_storage()

        self.assertIsInstance(storage, AliyunMediaStorage)
        self.assertEqual(storage.bucket_name, "nanzi-media")
        self.assertEqual(storage.custom_domain, "media.nanzitravel.com")
        self.assertFalse(storage.querystring_auth)
        self.assertEqual(storage.default_acl, "public-read")
        self.assertEqual(storage.signature_version, "s3")
        self.assertEqual(storage.addressing_style, "virtual")
