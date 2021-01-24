from flask import render_template, flash, redirect, url_for, request
from datetime import datetime
from app import app, db
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required


# ------------------------------------------ Last Seen -----------------------------------------------------------------
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# ------------------------------------------ Home Page -----------------------------------------------------------------
@app.route('/')
@app.route('/index')
@login_required
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
    if request.method == 'GET':
        # ------------------------ If User is already logged in --------------------------------------------------------
        if current_user.is_authenticated:  # is_authenticated is coming from the UserMixin added to the User model
            return redirect(url_for('index'))
        else:
            return render_template('login.html', title='Sign In', form=form)
    if request.method == 'POST':
        # ------------------------ Check for login ---------------------------------------------------------------------
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data.lower()).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid Username or Password', 'danger')
                return redirect(url_for('login'))
            else:
                # ------------------------ Successful login ------------------------------------------------------------
                login_user(user=user, remember=form.remember_me.data)
                # ------------------------ If User was in a page -------------------------------------------------------
                next_page = request.args.get('next')  # the next page argument is added to the url after ?next=...

                # ------------------------ Not Valid Next Page or an Attack --------------------------------------------
                if not next_page or url_parse(next_page).netloc() != '':
                    return redirect(url_for('index'))

                return redirect(url_for(next_page))
        # ------------------------ Failed Login ------------------------------------------------------------------------
        else:
            return render_template('login.html', title='Sign In', form=form)


# ------------------------------------------ Logout Page ---------------------------------------------------------------
@app.route('/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        logout_user()
        return redirect(url_for('index'))
    else:
        print('Invalid request!')


# ------------------------------------------ Registration Page ---------------------------------------------------------
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if request.method == 'GET':
        # ------------------------ If User is already logged in --------------------------------------------------------
        if current_user.is_authenticated:  # is_authenticated is coming from the UserMixin added to the User model
            return redirect(url_for('index'))

        else:
            return render_template('registration.html', title='Register', form=form)

    if request.method == 'POST':
        print('Registration Err:', form.errors)
        # ------------------------ Successful Registration -------------------------------------------------------------
        if form.validate_on_submit():
            print('Registration form is validated')
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(password=form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('You are not registered!', 'success')
            return redirect(url_for('index'))
        # ------------------------ Failed Registration -----------------------------------------------------------------
        else:
            flash('Something went wrong!', 'danger')
            return render_template('registration.html', title='Register', form=form)


# ------------------------------------------ User Profile Page ---------------------------------------------------------
@app.route('/user/<username>', methods=['GET'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


# ------------------------------------------ Edit User Profile Page ----------------------------------------------------
@app.route('/user/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm()
    # ------------------------ Loading the Edit Profile Page -----------------------------------------------------------
    if request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        return render_template('edit_profile.html', form=form)
    # ------------------------ Posting the Edit Profile Form -----------------------------------------------------------
    elif request.method == 'POST':
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Changes have been accepted!', 'success')
        return redirect(url_for('user', username=current_user.username))

    else:
        return redirect(url_for('user', username=current_user.username))