"""Find incidents with status 'in_progress' and no assigned resources and set them to 'reported'.

Usage: python manage.py fix_in_progress_incidents
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from management.models import Incident


class Command(BaseCommand):
    help = "Fix incidents: set status to 'reported' for in_progress incidents with no resources"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't save changes, only print how many incidents would be changed",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)

        qs = Incident.objects.filter(status="in_progress")
        total_in_progress = qs.count()

        # Filter those that have no assigned_resources
        problematic = [inc for inc in qs if inc.assigned_resources.count() == 0]
        problematic_count = len(problematic)

        if problematic_count == 0:
            self.stdout.write(self.style.SUCCESS("No in_progress incidents without resources found."))
            return

        self.stdout.write(f"Found {problematic_count} in_progress incidents without assigned resources (total in_progress: {total_in_progress}).")

        if dry_run:
            self.stdout.write("Dry run: no changes will be made.")
            return

        for inc in problematic:
            inc.status = "reported"
            inc.save(update_fields=["status"])

        self.stdout.write(self.style.SUCCESS(f"Updated {problematic_count} incidents to status 'reported'."))

