from django import forms

# TODO: custom entries will be added in, extends from UserCreationForm
class SignUpForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
