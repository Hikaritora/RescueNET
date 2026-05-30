from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    ROLE_CHOICES = [
        ('dispatcher', 'Dispatcher'),
        ('rescuer', 'Rescuer'),
        ('admin', 'Administrator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='rescuer')

    class Meta:
        db_table = 'management_user'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

class Incident(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    TYPE_CHOICES = [
        ('Road Incident', 'Road Incident'),
        ('Medical Emergency', 'Medical Emergency'),
        ('Public Order Disturbance', 'Public Order Disturbance'),
        ('Domestic Violence', 'Domestic Violence'),
        ('Fire', 'Fire'),
        ('Technical & Weather Hazard', 'Technical & Weather Hazard'),
        ('Intoxicated or Dangerous Person', 'Intoxicated or Dangerous Person'),
        ('Theft & Suspicious Activity', 'Theft & Suspicious Activity'),
        ('Animal Assistance', 'Animal Assistance'),
        ('Missing Person', 'Missing Person'),
        ('Other', 'Other'),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, default='reported')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'management_incident'
        indexes = [
            models.Index(fields=['status'], name='management_incident_status_idx'),
        ]

    def __str__(self):
        return f"Incident #{self.id} - {self.type}"

    def clean(self):
        """Validate that in_progress incidents have assigned resources."""
        if self.status == 'in_progress':
            # Check if this incident has any assigned resources
            if not self.assigned_resources.exists():
                raise ValidationError(
                    "An incident cannot be set to 'in_progress' without assigned resources."
                )


class Resource(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('unavailable', 'Unavailable'),
    ]

    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    assigned_to = models.ForeignKey(
        Incident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_resources'
    )
    latitude = models.FloatField(default=51.1079)
    longitude = models.FloatField(default=17.0385)

    class Meta:
        db_table = 'management_resource'
        indexes = [
            models.Index(fields=['status'], name='management_resource_status_idx'),
        ]

    def __str__(self):
        return self.name
