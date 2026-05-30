"""Seed the RescueNet database with demo users, resources and incidents."""

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from management.models import Incident, Resource


User = get_user_model()
UserManager = User._default_manager

FIRST_NAMES = [
    "Jan", "Piotr", "Krzysztof", "Andrzej", "Mateusz", "Tomasz", "Marcin",
    "Paweł", "Michał", "Jakub", "Anna", "Katarzyna", "Agnieszka", "Magdalena",
    "Ewa", "Julia", "Zuzanna", "Oliwia", "Natalia", "Aleksandra",
]
LAST_NAMES = [
    "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński",
    "Lewandowski", "Zieliński", "Szymański", "Woźniak", "Kubiak", "Jankowski",
    "Mazur", "Wróbel", "Kaczmarek",
]


class Command(BaseCommand):
    help = "Seed database with users, resources, and incidents."

    def add_arguments(self, parser):
        parser.add_argument("--admins", type=int, default=3, help="Target number of superusers")
        parser.add_argument("--dysp", type=int, default=50, help="Target number of dispatcher users")
        parser.add_argument("--rescuers", type=int, default=50, help="Target number of rescuer users")
        parser.add_argument("--resources", type=int, default=60, help="Target number of resources")
        parser.add_argument("--incidents", type=int, default=200, help="Number of incidents to append")
        parser.add_argument("--password", default="ChangeMe123!", help="Password used for seeded users")

    def unique_username(self, prefix, start=1):
        i = start
        while True:
            username = f"{prefix}{i}"
            if not User.objects.filter(username=username).exists():
                return username, i
            i += 1

    def create_users(self, target_admins=3, target_dysp=50, target_rescuers=50, default_password="ChangeMe123!"):
        created = {"admin": 0, "dispatcher": 0, "rescuer": 0}

        existing_admins = User.objects.filter(is_superuser=True).count()
        existing_dysp = User.objects.filter(role="dispatcher").count()
        existing_rescuers = User.objects.filter(role="rescuer").count()

        to_create_admins = max(0, target_admins - existing_admins)
        start = 1
        for _ in range(to_create_admins):
            username, start = self.unique_username("seed_admin_", start)
            email = f"{username}@example.com"
            user = UserManager.create_superuser(username=username, email=email, password=default_password)
            user.role = "admin"
            user.save(update_fields=["role"])
            created["admin"] += 1
            start += 1

        to_create_dysp = max(0, target_dysp - existing_dysp)
        start = 1
        for _ in range(to_create_dysp):
            username, start = self.unique_username("seed_dysp_", start)
            user = UserManager.create_user(
                username=username,
                email=f"{username}@example.com",
                password=default_password,
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
            )
            user.role = "dispatcher"
            user.save(update_fields=["role"])
            created["dispatcher"] += 1
            start += 1

        to_create_rescuers = max(0, target_rescuers - existing_rescuers)
        start = 1
        for _ in range(to_create_rescuers):
            username, start = self.unique_username("seed_rescuer_", start)
            user = UserManager.create_user(
                username=username,
                email=f"{username}@example.com",
                password=default_password,
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
            )
            user.role = "rescuer"
            user.save(update_fields=["role"])
            created["rescuer"] += 1
            start += 1

        return created

    def create_resources(self, total_resources=60, prefix="WRO"):
        mapping = [
            ("AMB", "Ambulance"),
            ("FIR", "Fire Truck"),
            ("POL", "Police Car"),
        ]

        existing_counts = {
            code: Resource.objects.filter(name__startswith=f"{prefix}-{code}-").count()
            for code, _ in mapping
        }

        per_type = total_resources // len(mapping)
        remainder = total_resources % len(mapping)
        targets = {
            code: per_type + (1 if idx < remainder else 0)
            for idx, (code, _) in enumerate(mapping)
        }

        new_resources = []
        for code, resource_type in mapping:
            existing = existing_counts[code]
            target = targets[code]
            to_create = max(0, target - existing)
            for i in range(existing + 1, existing + 1 + to_create):
                new_resources.append(
                    Resource(
                        name=f"{prefix}-{code}-{i}",
                        type=resource_type,
                        specialization="",
                        status="available",
                        latitude=round(random.uniform(51.0400, 51.1800), 6),
                        longitude=round(random.uniform(16.8800, 17.1400), 6),
                    )
                )

        if new_resources:
            Resource.objects.bulk_create(new_resources)

        return len(new_resources)

    def create_incidents(self, incidents_count=200):
        dispatchers = list(User.objects.filter(role="dispatcher"))
        if not dispatchers:
            raise SystemExit("No dispatcher users found. Create some first.")

        lat_min, lat_max = 51.0400, 51.1800
        lng_min, lng_max = 16.8800, 17.1400

        batch = []
        total_created = 0
        for _ in range(incidents_count):
            batch.append(
                Incident(
                    type=random.choice([choice[0] for choice in Incident.TYPE_CHOICES]),
                    latitude=round(random.uniform(lat_min, lat_max), 6),
                    longitude=round(random.uniform(lng_min, lng_max), 6),
                    priority=random.choice([choice[0] for choice in Incident.PRIORITY_CHOICES]),
                    status=random.choice(["reported", "in_progress", "closed"]),
                    reporter=random.choice(dispatchers),
                    reported_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                    notes="",
                )
            )
            if len(batch) >= 500:
                Incident.objects.bulk_create(batch)
                total_created += len(batch)
                batch = []

        if batch:
            Incident.objects.bulk_create(batch)
            total_created += len(batch)

        return total_created

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creating users (if needed)...")
        created_users = self.create_users(
            target_admins=options["admins"],
            target_dysp=options["dysp"],
            target_rescuers=options["rescuers"],
            default_password=options["password"],
        )
        self.stdout.write(f"Users created: {created_users}")

        self.stdout.write("Creating resources (if needed)...")
        created_resources = self.create_resources(total_resources=options["resources"])
        self.stdout.write(f"New resources created: {created_resources}")

        if options["incidents"] > 0:
            self.stdout.write(f"Creating {options['incidents']} incidents...")
            created_incidents = self.create_incidents(incidents_count=options["incidents"])
            self.stdout.write(self.style.SUCCESS(f"Incidents created: {created_incidents}"))
        else:
            self.stdout.write("Skipping incidents (incidents=0)")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
