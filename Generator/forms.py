from django import forms
from .models import Schedule, Event

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ("name",)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter schedule name', 'class': 'form-control', 'required': True })
        }
        labels = {"name": "Schedule Name"}