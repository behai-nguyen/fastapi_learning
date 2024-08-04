"""
29/07/2024.

Implements validations for submitted employees data.
"""

from wtforms import StringField

from wtforms.validators import (
    Email,
    Length,
)

from .base_validation import BaseValidationForm

WWW_EMAIL_MSG = "Please enter up to 255 characters"
EMAIL_MSG = "Please enter a valid email address"
PASSWORD_MSG = "Please enter up to 32 characters"

class SearchByEmailForm(BaseValidationForm):
    email = StringField('Email', validators=[Length(1, 255, WWW_EMAIL_MSG), Email(EMAIL_MSG)])

class LoginForm(BaseValidationForm):
    email = StringField('Email', validators=[Length(1, 255, WWW_EMAIL_MSG), Email(EMAIL_MSG)])
    password = StringField('Password', validators=[Length(1, 32, PASSWORD_MSG)])
