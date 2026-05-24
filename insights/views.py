import json
import os
from datetime import datetime, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import LoginForm, RegisterForm
from .models import CongestionLog, RoadCondition, TollCollection, Trip
from .road_conditions import get_road_condition_factor, report_condition, resolve_condition
from .routing import geocode, get_routes
from .toll_calc import compute_toll
from .traffic import get_traffic_info


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user:
                login(request, user)
                return redirect("/")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            login(request, user)
            return redirect("/")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/login/")


@login_required
@ensure_csrf_cookie
def map_view(request):
    return render(request, "index.html")


@login_required
def dashboard_view(request):
    trips = Trip.objects.filter(user=request.user)
    total_trips = trips.count()
    total_toll = trips.aggregate(Sum("toll_amount"))["toll_amount__sum"] or 0
    trips_json = json.dumps(
        list(
            trips.values(
                "id", "origin_name", "dest_name", "distance_km", "toll_amount", "vehicle_type", "created_at"
            )[:50]
        ),
        default=str,
    )
    vehicle_data = list(trips.values("vehicle_type").annotate(count=Count("id"), total=Sum("toll_amount")))
    my_reports = RoadCondition.objects.filter(reported_by=request.user)[:10]
    recent_conditions = RoadCondition.objects.filter(status__in=["reported", "verified"])[:10]
    return render(
        request,
        "dashboard.html",
        {
            "total_trips": total_trips,
            "total_toll": round(total_toll, 2),
            "recent_trips": trips[:10],
            "trips_json": trips_json,
            "vehicle_data": vehicle_data,
            "my_reports": my_reports,
            "recent_conditions": recent_conditions,
        },
    )


@staff_member_required
def admin_dashboard_view(request):
    all_trips = Trip.objects.all()
    total_revenue = all_trips.aggregate(Sum("toll_amount"))["toll_amount__sum"] or 0
    total_trips_count = all_trips.count()
    today = datetime.now().date()
    today_revenue = (
        all_trips.filter(created_at__date=today).aggregate(Sum("toll_amount"))["toll_amount__sum"] or 0
    )
    week_revenue = (
        all_trips.filter(created_at__gte=today - timedelta(days=7))
        .aggregate(Sum("toll_amount"))["toll_amount__sum"]
        or 0
    )
    vehicle_data = list(all_trips.values("vehicle_type").annotate(count=Count("id"), total=Sum("toll_amount")))

    top_users = (
        User.objects.annotate(trip_count=Count("trips"), total_spent=Sum("trips__toll_amount"))
        .filter(trip_count__gt=0)
        .order_by("-trip_count")[:10]
    )

    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')
    with open(config_path) as f:
        config_data = json.load(f)

    road_conditions = RoadCondition.objects.all()[:20]
    rc_stats = {
        "total": RoadCondition.objects.count(),
        "open": RoadCondition.objects.filter(status__in=["reported", "verified"]).count(),
        "resolved": RoadCondition.objects.filter(status="resolved").count(),
    }

    return render(
        request,
        "admin_dashboard.html",
        {
            "total_revenue": round(total_revenue, 2),
            "total_trips": total_trips_count,
            "today_revenue": round(today_revenue, 2),
            "week_revenue": round(week_revenue, 2),
            "vehicle_data": vehicle_data,
            "recent_trips": all_trips.select_related("user")[:20],
            "top_users": top_users,
            "config": config_data,
            "road_conditions": road_conditions,
            "rc_stats": rc_stats,
        },
    )


@login_required
def api_geocode(request):
    q = request.GET.get("q", "")
    if not q:
        return JsonResponse({"error": "Missing query"}, status=400)
    try:
        results = geocode(q)
        data = [
            {"lat": float(r["lat"]), "lng": float(r["lon"]), "display_name": r["display_name"]}
            for r in results
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def api_route(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        body = json.loads(request.body)
        origin_lat = body["origin_lat"]
        origin_lng = body["origin_lng"]
        dest_lat = body["dest_lat"]
        dest_lng = body["dest_lng"]
        origin_name = body.get("origin_name", "")
        dest_name = body.get("dest_name", "")
        vehicle = body.get("vehicle", "car")

        osrm_data = get_routes(origin_lat, origin_lng, dest_lat, dest_lng)
        congestion_logs = list(CongestionLog.objects.all().values("location_name"))
        traffic = get_traffic_info(origin_name, dest_name, congestion_logs)

        from .road_conditions import get_road_condition_factor
        road_factor = get_road_condition_factor(
            origin_lat, origin_lng, dest_lat, dest_lng
        )
        combined_factor = max(round(traffic["factor"] + road_factor, 2), 0.5)

        routes = []
        for i, route in enumerate(osrm_data.get("routes", [])):
            distance_km = round(route["legs"][0]["distance"] / 1000, 1)
            duration_sec = route["legs"][0]["duration"]
            adjusted_duration = int(duration_sec * combined_factor)
            toll, pricing_model = compute_toll(distance_km, vehicle)

            routes.append(
                {
                    "index": i,
                    "recommended": i == 0,
                    "distance_km": distance_km,
                    "duration_sec": duration_sec,
                    "adjusted_duration_sec": adjusted_duration,
                    "adjusted_duration_min": round(adjusted_duration / 60, 1),
                    "toll": toll,
                    "pricing_model": pricing_model,
                    "traffic": traffic,
                    "road_condition_factor": road_factor,
                    "geometry": route["geometry"],
                }
            )

        if routes:
            r = routes[0]
            trip = Trip.objects.create(
                user=request.user,
                origin_name=origin_name,
                dest_name=dest_name,
                origin_lat=origin_lat,
                origin_lng=origin_lng,
                dest_lat=dest_lat,
                dest_lng=dest_lng,
                distance_km=r["distance_km"],
                duration_sec=r["adjusted_duration_sec"],
                route_geometry=r["geometry"],
                vehicle_type=vehicle,
                toll_amount=r["toll"],
                pricing_model=r["pricing_model"],
                congestion_level=r["traffic"]["level"],
            )
            multiplier_map = {"bike": 0.5, "car": 1.0, "bus": 1.5, "truck": 2.0, "ambulance": 0.0}
            multiplier = multiplier_map.get(vehicle, 1.0)
            if r["toll"] and multiplier > 0:
                base_toll = round(r["toll"] / multiplier, 2)
                TollCollection.objects.create(
                    trip=trip,
                    base_toll=base_toll,
                    multiplier=multiplier,
                    total_toll=r["toll"],
                    pricing_model=r["pricing_model"],
                )

            for name, lat, lng in [(origin_name, origin_lat, origin_lng), (dest_name, dest_lat, dest_lng)]:
                CongestionLog.objects.create(
                    location_name=name,
                    lat=lat,
                    lng=lng,
                    level=traffic["factor"],
                    source="query",
                )

        return JsonResponse({"routes": routes, "traffic": traffic})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def api_trips(request):
    trips = Trip.objects.filter(user=request.user)
    data = list(
        trips.values("id", "origin_name", "dest_name", "distance_km", "toll_amount", "vehicle_type", "created_at")[:100]
    )
    return JsonResponse(data, safe=False)


@staff_member_required
def api_admin_stats(request):
    all_trips = Trip.objects.all()
    total = all_trips.aggregate(Sum("toll_amount"))["toll_amount__sum"] or 0
    count = all_trips.count()
    avg_toll = all_trips.aggregate(Avg("toll_amount"))["toll_amount__avg"] or 0

    today = datetime.now().date()
    daily_data = []
    for i in range(30):
        day = today - timedelta(days=29 - i)
        day_total = (
            all_trips.filter(created_at__date=day).aggregate(Sum("toll_amount"))["toll_amount__sum"] or 0
        )
        daily_data.append({"date": day.isoformat(), "revenue": float(day_total)})

    vehicle_data = list(all_trips.values("vehicle_type").annotate(count=Count("id"), total=Sum("toll_amount")))

    return JsonResponse(
        {
            "total_revenue": float(total),
            "total_trips": count,
            "avg_toll": float(avg_toll),
            "daily_revenue": daily_data,
            "vehicle_breakdown": vehicle_data,
        }
    )


@login_required
def api_road_conditions(request):
    qs = RoadCondition.objects.all()
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    radius = request.GET.get("radius")
    if lat and lng and radius:
        try:
            clat, clng, r = float(lat), float(lng), float(radius)
            from .road_conditions import _haversine
            ids = []
            for rc in qs:
                if _haversine(clat, clng, rc.lat, rc.lng) <= r:
                    ids.append(rc.id)
            qs = qs.filter(id__in=ids)
        except ValueError:
            pass
    data = list(qs.values(
        "id", "road_name", "lat", "lng", "condition_type", "severity",
        "description", "report_count", "status", "created_at"
    ))
    return JsonResponse(data, safe=False)


@login_required
def api_report_road_condition(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        body = json.loads(request.body)
        rc, created = report_condition(
            road_name=body["road_name"],
            lat=float(body["lat"]),
            lng=float(body["lng"]),
            condition_type=body["condition_type"],
            severity=body.get("severity", "medium"),
            description=body.get("description", ""),
            user=request.user,
        )
        return JsonResponse({
            "id": rc.id,
            "status": rc.status,
            "report_count": rc.report_count,
            "created": created,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@staff_member_required
def api_resolve_road_condition(request, condition_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    rc = resolve_condition(condition_id)
    if rc:
        return JsonResponse({"id": rc.id, "status": rc.status})
    return JsonResponse({"error": "Not found or already resolved"}, status=404)


@staff_member_required
def api_road_condition_stats(request):
    total = RoadCondition.objects.count()
    open_count = RoadCondition.objects.filter(status__in=["reported", "verified"]).count()
    resolved_count = RoadCondition.objects.filter(status="resolved").count()
    type_breakdown = list(
        RoadCondition.objects.values("condition_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    severity_breakdown = list(
        RoadCondition.objects.values("severity")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return JsonResponse({
        "total": total,
        "open": open_count,
        "resolved": resolved_count,
        "type_breakdown": type_breakdown,
        "severity_breakdown": severity_breakdown,
    })
