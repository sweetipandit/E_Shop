from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomerCreationForm(UserCreationForm):
    username= forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True )
    last_name = forms.CharField(required=True )

    def clean_first_name(self):
        fname = self.cleaned_data.get('first_name')
        if len(fname.strip())< 3:
            raise ValidationError("first name must be 4 char long")
        return fname.strip()

    def clean_last_name(self):
        lname = self.cleaned_data.get('last_name')
        if len(lname.strip())< 3:
            raise ValidationError("last name must be 4 char long")
        return lname.strip()


    class Meta:
        model=User
        fields=['first_name','last_name','username']


class CustomerAuthenticationForm(AuthenticationForm):
    username= forms.EmailField(required=True, label="Email")
    class Meta:
        model=User
        fields=['username']