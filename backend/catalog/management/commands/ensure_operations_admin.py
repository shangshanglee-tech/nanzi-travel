import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "创建或更新唯一的 React 运营后台超级管理员。"

    def handle(self, *args, **options):
        password = os.environ.get("OPERATIONS_ADMIN_PASSWORD")
        if not password:
            raise CommandError("必须设置 OPERATIONS_ADMIN_PASSWORD 才能创建运营后台管理员。")

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(username="admin")
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "创建" if created else "更新"
        self.stdout.write(self.style.SUCCESS(f"已{action}运营后台管理员：admin"))
