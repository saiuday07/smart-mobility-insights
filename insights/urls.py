from django.urls import path
from . import views

urlpatterns = [
    path("", views.map_view, name="map"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("api/geocode/", views.api_geocode, name="api_geocode"),
    path("api/route/", views.api_route, name="api_route"),
    path("api/trips/", views.api_trips, name="api_trips"),
    path("api/admin/stats/", views.api_admin_stats, name="api_admin_stats"),
]
