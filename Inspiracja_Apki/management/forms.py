from django import forms
from .models import Incydent

class IncydentForm(forms.ModelForm):
    class Meta:
        model = Incydent
        fields = ['typ', 'lat', 'lng', 'priorytet']
        widgets = {
            'typ': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Np. Wypadek drogowy'}),
            'lat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'lng': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'priorytet': forms.Select(attrs={'class': 'form-control'}),
        }