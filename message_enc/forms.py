from flask_wtf import FlaskForm
from wtforms import StringField, StringField, SubmitField, PasswordField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import Length, DataRequired, Email, EqualTo, ValidationError
from message_enc.models import User

class RoomForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=30)])
    description = StringField('Brief', validators=[Length(min=5, max=60)])
    key = StringField('PIN', validators=[Length(min=0, max=6)])
    submit = SubmitField('Create Room')

    def validate_key(self, key):
        x = key.data
        if not x.isdigit():
            raise ValidationError("Only numerals(0-9) allowed.")

# User Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is taken. Try with a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("There is already an account created using this email.")

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me', default=False)
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title',
                        validators=[DataRequired(), Length(min=4, max=20)])
    content = TextAreaField('Content',
                        validators=[DataRequired()])
    submit = SubmitField('Add to Room')