import re


def validate_password(password):
    errors = {}
    errors_list = []

    special_characters = "!@#$%^&*()-+?_=,<>/"
    if len(password) < 12:
        errors['length'] = False
        # errors['error'] = 'Password Should contain at least 12 Characters'

    if not any(x.isupper() for x in password):
        errors['upper'] = False
        # errors['error'] = 'Password Should contain at least one Upper Case Character'

    if not any(x.islower() for x in password):
        errors['lower'] = False
        # errors['error'] = 'Password Should contain at least one Lower Case Character'

    if not any(x.isdigit() for x in password):
        errors['digit'] = False
        # errors['error'] = 'Password Should contain at least one Number'

    if not any(p in special_characters for p in password):
        errors['special'] = False
        # errors['error'] = 'Password Should contain any special character'
    errors_list.append(errors)
    return errors_list
