from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


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

    # ------------------------ Successful login ------------------------------------------------------------------------
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)