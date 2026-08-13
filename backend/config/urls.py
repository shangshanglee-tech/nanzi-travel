from django.contrib import admin
from django.urls import include, path

from catalog.views import healthz


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("catalog.urls")),
    path("healthz", healthz),
]
