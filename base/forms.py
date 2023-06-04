from django.forms import ModelForm
from .models import Project
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        exclude = ['host','authorized_users']

from django.contrib.auth.forms import UserCreationForm
from django import forms

class UserCreationFormExtended(UserCreationForm):
    DESIGNATION_CHOICES = (
        ('Manager', 'Manager'),
        ('Senior Manager', 'Senior Manager'),
        ('Assistant General Manager', 'Assistant General Manager'),
        ('Deputy General Manager', 'Deputy General Manager'),
        ('General Manager', 'General Manager'),
    )

    DEPARTMENT_CHOICES = (
        ('Human Resource', 'Human Resource'),
        ('Finance','Finace'),
        ('Planning','Planning'),
        ('Air Navigation Services','Air Navigation Services'),
        ('Operations','Operations'),
    )
    
    LOCATION_CHOICES = (
        ('Northern Region','Northern Region'),
        ('North Eastern Region','North Eastern Region'),
        ('Eastern Region','Eastern Region'),
        ('Southern Region','Southern Region'),
        ('Western Region','Western Region'),
        ('CHQ','CHQ'),
        ('CATC','CATC'),
        ('Chennai','Chennai'),
        ('Kolkata','Kolkata'),
    )
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES)
    location = forms.ChoiceField(choices=LOCATION_CHOICES)
    designation = forms.ChoiceField(choices=DESIGNATION_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'department', 'location', 'designation']
