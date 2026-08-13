from django.urls import path

from .views import HomeView, ProductDetailView, ProductListView, SiteView


urlpatterns = [
    path("site", SiteView.as_view(), name="site"),
    path("home", HomeView.as_view(), name="home"),
    path("products", ProductListView.as_view(), name="product-list"),
    path("products/<slug:slug>", ProductDetailView.as_view(), name="product-detail"),
]

