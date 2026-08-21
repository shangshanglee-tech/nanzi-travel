# Generated manually to align the operations label with the activity content field.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0015_activity_content_and_product_activities")]

    operations = [
        migrations.AlterField(
            model_name="activity",
            name="content",
            field=models.TextField("活动介绍", blank=True),
        ),
    ]
