from django import forms
from .models import Incydent

class IncydentForm(forms.ModelForm):

    PRIORITY_CHOICES_EN = [
        ('niski', 'Low'),
        ('średni', 'Medium'),
        ('wysoki', 'High'),
        ('krytyczny', 'Critical'),
    ]

    priorytet = forms.ChoiceField(
        choices=PRIORITY_CHOICES_EN,
        label='Priority',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Incydent
        fields = ['typ', 'lat', 'lng', 'priorytet']
        labels = {
            'typ': 'Type',
            'lat': 'Latitude',
            'lng': 'Longitude',
            'priorytet': 'Priority',
        }
        widgets = {
            'typ': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Road Accident'}),
            'lat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'lng': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
        }
