import json
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
from .models import CongestionLog, TollCollection, Trip
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
    return render(
        request,
        "dashboard.html",
        {
            "total_trips": total_trips,
            "total_toll": round(total_toll, 2),
            "recent_trips": trips[:10],
            "trips_json": trips_json,
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

        routes = []
        for i, route in enumerate(osrm_data.get("routes", [])):
            distance_km = round(route["legs"][0]["distance"] / 1000, 1)
            duration_sec = route["legs"][0]["duration"]
            adjusted_duration = int(duration_sec * traffic["factor"])
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
            if r["toll"]:
                multiplier = {"bike": 0.5, "car": 1.0, "bus": 1.5, "truck": 2.0, "ambulance": 0.0}.get(
                    vehicle, 1.0
                )
                base_toll = round(r["toll"] / multiplier, 2) if multiplier > 0 else r["toll"]
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
