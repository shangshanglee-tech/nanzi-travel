import json
import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase


class OperationsAuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            password="admin123456",
        )

    def test_superuser_login_creates_management_session(self):
        response = self.client.post(
            "/api/admin/v1/auth/login",
            data=json.dumps({"username": "admin", "password": "admin123456"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"username": "admin"})

        me_response = self.client.get("/api/admin/v1/auth/me")
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json(), {"username": "admin"})

    def test_login_requires_a_csrf_token_for_browser_requests(self):
        browser_client = Client(enforce_csrf_checks=True)
        payload = json.dumps({"username": "admin", "password": "admin123456"})

        self.assertEqual(
            browser_client.post(
                "/api/admin/v1/auth/login",
                data=payload,
                content_type="application/json",
            ).status_code,
            403,
        )

        csrf_response = browser_client.get("/api/admin/v1/auth/csrf")
        token = csrf_response.json()["csrfToken"]
        response = browser_client.post(
            "/api/admin/v1/auth/login",
            data=payload,
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)

    def test_management_api_requires_an_admin_session(self):
        response = self.client.get("/api/admin/v1/auth/me")

        self.assertIn(response.status_code, {401, 403})

    def test_console_shell_exposes_a_csrf_token(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="csrf-token"')
        self.assertIn("csrftoken", response.cookies)

    def test_console_shell_versions_static_assets(self):
        response = self.client.get("/")

        self.assertContains(response, "operations.js?v=")
        self.assertContains(response, "operations.css?v=")

    def test_console_content_routes_use_the_single_page_shell(self):
        for route in ("/products", "/destinations", "/vessels"):
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'id="operations-console"')

    def test_logout_clears_management_session(self):
        self.client.force_login(self.user)

        response = self.client.post("/api/admin/v1/auth/logout")
        self.assertEqual(response.status_code, 204)
        self.assertIn(self.client.get("/api/admin/v1/auth/me").status_code, {401, 403})


class EnsureOperationsAdminCommandTests(TestCase):
    def test_command_requires_password_from_environment(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CommandError):
                call_command("ensure_operations_admin")

    def test_command_creates_the_single_operations_administrator(self):
        with patch.dict(os.environ, {"OPERATIONS_ADMIN_PASSWORD": "admin123456"}, clear=True):
            call_command("ensure_operations_admin", stdout=StringIO())

        user = get_user_model().objects.get(username="admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password("admin123456"))
