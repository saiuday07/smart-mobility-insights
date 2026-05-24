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
    path("api/road-conditions/", views.api_road_conditions, name="api_road_conditions"),
    path("api/road-conditions/report/", views.api_report_road_condition, name="api_report_road_condition"),
    path("api/road-conditions/<int:condition_id>/resolve/", views.api_resolve_road_condition, name="api_resolve_road_condition"),
    path("api/road-conditions/stats/", views.api_road_condition_stats, name="api_road_condition_stats"),
]
