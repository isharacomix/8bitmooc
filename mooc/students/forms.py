# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.forms import Form

class RegistrationForm(Form):
    username    = forms.SlugField(label="Username")
    email       = forms.EmailField(label="E-mail address")
    password1   = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                  label="Password")
    password2   = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                  label="Repeat password")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with your login name (%s) "
                                        "already exists."%username)
        else:
            return username

    def clean(self):
        data = self.cleaned_data
        if 'password1' in data and 'password2' in data:
            if data['password1'] != data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return data

