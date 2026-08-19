from django.core.validators import FileExtensionValidator
from django.db import migrations, models

import catalog.storage


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0011_vessel_page_block_images"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vesseldeckplan",
            name="image",
            field=models.FileField(
                storage=catalog.storage.build_media_storage,
                upload_to="vessels/deck-plans/",
                validators=[FileExtensionValidator(allowed_extensions=["svg", "png", "jpg", "jpeg", "webp"])],
                verbose_name="甲板示意图",
            ),
        ),
    ]
