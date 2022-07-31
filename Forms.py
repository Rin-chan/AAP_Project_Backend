from wtforms import Form, PasswordField, validators
from wtforms.validators import EqualTo

class ResetForm(Form):
    password = PasswordField('Password', [validators.length(min=8),validators.DataRequired()])
    confirm = PasswordField('Repeat Password', [validators.length(min=8), validators.DataRequired(), EqualTo('password', message='Passwords must match')])