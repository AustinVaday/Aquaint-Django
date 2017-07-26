from django import forms
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    fullname = forms.CharField(label='Full Name', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
