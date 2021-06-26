from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired,Length, EqualTo, ValidationError
from report.models import User

#these are the respective forms using a flask extension, it genrates the html view too

class CreateAccount(FlaskForm):
    username = StringField('Username',
                             validators=[DataRequired(),
                            Length(min = 3, max= 15 ) ])
    password = PasswordField('Password', 
                            validators = [DataRequired()])
    
    confirm = PasswordField('Confirm',
                            validators = [DataRequired(),
                            EqualTo('password',"password don't match")]
                            )

    submit = SubmitField('Sign Up')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken, think of another.')        


class LoginForm(FlaskForm):
    username = StringField('Username',
                             validators=[DataRequired(),
                            Length(min = 3, max= 15 ) ])
    password = PasswordField('Password', 
                            validators = [DataRequired()])
    
    
    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')