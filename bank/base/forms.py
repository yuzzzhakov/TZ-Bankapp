from django import forms
from .models import *
from .constants import *


class MasterAccountRefillForm(forms.Form):
    refill = forms.IntegerField()


class NewOrgForm(forms.Form):
    INN = forms.IntegerField()
    balance = forms.IntegerField()
