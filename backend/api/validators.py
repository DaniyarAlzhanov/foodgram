from django.core.exceptions import ValidationError


def validate_username(username):
    if username == 'me':
        raise ValidationError(
            'Использовать имя "me" в качестве '
            'никнейма запрещено'
        )
    return username
