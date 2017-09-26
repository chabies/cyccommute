#This is to use a certain column names for fields of a form where the user input data

from django.contrib.auth.models import User #user system in the admin # we will tweak the user management system in the admin
from django import forms

from .models import ZIPGPX

# filename column will be used as a field in the file upload form
class FileUploadForm(forms.ModelForm):

    class Meta:
        model = ZIPGPX
        fields = ['filename']

class UserForm(forms.ModelForm): #blueprint for making forms
    password = forms.CharField(widget=forms.PasswordInput) #to hide password/ if empty parenthesis, it returns raw texts

    class Meta: #information about the UserForm class
        model = User
        fields = ['username','email','password'] #specify which information we need out of the original admin
