# employee/forms.py

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Delegation

class DelegationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)

        self.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['delegate'].widget.attrs.update({'class': 'form-control'})

        if self.manager:
            self.fields['delegate'].queryset = User.objects.filter(
                employee__manager=self.manager
            ).exclude(pk=self.manager.pk)

    class Meta:
        model = Delegation
        fields = ['delegate', 'start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and start_date < timezone.now().date():
            raise ValidationError("Delegation cannot start in the past.")
        if start_date and end_date and end_date < start_date:
            raise ValidationError("The end date cannot be before the start date.")

        # check for overlapping delegations
        if self.manager and start_date and end_date:
            overlapping_delegations = Delegation.objects.filter(
                manager=self.manager,
                start_date__lte=end_date,
                end_date__gte=start_date
            ).exclude(pk=self.instance.pk)

            if overlapping_delegations.exists():
                raise ValidationError("You already have an active delegation during these dates.")

        return cleaned_data
