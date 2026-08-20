from django.urls import path

from .operations_views import (
    CsrfTokenView,
    CurrentUserView,
    DestinationDetailView,
    DestinationListCreateView,
    LoginView,
    LogoutView,
    ProductDetailView,
    ProductHeroImageView,
    ProductImageDetailView,
    ProductImageListCreateView,
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
    path("products/<int:pk>/hero-image", ProductHeroImageView.as_view(), name="operations-product-hero-image"),
    path("products/<int:pk>/images", ProductImageListCreateView.as_view(), name="operations-product-images"),
    path("products/<int:pk>/images/<int:image_id>", ProductImageDetailView.as_view(), name="operations-product-image-detail"),
    path("vessel-options", VesselOptionsView.as_view(), name="operations-vessel-options"),
]
