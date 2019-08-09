import re

from django import forms
from django.core.exceptions import ValidationError

from constance import config


class ConnectionPackForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password', '')

        if password == config.GENERATOR_PASSWORD:
            return password

        raise ValidationError('Invalid password')


class ConnectionPackLookupForm(forms.Form):
    private_key = forms.CharField()

    def clean_private_key(self):
        private_key = self.cleaned_data.get('private_key', '')

        if len(private_key) == 44 and re.match('^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$', private_key):
            return private_key

        raise ValidationError('Invalid private key')
