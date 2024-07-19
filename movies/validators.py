# movies/validators.py
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.deconstruct import deconstructible

@deconstructible
class CustomURLValidator:
    def __call__(self, value):
        url_validator = URLValidator()
        try:
            if not value.startswith(('http://', 'https://')):
                raise ValidationError('URL must start with http:// or https://')
            url_validator(value)
        except ValidationError:
            raise ValidationError('it isnt valid URL.')

    def __eq__(self, other):
        return isinstance(other, CustomURLValidator)


    def __eq__(self, other):
        return isinstance(other, CustomURLValidator)









