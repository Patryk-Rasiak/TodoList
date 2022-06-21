from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Todo, Tag
from django import forms


class TodoForm(ModelForm):

    class Meta:
        model = Todo
        fields = ['title', 'description', 'tag', 'deadline', 'important']


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='username', min_length=1, max_length=20)
    password1 = forms.CharField()
    password2 = forms.CharField()


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = ['title']
