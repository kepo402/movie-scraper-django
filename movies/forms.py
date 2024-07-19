# movies/forms.py
from django import forms
from .models import Content
from .validators import CustomURLValidator

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply custom URL validator
        self.fields['download_link'].validators.append(CustomURLValidator())



