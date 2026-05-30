# ZInspiracja_Apki/management/management/commands/seed_database.py

import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from management.models import Incydent, Zasob

User = get_user_model()

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

class Command(BaseCommand):
    help = 'Seed database with users, resources, and incidents'

    def add_arguments(self, parser):
        parser.add_argument('--admins', type=int, default=3, help='Total number of admin superusers')
        parser.add_argument('--dysp', type=int, default=50, help='Total number of dyspozytor users')
        parser.add_argument('--rescuers', type=int, default=50, help='Total number of ratownik users')
        parser.add_argument('--resources', type=int, default=50, help='Total number of resources')
        parser.add_argument('--incidents', type=int, default=500, help='Number of incidents to append')

    def unique_username(self, prefix, start=1):
        i = start
        while True:
            username = f"{prefix}{i}"
            if not User.objects.filter(username=username).exists():
                return username, i
            i += 1

    def create_users(self, target_admins=3, target_dysp=50, target_rescuers=50, default_password="ChangeMe123!"):
        created = {"admin": 0, "dyspozytor": 0, "ratownik": 0}

        # Count existing by role
        existing_admins = User.objects.filter(is_superuser=True).count()
        existing_dysp = User.objects.filter(role='dispatcher').count()
        existing_rescuers = User.objects.filter(role='rescuer').count()

        # Admins
        to_create_admins = max(0, target_admins - existing_admins)
        if to_create_admins:
            start = 1
            for _ in range(to_create_admins):
                username, start = self.unique_username("seed_admin_", start)
                email = f"{username}@example.com"
                user = User.objects.create_user(username=username, email=email, password=default_password)
                user.is_staff = True
                user.is_superuser = True
                    user.role = 'admin'
                user.save()
                created['admin'] += 1
                start += 1

        # Dyspozytor
        to_create_dysp = max(0, target_dysp - existing_dysp)
        if to_create_dysp:
            start = 1
            for _ in range(to_create_dysp):
                username, start = self.unique_username("seed_dysp_", start)
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                email = f"{username}@example.com"
                user = User.objects.create_user(username=username, email=email, password=default_password, first_name=first, last_name=last)
                user.role = 'dispatcher'
                user.save()
                created['dyspozytor'] += 1
                start += 1

        # Ratownik
        to_create_rescuers = max(0, target_rescuers - existing_rescuers)
        if to_create_rescuers:
            start = 1
            for _ in range(to_create_rescuers):
                username, start = self.unique_username("seed_rat_", start)
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                email = f"{username}@example.com"
                user = User.objects.create_user(username=username, email=email, password=default_password, first_name=first, last_name=last)
                user.role = 'rescuer'
                user.save()
                created['ratownik'] += 1
                start += 1

        return created

    def create_resources(self, total_resources=50, prefix="WRO"):
        mapping = [
            ("AMB", "Ambulance"),
            ("FIR", "Fire Truck"),
            ("POL", "Police Car")
        ]

        existing_counts = {}
        for code, _ in mapping:
            existing_counts[code] = Zasob.objects.filter(nazwa__startswith=f"{prefix}-{code}-").count()

        per_type = total_resources // len(mapping)
        remainder = total_resources % len(mapping)
        targets = {}
        for idx, (code, typ_en) in enumerate(mapping):
            t = per_type + (1 if idx < remainder else 0)
            targets[code] = t

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

    def create_incidents(self, incidents_count=500):
        dyspozytors = list(User.objects.filter(role='dispatcher'))
        if not dyspozytors:
            raise SystemExit("No 'dyspozytor' users found. Create some first.")

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
                priorytet=random.choice(['low', 'medium', 'high', 'critical']),
                status=random.choice(['reported', 'in_progress', 'closed']),
                zglaszajacy=reporter,
                data_zgloszenia=timezone.now() - timedelta(days=random.randint(0, 30)),
                notatki=''
            )
            batch.append(inc)
            if len(batch) >= 500:
                Incydent.objects.bulk_create(batch)
                batch = []
        if batch:
            Incydent.objects.bulk_create(batch)

        return incidents_count

    def handle(self, *args, **options):
        self.stdout.write("Creating users (if needed)...")
        created_users = self.create_users(
            target_admins=options['admins'],
            target_dysp=options['dysp'],
            target_rescuers=options['rescuers']
        )
        self.stdout.write(f"Users created: {created_users}")

        self.stdout.write("Creating resources (if needed)...")
        created_resources = self.create_resources(total_resources=options['resources'])
        self.stdout.write(f"New resources created: {created_resources}")

        if options['incidents'] > 0:
            self.stdout.write(f"Creating {options['incidents']} incidents...")
            created_incidents = self.create_incidents(incidents_count=options['incidents'])
            self.stdout.write(self.style.SUCCESS(f"Incidents created: {created_incidents}"))
        else:
            self.stdout.write("Skipping incidents (incidents=0)")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))


#USAGE EXAMPLE:
#python manage.py seed_database --admins 3 --dysp 50 --rescuers 50 --resources 60 --incidents 500