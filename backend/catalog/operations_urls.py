from django.urls import path

from .operations_views import CsrfTokenView, CurrentUserView, LoginView, LogoutView


urlpatterns = [
    path("auth/csrf", CsrfTokenView.as_view(), name="operations-csrf"),
    path("auth/login", LoginView.as_view(), name="operations-login"),
    path("auth/logout", LogoutView.as_view(), name="operations-logout"),
    path("auth/me", CurrentUserView.as_view(), name="operations-me"),
]
