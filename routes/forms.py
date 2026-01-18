from django import forms
from .models import PickUpLocation, DropOffLocation


class LocationForm(forms.ModelForm):
    """Base form for creating pickup or dropoff locations."""
    latitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='Enter latitude between -90 and 90',
        widget=forms.NumberInput(attrs={'step': '0.000001'})
    )
    longitude = forms.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text='Enter longitude between -180 and 180',
        widget=forms.NumberInput(attrs={'step': '0.000001'})
    )

    class Meta:
        fields = ['name', 'latitude', 'longitude']

    def clean_latitude(self):
        latitude = self.cleaned_data.get('latitude')
        if latitude is not None:
            if latitude < -90 or latitude > 90:
                raise forms.ValidationError('Latitude must be between -90 and 90.')
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data.get('longitude')
        if longitude is not None:
            if longitude < -180 or longitude > 180:
                raise forms.ValidationError('Longitude must be between -180 and 180.')
        return longitude


class PickUpLocationForm(LocationForm):
    """Form for creating pickup locations."""
    class Meta(LocationForm.Meta):
        model = PickUpLocation


class DropOffLocationForm(LocationForm):
    """Form for creating dropoff locations."""
    class Meta(LocationForm.Meta):
        model = DropOffLocation
