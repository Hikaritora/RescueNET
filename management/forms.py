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
        ('Police', 'Police'),
        ('Fire Truck', 'Fire Truck'),
        ('Technical', 'Technical'),
    ]

    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label='Type',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    specialization = forms.ChoiceField(
        choices=[],
        required=True,
        label='Specialization',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Resource
        # Exclude status and assigned_to; those are managed by assignment logic
        fields = ['name', 'type', 'specialization', 'latitude', 'longitude']
        labels = {
            'name': 'Name',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ambulance A-12'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        resource_type = None
        if self.data.get('type'):
            resource_type = self.data.get('type')
        elif self.instance and self.instance.pk:
            resource_type = self.instance.type
        else:
            resource_type = Resource.TYPE_CHOICES[0][0]

        allowed = Resource.specialization_choices_for_type(resource_type)
        self.fields['specialization'].choices = allowed
        if not self.is_bound and allowed:
            self.fields['specialization'].initial = allowed[0][0]

    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('type')
        specialization = cleaned_data.get('specialization')

        if resource_type:
            if not specialization:
                cleaned_data['specialization'] = Resource.default_specialization_for_type(resource_type)
                specialization = cleaned_data['specialization']

            allowed = {value for value, _ in Resource.specialization_choices_for_type(resource_type)}
            if specialization and specialization not in allowed:
                self.add_error('specialization', 'Select a valid specialization for this resource type.')

        return cleaned_data

