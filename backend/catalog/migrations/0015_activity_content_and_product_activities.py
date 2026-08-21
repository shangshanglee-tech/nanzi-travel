# Generated manually for the operations console activity editor.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0014_activity_activityimage")]

    operations = [
        migrations.RenameField(model_name="activity", old_name="explanation", new_name="content"),
        migrations.RemoveField(model_name="activity", name="summary"),
    ]
