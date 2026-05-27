# generator_danych.py
# Place this file in the Inspiracja_Apki folder (same folder as manage.py).
# Usage examples:
#   python generator_danych.py
#   python generator_danych.py --admins 3 --dysp 50 --rescuers 50 --resources 60 --incidents 500

import os
import django
import random
import argparse
from datetime import timedelta
from django.utils import timezone

# Bootstrap Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from management.models import Incydent, Zasob

User = get_user_model()

# Small lists of Polish first & last names (no extra dependency)
FIRST_NAMES = [
    "Jan", "Piotr", "Krzysztof", "Andrzej", "Mateusz", "Tomasz", "Marcin",
    "Paweł", "Michał", "Jakub", "Anna", "Katarzyna", "Agnieszka", "Magdalena",
    "Ewa", "Julia", "Zuzanna", "Oliwia", "Natalia", "Aleksandra"
]
LAST_NAMES = [
    "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński",
    "Lewandowski", "Zieliński", "Szymański", "Woźniak", "Kubiak", "Jankowski",
    "Mazur", "Wróbel", "Kaczmarek"
]

def unique_username(prefix, start=1):
    i = start
    while True:
        username = f"{prefix}{i}"
        if not User.objects.filter(username=username).exists():
            return username, i
        i += 1

def create_users(target_admins=3, target_dysp=50, target_rescuers=50, default_password="ChangeMe123!"):
    created = {"admin": 0, "dyspozytor": 0, "ratownik": 0}

    # Count existing by role
    existing_admins = User.objects.filter(is_superuser=True).count()
    existing_dysp = User.objects.filter(rola='dyspozytor').count()
    existing_rescuers = User.objects.filter(rola='ratownik').count()

    # Admins: create only missing number (but don't touch existing superusers if they're there)
    to_create_admins = max(0, target_admins - existing_admins)
    if to_create_admins:
        start = 1
        for _ in range(to_create_admins):
            username, start = unique_username("seed_admin_", start)
            email = f"{username}@example.com"
            user = User.objects.create_user(username=username, email=email, password=default_password)
            user.is_staff = True
            user.is_superuser = True
            user.rola = 'admin'
            user.save()
            created['admin'] += 1
            start += 1

    # Dyspozytor users
    to_create_dysp = max(0, target_dysp - existing_dysp)
    if to_create_dysp:
        start = 1
        for _ in range(to_create_dysp):
            username, start = unique_username("seed_dysp_", start)
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            email = f"{username}@example.com"
            user = User.objects.create_user(username=username, email=email, password=default_password, first_name=first, last_name=last)
            user.rola = 'dyspozytor'
            user.save()
            created['dyspozytor'] += 1
            start += 1

    # Ratownik users
    to_create_rescuers = max(0, target_rescuers - existing_rescuers)
    if to_create_rescuers:
        start = 1
        for _ in range(to_create_rescuers):
            username, start = unique_username("seed_rat_", start)
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            email = f"{username}@example.com"
            user = User.objects.create_user(username=username, email=email, password=default_password, first_name=first, last_name=last)
            user.rola = 'ratownik'
            user.save()
            created['ratownik'] += 1
            start += 1

    return created

def create_resources(total_resources=50, prefix="WRO"):
    """
    Create resources up to total_resources. Distribute evenly over AMB, FIR, POL types.
    Names: WRO-AMB-1, WRO-FIR-1, WRO-POL-1 etc.
    Types set to English: 'Ambulance', 'Fire Truck', 'Police Car'
    """
    mapping = [
        ("AMB", "Ambulance"),
        ("FIR", "Fire Truck"),
        ("POL", "Police Car")
    ]
    # Count existing generated resources per code type
    existing_counts = {}
    for code, _ in mapping:
        existing_counts[code] = Zasob.objects.filter(nazwa__startswith=f"{prefix}-{code}-").count()

    # Decide how many per type (distribute evenly)
    per_type = total_resources // len(mapping)
    remainder = total_resources % len(mapping)
    targets = {}
    for idx, (code, typ_en) in enumerate(mapping):
        t = per_type + (1 if idx < remainder else 0)
        targets[code] = t

    # Create missing resources for each type
    created_total = 0
    new_resources = []
    for code, typ_en in mapping:
        existing = existing_counts[code]
        target = targets[code]
        to_create = max(0, target - existing)
        start_index = existing + 1
        for i in range(start_index, start_index + to_create):
            name = f"{prefix}-{code}-{i}"
            new_resources.append(Zasob(
                nazwa=name,
                typ=typ_en,
                specjalizacja='',
                dostepnosc=True,
                status='Available',
                lat=round(random.uniform(51.0400, 51.1800), 6),
                lng=round(random.uniform(16.8800, 17.1400), 6)
            ))
        created_total += to_create

    if new_resources:
        Zasob.objects.bulk_create(new_resources)

    return created_total

def create_incidents(incidents_count=500):
    # Reporter must be a dyspozytor
    dyspozytors = list(User.objects.filter(rola='dyspozytor'))
    if not dyspozytors:
        raise SystemExit("No 'dyspozytor' users found. Create some before generating incidents.")

    LAT_MIN, LAT_MAX = 51.0400, 51.1800
    LNG_MIN, LNG_MAX = 16.8800, 17.1400

    batch = []
    for _ in range(incidents_count):
        reporter = random.choice(dyspozytors)
        inc = Incydent(
            typ=random.choice([
                'Road Incident', 'Medical Emergency', 'Public Order Disturbance',
                'Domestic Violence', 'Fire', 'Technical & Weather Hazard',
                'Intoxicated or Dangerous Person', 'Theft & Suspicious Activity',
                'Animal Assistance', 'Missing Person', 'Other'
            ]),
            lat=round(random.uniform(LAT_MIN, LAT_MAX), 6),
            lng=round(random.uniform(LNG_MIN, LNG_MAX), 6),
            priorytet=random.choice(['niski', 'średni', 'wysoki', 'krytyczny']),
            status=random.choice(['zgłoszony', 'w toku', 'zakończony']),
            zglaszajacy=reporter,
            data_zgloszenia=timezone.now() - timedelta(days=random.randint(0, 30)),
            notatki=''
        )
        batch.append(inc)
        # bulk create in batches of 500 to avoid memory spikes
        if len(batch) >= 500:
            Incydent.objects.bulk_create(batch)
            batch = []
    if batch:
        Incydent.objects.bulk_create(batch)

    return incidents_count

def main(args):
    print("Creating users (if needed)...")
    created_users = create_users(target_admins=args.admins, target_dysp=args.dysp, target_rescuers=args.rescuers)
    print(f"Users created: {created_users}")

    print("Creating resources (if needed)...")
    created_resources = create_resources(total_resources=args.resources)
    print(f"New resources created: {created_resources}")

    if args.incidents > 0:
        print(f"Creating {args.incidents} incidents (appends)...")
        created_incidents = create_incidents(incidents_count=args.incidents)
        print(f"Incidents created: {created_incidents}")
    else:
        print("Skipping incident creation (incidents=0)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed DB with users, resources and incidents.")
    parser.add_argument("--admins", type=int, default=3, help="Total number of admin superusers to ensure")
    parser.add_argument("--dysp", type=int, default=50, help="Total number of dyspozytor users to ensure")
    parser.add_argument("--rescuers", type=int, default=50, help="Total number of ratownik users to ensure")
    parser.add_argument("--resources", type=int, default=50, help="Total number of resources to ensure")
    parser.add_argument("--incidents", type=int, default=500, help="Number of incidents to append")
    args = parser.parse_args()
    main(args)