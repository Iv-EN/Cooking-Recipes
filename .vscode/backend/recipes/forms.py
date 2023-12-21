from django.forms import ModelForm
from django.forms.widgets import TextInput

from .models import Tag


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        widgets = {
            'color': TextInput(attrs={'type': 'color'})
        }
