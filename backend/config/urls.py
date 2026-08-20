from django.contrib import admin
from django.urls import include, path, re_path

from catalog.views import healthz, operations_console


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/admin/v1/", include("catalog.operations_urls")),
    path("api/v1/", include("catalog.urls")),
    path("healthz", healthz),
    path("", operations_console, name="operations-console"),
    re_path(r"^(?:products|destinations|vessels)/?$", operations_console),
]
