from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, length, ValidationError, EqualTo, Email
from app.models import User


# ------------------------------------------ Login Form ----------------------------------------------------------------
class LoginForm(FlaskForm):
    username = StringField(label='Username',
                           render_kw={'class': 'form-control', 'id': 'form-username'},
                           validators=[DataRequired()])

    password = PasswordField(label='Password',
                             render_kw={'class': 'form-control', 'id': 'form-password'},
                             validators=[DataRequired()])

    remember_me = BooleanField(label='Remember Me',
                               render_kw={'class': 'form-check-label'})

    submit = SubmitField(label='Sign In',
                         render_kw={'class': 'btn btn-primary', 'id': 'register-button'},
                         )


# ------------------------------------------ Registration Form ---------------------------------------------------------
class RegistrationForm(FlaskForm):
    username = StringField(label='Username',
                           render_kw={'class': 'form-control', 'id': 'form-username'},
                           validators=[DataRequired(),
                                       length(min=3, message='Username must be at least 3 characters'),
                                       length(max=64, message='Too long username')]
                           )

    email = StringField(label='Email',
                        render_kw={'class': 'form-control', 'id': 'form-email'},
                        validators=[DataRequired(),
                                    length(max=120, message='Too long email'),
                                    Email()]
                        )

    password = PasswordField(label='Password',
                             render_kw={'class': 'form-control', 'id': 'form-password'},
                             validators=[DataRequired()]
                             )

    password2 = PasswordField(label='Repeat Password',
                              render_kw={'class': 'form-control', 'id': 'form-password2'},
                              validators=[DataRequired(), EqualTo('password')
                                          ]
                              )
    submit = SubmitField(label='Register',
                         render_kw={'class': 'btn btn-primary', 'id': 'register-button'},
                         )

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:  # username already exists
            raise ValidationError(message='Please try a different username.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:  # email already exists
            raise ValidationError(message='Please try a different email.')


# ------------------------------------------ Edit Profile Form ---------------------------------------------------------
class EditProfileForm(FlaskForm):
    username = StringField(label='Username',
                           render_kw={'class': 'form-control', 'id': 'form-username'},
                           validators=[DataRequired(),
                                       length(min=3, message='Username must be at least 3 characters'),
                                       length(max=64, message='Too long username')]
                           )

    email = StringField(label='Email',
                        render_kw={'class': 'form-control', 'id': 'form-email'},
                        validators=[Email(),
                                    length(max=120, message='Too long email')]
                        )

    about_me = TextAreaField(label='About Me',
                             render_kw={'class': 'form-control', 'id': 'form-about-me'},
                             validators=[length(min=0, max=140)]
                             )

    submit = SubmitField(label='Submit',
                         render_kw={'class': 'btn btn-primary', 'id': 'register-button'},
                         )

    # Prevent Duplicate Username
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username != self.original_username:
            user = User.query.filter_by(username=username).first()
            if user is not None:
                raise ValidationError('Please try a different username.')