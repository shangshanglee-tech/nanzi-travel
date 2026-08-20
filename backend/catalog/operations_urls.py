from django.urls import path

from .operations_views import (
    CsrfTokenView,
    CurrentUserView,
    DestinationDetailView,
    DestinationListCreateView,
    LoginView,
    LogoutView,
    ProductDetailView,
    ProductListCreateView,
    VesselOptionsView,
)


urlpatterns = [
    path("auth/csrf", CsrfTokenView.as_view(), name="operations-csrf"),
    path("auth/login", LoginView.as_view(), name="operations-login"),
    path("auth/logout", LogoutView.as_view(), name="operations-logout"),
    path("auth/me", CurrentUserView.as_view(), name="operations-me"),
    path("destinations", DestinationListCreateView.as_view(), name="operations-destinations"),
    path("destinations/<int:pk>", DestinationDetailView.as_view(), name="operations-destination-detail"),
    path("products", ProductListCreateView.as_view(), name="operations-products"),
    path("products/<int:pk>", ProductDetailView.as_view(), name="operations-product-detail"),
    path("vessel-options", VesselOptionsView.as_view(), name="operations-vessel-options"),
]
