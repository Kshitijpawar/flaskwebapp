from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.mongoflask import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
    validators= [DataRequired(), Length(min = 2,  max = 20)])

    email = StringField('Email', 
    validators= [DataRequired(), Email()])

    password = PasswordField('Password', 
    validators= [DataRequired()])

    confirm_password = PasswordField('Confirm Password', 
    validators= [DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.objects(username= username.data).first()
        if user:
            raise ValidationError('Username is taken!!')

    def validate_email(self, email):
        user = User.objects(email= email.data).first()
        if user:
            raise ValidationError('Email is taken!!')

class LoginForm(FlaskForm):
    
    email = StringField('Email', 
    validators= [DataRequired(), Email()])

    password = PasswordField('Password', 
    validators= [DataRequired()])

    remember = BooleanField('Remember Me')
  
    submit = SubmitField('Sign In')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
    validators= [DataRequired(), Length(min = 2,  max = 20)])

    email = StringField('Email', 
    validators= [DataRequired(), Email()])

    picture = FileField('Update Profile Picture', validators= [FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username= username.data).first()
            if user:
                raise ValidationError('Username is taken!!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.objects(email= email.data).first()
            if user:
                raise ValidationError('Email is taken!!')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

    submit = SubmitField('Post')

# class RatingsForm(FlaskForm):
#     choices = [(0, 0), (0.5, 0.5), (1.0, 1.0) ,(1.5, 1.5), (2.0, 2.0), (2.5, 2.5), (3.0, 3.0), (3.5, 3.5), (4.0, 4.0), (4.5, 4.5), (5.0, 5.0)]
#     ratings = SelectField(u'Ratings', choices= choices, validators=[DataRequired()])
#     submit = SubmitField('Rating')