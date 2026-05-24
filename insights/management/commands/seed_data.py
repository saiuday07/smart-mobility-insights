import json
import os
import random
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from insights.models import CongestionLog, RoadCondition, TollCollection, Trip

VEHICLES = ["car", "bike", "bus", "truck", "ambulance"]

ROUTES = [
    ("Hitech City, Hyderabad", "Gachibowli, Hyderabad", 17.4435, 78.3772, 17.4481, 78.3532),
    ("Jubilee Hills, Hyderabad", "Madhapur, Hyderabad", 17.4318, 78.4026, 17.4489, 78.3891),
    ("Hyderabad Airport", "HiTech City, Hyderabad", 17.2403, 78.4294, 17.4435, 78.3772),
    ("Secunderabad", "Ameerpet, Hyderabad", 17.4399, 78.4985, 17.4375, 78.4483),
    ("Kukatpally, Hyderabad", "Banjara Hills, Hyderabad", 17.4898, 78.4084, 17.4176, 78.4350),
    ("Miyapur, Hyderabad", "Kondapur, Hyderabad", 17.4974, 78.3673, 17.4699, 78.3669),
    ("LB Nagar, Hyderabad", "Dilsukhnagar, Hyderabad", 17.3476, 78.5527, 17.3699, 78.5257),
    ("Koti, Hyderabad", "Abids, Hyderabad", 17.3860, 78.4744, 17.3865, 78.4725),
    ("Patancheru, Hyderabad", "BHEL, Hyderabad", 17.5308, 78.2647, 17.4399, 78.2907),
    ("Uppal, Hyderabad", "Ramoji Film City", 17.4053, 78.5588, 17.3294, 78.6833),
    ("Nampally, Hyderabad", "Charminar", 17.3748, 78.4743, 17.3617, 78.4746),
    ("Himayatnagar, Hyderabad", "Somajiguda, Hyderabad", 17.3987, 78.4852, 17.4181, 78.4538),
    ("Toli Chowki, Hyderabad", "Mehdipatnam, Hyderabad", 17.3903, 78.4128, 17.3976, 78.4373),
    ("Shamshabad, Hyderabad", "Rajiv Gandhi International Airport", 17.2532, 78.4297, 17.2403, 78.4294),
    ("Begumpet, Hyderabad", "Paradise, Secunderabad", 17.4426, 78.4709, 17.4399, 78.4985),
    ("Alwal, Hyderabad", "Malkajgiri, Hyderabad", 17.5054, 78.5327, 17.4513, 78.5312),
    ("ECIL, Hyderabad", "Kushaiguda, Hyderabad", 17.4363, 78.5762, 17.4428, 78.5667),
    ("Boduppal, Hyderabad", "Peerzadiguda, Hyderabad", 17.4087, 78.5799, 17.4109, 78.5656),
    ("Narsingi, Hyderabad", "Manikonda, Hyderabad", 17.3731, 78.3452, 17.3971, 78.3814),
    ("Attapur, Hyderabad", "Rajendra Nagar, Hyderabad", 17.3678, 78.4171, 17.3403, 78.4044),
]

CONGESTION_LOCATIONS = [
    ("Junction 1 - Hitech City", 17.4435, 78.3772),
    ("Junction 2 - Gachibowli", 17.4481, 78.3532),
    ("Junction 3 - Madhapur", 17.4489, 78.3891),
    ("Junction 4 - Ameerpet", 17.4375, 78.4483),
    ("Junction 5 - Kukatpally", 17.4898, 78.4084),
    ("Junction 6 - LB Nagar", 17.3476, 78.5527),
    ("Junction 7 - Dilsukhnagar", 17.3699, 78.5257),
    ("Junction 8 - Charminar", 17.3617, 78.4746),
]

ROAD_CONDITIONS_DATA = [
    ("Hitech City Road", 17.4440, 78.3775, "pothole", "medium"),
    ("Gachibowli Flyover", 17.4475, 78.3540, "under_construction", "high"),
    ("Madhapur Main Road", 17.4495, 78.3885, "fair", "low"),
    ("Ameerpet Junction", 17.4378, 78.4480, "accident", "high"),
    ("Kukatpally Road", 17.4902, 78.4080, "poor", "medium"),
    ("LB Nagar Underpass", 17.3470, 78.5520, "flooding", "critical"),
    ("Dilsukhnagar Road", 17.3705, 78.5250, "pothole", "medium"),
    ("Charminar Approach", 17.3620, 78.4740, "good", "low"),
]


def _load_config():
    path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'config.json')
    with open(path) as f:
        return json.load(f)


def _compute_toll(distance_km, vehicle):
    config = _load_config()
    tc = config['toll']
    if distance_km <= tc['decision_threshold_km']:
        base_toll = tc['slabs'][-1]['rate']
        for slab in tc['slabs']:
            if slab['max_km'] is None or distance_km <= slab['max_km']:
                base_toll = slab['rate']
                break
        model = "slab"
    else:
        base_toll = distance_km * tc['dynamic_rate_per_km']
        model = "dynamic"
    multiplier = tc['vehicle_multipliers'].get(vehicle, 1.0)
    return round(base_toll * multiplier, 2), model, base_toll, multiplier


class Command(BaseCommand):
    help = "Seed database with sample trips, congestion logs, and road conditions"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Delete existing data before seeding")

    def handle(self, *args, **options):
        if options["force"]:
            self.stdout.write("Clearing existing data...")
            RoadCondition.objects.all().delete()
            CongestionLog.objects.all().delete()
            TollCollection.objects.all().delete()
            Trip.objects.all().delete()

        admin_user = User.objects.filter(username="admin").first()
        if not admin_user:
            admin_user = User.objects.create_superuser("admin", "admin@example.com", "admin123")
            self.stdout.write("Created admin user")

        demo_user = User.objects.filter(username="user").first()
        if not demo_user:
            demo_user = User.objects.create_user("user", "user@example.com", "user1234")
            self.stdout.write("Created demo user")

        if Trip.objects.exists() and not options["force"]:
            self.stdout.write("Data already exists, skipping seed. Use --force to re-seed.")
            return

        today = timezone.now().date()

        for i, (origin_name, dest_name, olat, olng, dlat, dlng) in enumerate(ROUTES):
            user = admin_user if i < 5 else demo_user
            offset_days = random.randint(0, 29)
            created = timezone.make_aware(datetime.combine(
                today - timedelta(days=offset_days),
                datetime.min.time().replace(hour=random.randint(6, 22), minute=random.randint(0, 59))
            ))
            vehicle = random.choice(VEHICLES)
            distance_km = round(random.uniform(3, 25), 1)
            toll, model, base_toll, multiplier = _compute_toll(distance_km, vehicle)

            trip = Trip.objects.create(
                user=user,
                origin_name=origin_name,
                dest_name=dest_name,
                origin_lat=olat,
                origin_lng=olng,
                dest_lat=dlat,
                dest_lng=dlng,
                distance_km=distance_km,
                duration_sec=random.randint(300, 1800),
                route_geometry={"type": "LineString", "coordinates": [[olng, olat]]},
                vehicle_type=vehicle,
                toll_amount=toll,
                pricing_model=model,
                congestion_level=random.choice(["light", "moderate", "heavy", "congested"]),
                created_at=created,
            )

            if toll and multiplier > 0:
                TollCollection.objects.create(
                    trip=trip,
                    base_toll=round(base_toll, 2),
                    multiplier=multiplier,
                    total_toll=toll,
                    pricing_model=model,
                )

        self.stdout.write(f"Created {len(ROUTES)} sample trips")

        for name, lat, lng in CONGESTION_LOCATIONS:
            for _ in range(random.randint(3, 8)):
                created = timezone.make_aware(datetime.combine(
                    today - timedelta(days=random.randint(0, 29)),
                    datetime.min.time().replace(hour=random.randint(7, 21))
                ))
                CongestionLog.objects.create(
                    location_name=name,
                    lat=lat + random.uniform(-0.002, 0.002),
                    lng=lng + random.uniform(-0.002, 0.002),
                    level=round(random.uniform(0.7, 2.5), 2),
                    source="query",
                    created_at=created,
                )

        self.stdout.write(f"Created congestion logs")

        for name, lat, lng, ctype, severity in ROAD_CONDITIONS_DATA:
            status = random.choices(["reported", "verified", "resolved"], weights=[3, 3, 1])[0]
            resolved_at = timezone.now() - timedelta(days=random.randint(1, 5)) if status == "resolved" else None
            RoadCondition.objects.create(
                road_name=name,
                lat=lat,
                lng=lng,
                condition_type=ctype,
                severity=severity,
                description=f"{ctype.replace('_', ' ').title()} on {name}",
                reported_by=random.choice([admin_user, demo_user, None]),
                report_count=random.randint(1, 5),
                status=status,
                resolved_at=resolved_at,
            )

        self.stdout.write(f"Created {len(ROAD_CONDITIONS_DATA)} road conditions")
        self.stdout.write(self.style.SUCCESS("Seed complete"))
