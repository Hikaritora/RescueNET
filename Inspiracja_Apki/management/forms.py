from django import forms
from .models import Incydent, Zasob


class IncydentForm(forms.ModelForm):

    PRIORITY_CHOICES_EN = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    priorytet = forms.ChoiceField(
        choices=PRIORITY_CHOICES_EN,
        label='Priority',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    typ = forms.ChoiceField(
        choices=Incydent.TYPE_CHOICES,
        label='Type',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Incydent
        # Order fields logically for the UI: type, priority, notes, then coordinates
        fields = ['typ', 'priorytet', 'notatki', 'lat', 'lng']
        labels = {
            'lat': 'Latitude',
            'lng': 'Longitude',
            'notatki': 'Notes',
        }
        widgets = {
            'lat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'lng': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'notatki': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes or details about the incident...'}),
        }


class ZasobForm(forms.ModelForm):

    TYPE_CHOICES = [
        ('Ambulance', 'Ambulance'),
        ('Fire Truck', 'Fire Truck'),
        ('Police Car', 'Police Car'),
        ('Rescue Unit', 'Rescue Unit'),
        ('Medical Personnel', 'Medical Personnel'),
        ('Other', 'Other'),
    ]

    typ = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label='Type',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Zasob
        # Exclude status and assigned_to; those are managed by assignment logic
        fields = ['nazwa', 'typ', 'specjalizacja', 'lat', 'lng']
        labels = {
            'nazwa': 'Name',
            'specjalizacja': 'Specialization',
            'lat': 'Latitude',
            'lng': 'Longitude',
        }
        widgets = {
            'nazwa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ambulance A-12'}),
            'specjalizacja': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Life Support'}),
            'lat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'lng': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
        }
