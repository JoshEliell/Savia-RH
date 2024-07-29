from django.core.exceptions import ValidationError

def validate_file_size(value):
        filesize= value.size

        if filesize > 1000000:
            raise ValidationError("No puedes subir un archivo mayor a 1 MB")
        else:
            return value