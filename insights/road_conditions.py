import math
from datetime import datetime

from django.utils import timezone

from .models import RoadCondition

REPORT_AUTO_VERIFY_THRESHOLD = 3
PROXIMITY_METERS = 500


def _haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearby_condition(lat, lng, condition_type):
    nearby = RoadCondition.objects.filter(
        condition_type=condition_type,
        status__in=['reported', 'verified'],
    )
    for rc in nearby:
        dist = _haversine(lat, lng, rc.lat, rc.lng)
        if dist <= PROXIMITY_METERS:
            return rc
    return None


def report_condition(road_name, lat, lng, condition_type, severity, description, user=None):
    existing = find_nearby_condition(lat, lng, condition_type)
    if existing:
        existing.report_count += 1
        if existing.report_count >= REPORT_AUTO_VERIFY_THRESHOLD and existing.status == 'reported':
            existing.status = 'verified'
        existing.save()
        return existing, False
    rc = RoadCondition.objects.create(
        road_name=road_name,
        lat=lat,
        lng=lng,
        condition_type=condition_type,
        severity=severity,
        description=description,
        reported_by=user,
        report_count=1,
        status='reported',
    )
    return rc, True


def resolve_condition(condition_id):
    try:
        rc = RoadCondition.objects.get(id=condition_id, status__in=['reported', 'verified'])
        rc.status = 'resolved'
        rc.resolved_at = timezone.now()
        rc.save()
        return rc
    except RoadCondition.DoesNotExist:
        return None


def get_road_condition_factor(origin_lat, origin_lng, dest_lat, dest_lng):
    lat_center = (origin_lat + dest_lat) / 2
    lng_center = (origin_lng + dest_lng) / 2
    radius = max(
        _haversine(origin_lat, origin_lng, dest_lat, dest_lng) / 2,
        1000,
    )
    active = RoadCondition.objects.filter(
        status__in=['reported', 'verified'],
    )
    severity_map = {'low': 0.1, 'medium': 0.2, 'high': 0.4, 'critical': 0.6}
    factor = 0.0
    for rc in active:
        dist = _haversine(lat_center, lng_center, rc.lat, rc.lng)
        if dist <= radius:
            if rc.condition_type == 'closed':
                factor += 0.8
            elif rc.condition_type in ('accident', 'flooding'):
                factor += severity_map.get(rc.severity, 0.3)
            elif rc.condition_type in ('poor', 'under_construction', 'pothole'):
                factor += severity_map.get(rc.severity, 0.15)
    return round(min(factor, 1.5), 2)
