from django.urls import path

from .views import HomeView, ProductDetailView, ProductListView, SiteView, VesselDetailView, VesselIconView, VesselListView


urlpatterns = [
    path("site", SiteView.as_view(), name="site"),
    path("home", HomeView.as_view(), name="home"),
    path("products", ProductListView.as_view(), name="product-list"),
    path("products/<slug:slug>", ProductDetailView.as_view(), name="product-detail"),
    path("vessels", VesselListView.as_view(), name="vessel-list"),
    path("vessel-icons/<slug:icon>.svg", VesselIconView.as_view(), name="vessel-icon"),
    path("vessels/<slug:slug>", VesselDetailView.as_view(), name="vessel-detail"),
]
