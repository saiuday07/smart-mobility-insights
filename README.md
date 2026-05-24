# Smart Mobility Insights System

A smart city mobility system that calculates tolls, suggests optimal routes considering traffic and road conditions, and provides separate dashboards for users and city administrators.

Built with Django and a CLI prototype.

---

## Features

### Route Planning with Intelligence
- Real-time geocoding (Nominatim) and routing (OSRM)
- Configurable toll calculation (slab-based or dynamic per km)
- Traffic-aware ETA adjustments based on time of day and area congestion
- Road condition factors (potholes, accidents, flooding, closures) affect route delay
- Route comparison with distance, ETA, toll, and traffic level

### Road Condition Reporting
- Users report road conditions (potholes, poor surface, accidents, flooding, etc.)
- Auto-flagging: 3+ reports near same location auto-verify the condition
- Conditions displayed as color-coded markers on the map
- Affects route ETA calculations

### Role-Based Dashboards
- **User Dashboard**: Trip history, toll spending chart, vehicle usage breakdown, road conditions feed, personal reports
- **Admin Dashboard**: Revenue analytics (daily/weekly/total), 30-day revenue chart, vehicle breakdown, top users, system configuration viewer, road conditions management (resolve reports)

### CLI Prototype
Standalone command-line interface for toll calculation and traffic footfall analysis.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 6.0 |
| Database | SQLite |
| Frontend | Bootstrap 5, Leaflet, Chart.js |
| APIs | OSRM (routing), Nominatim (geocoding) |
| CLI | Python stdlib |

---

## Project Structure

```
smart-mobility-insights/
├── main.py                        # CLI entry point
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── data/
│   └── config.json                # Toll slabs, multipliers, thresholds
├── core/
│   └── toll_engine.py             # CLI toll calculation (config-driven)
├── automation/
│   ├── distance_service.py        # Simulated gate distances (CLI)
│   └── traffic_insights.py        # CLI traffic footfall + nudges
├── mobility/                      # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── insights/                      # Django app
│   ├── models.py                  # Trip, TollCollection, CongestionLog, RoadCondition
│   ├── views.py                   # All view functions + API endpoints
│   ├── urls.py                    # URL routing
│   ├── admin.py                   # Django admin registrations
│   ├── routing.py                 # Nominatim geocoding + OSRM routing
│   ├── toll_calc.py               # Config-driven toll calculation
│   ├── traffic.py                 # Time/area-based traffic factor
│   ├── road_conditions.py         # Auto-flagging + route impact factor
│   ├── forms.py                   # Login/Register forms
│   ├── management/commands/
│   │   └── seed_data.py           # Populate sample data
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html             # Route planner map
│   │   ├── dashboard.html         # User dashboard
│   │   ├── admin_dashboard.html   # Admin dashboard
│   │   └── registration/
│   │       ├── login.html
│   │       └── register.html
│   └── static/vendor/             # Vendored JS/CSS
│       ├── bootstrap/
│       ├── leaflet/
│       └── chartjs/
├── staticfiles/                   # Collected static files
└── db.sqlite3                     # SQLite database
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Seed Sample Data

```bash
python manage.py seed_data
```

Creates:
- Admin user: `admin` / `admin123`
- Demo user: `user` / `user1234`
- 20 sample trips, congestion logs, and road conditions

### 4. Start Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` and log in.

### 5. CLI Prototype (Alternative)

```bash
python main.py
```

Provides text-menu for toll calculation and traffic footfall.

---

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/geocode/?q=<query>` | GET | Login | Geocode location via Nominatim |
| `/api/route/` | POST | Login | Plan route with toll + traffic + road conditions |
| `/api/trips/` | GET | Login | Current user's trip history |
| `/api/road-conditions/` | GET | Login | List road conditions (optional lat/lng/radius) |
| `/api/road-conditions/report/` | POST | Login | Report a road condition |
| `/api/road-conditions/<id>/resolve/` | POST | Staff | Resolve a road condition |
| `/api/road-conditions/stats/` | GET | Staff | Road condition statistics |
| `/api/admin/stats/` | GET | Staff | Revenue + vehicle breakdown stats |

---

## Configuration

Toll pricing, vehicle multipliers, peak hours, and congestion thresholds are in `data/config.json`. Edit this file to adjust system behavior without code changes.

---

## Security Notes

- `DEBUG = True` is set for development; set to `False` and use a proper `ALLOWED_HOSTS` in production.
- Update `SECRET_KEY` in `mobility/settings.py` for production.
- Password validators require minimum 6 characters, no common passwords, no numeric-only passwords.
