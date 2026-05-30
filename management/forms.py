from django import forms
from .models import Incident, Resource


class IncidentForm(forms.ModelForm):

    PRIORITY_CHOICES_EN = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    # Expose English-named form fields that override the model's widgets
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES_EN,
        label='Priority',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    type = forms.ChoiceField(
        choices=Incident.TYPE_CHOICES,
        label='Type',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Incident
        # Order fields logically for the UI: type, priority, notes, then coordinates
        fields = ['type', 'priority', 'notes', 'latitude', 'longitude']
        labels = {
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'notes': 'Notes',
        }
        widgets = {
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes or details about the incident...'}),
        }


class ResourceForm(forms.ModelForm):

    TYPE_CHOICES = [
        ('Ambulance', 'Ambulance'),
        ('Fire Truck', 'Fire Truck'),
        ('Police Car', 'Police Car'),
        ('Rescue Unit', 'Rescue Unit'),
        ('Medical Personnel', 'Medical Personnel'),
        ('Other', 'Other'),
    ]

    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label='Type',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Resource
        # Exclude status and assigned_to; those are managed by assignment logic
        fields = ['name', 'type', 'specialization', 'latitude', 'longitude']
        labels = {
            'name': 'Name',
            'specialization': 'Specialization',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ambulance A-12'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Life Support'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
        }
