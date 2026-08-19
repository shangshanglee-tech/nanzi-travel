from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0012_alter_vesseldeckplan_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vesseldeckplan",
            name="description",
            field=models.TextField(blank=True, verbose_name="正文"),
        ),
    ]
