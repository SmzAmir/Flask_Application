from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from app.models import User
from flask_login import login_user, current_user

# ------------------------------------------ Home Page -----------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Amir'}
    posts = [
        {
            'author': {'username': 'Ali'},
            'body': 'Rainy day in North York!'
        },
        {
            'author': {'username': 'Sam'},
            'body': 'The Friends series is the best!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


# ------------------------------------------ Login Page ----------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # ------------------------ If User is already logged in ------------------------------------------------------------
    if current_user.is_authenticated:  # is_authenticated is coming from the UserMixin added to the User model
        return redirect(url_for('index'))

    # ------------------------ Check for login -------------------------------------------------------------------------
    if form.validate_on_submit():
        user = User.query(username=form.username.data).first()
        if user is None or user.check_password(form.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
        else:
            # ------------------------ Successful login ----------------------------------------------------------------
            login_user(user=user, remember=form.remember_me.data)
            return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)