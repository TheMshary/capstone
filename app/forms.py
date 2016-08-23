from django import forms
from django.core.validators import RegexValidator
from django.forms import ModelForm

letter_validator = RegexValidator(r'^[a-zA-Z]*$','Please Type Letters')



class PredefinedServiceForm(forms.Form):  
	title = forms.CharField(required=True)
	description = forms.CharField(required=False, widget=forms.Textarea)
	image = forms.ImageField(required=True)
	price = forms.FloatField(required=False)#placeholder=0.000)


#============================ Accounts Forms ============================#

class UserSignup(forms.Form):
	name = forms.CharField(required=True, validators=[letter_validator])
	email = forms.EmailField(required=True)
	password = forms.CharField(widget=forms.PasswordInput(), required=True)

class UserLogin(forms.Form):
	username = forms.CharField(required=True)
	password = forms.CharField(required=True, widget=forms.PasswordInput())
