from flask import render_template, flash, redirect, url_for, request
from datetime import datetime
from app import app, db
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from app.email import send_password_reset_email
from flask import session


# ------------------------------------------ Last Seen -----------------------------------------------------------------
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# ------------------------------------------ Home Page -----------------------------------------------------------------
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    user_posts = Post.query.filter_by(user_id=current_user.id).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('index', page=user_posts.next_num) if user_posts.has_next else None
    prev_url = url_for('index', page=user_posts.prev_num) if user_posts.has_prev else None

    followed_posts = current_user.followed_posts()
    # ------------------------ Default Page View -----------------------------------------------------------------------
    if request.method == 'GET':
        return render_template('index.html', title='Home', user=current_user,
                               user_posts=user_posts.items,
                               followed_posts=followed_posts,
                               next_url=next_url,
                               prev_url=prev_url)
    else:
        pass


# ------------------------------------------ Explore Page --------------------------------------------------------------
@app.route('/explore', methods=['GET'])
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    # ------------------------ Default Page View -----------------------------------------------------------------------
    if request.method == 'GET':
        return render_template('explore.html', title='Explore',
                               posts=posts.items,
                               next_url=next_url,
                               prev_url=prev_url)
    else:
        pass


# ------------------------------------------ New Post Page -------------------------------------------------------------
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def user_post():
    form = PostForm()
    # ------------------------ Default Page View -----------------------------------------------------------------------
    if request.method == 'GET':
        return render_template('post.html', title='Post', form=form)
    # ------------------------ Post a New Post -------------------------------------------------------------------------
    if request.method == 'POST':
        # ------------------------ Successful Posting ------------------------------------------------------------------
        if form.validate_on_submit():
            post_obj = Post(body=form.body.data, author=current_user)
            db.session.add(post_obj)
            db.session.commit()
            flash('You post is not live!', 'success')
            return redirect(url_for('index'))  # prevent user from submit the form by refreshing the page
        # ------------------------ Failed Posting ----------------------------------------------------------------------
        else:
            return render_template('post.html', title='Post', form=form)


# ------------------------------------------ Edit Post Page ------------------------------------------------------------
@app.route('/post/edit/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post_to_edit = Post.query.filter_by(id=post_id).first()
    form = PostForm(obj=post_to_edit)
    # ------------------------ Default Page View -----------------------------------------------------------------------
    if request.method == 'GET':
        return render_template('post.html', title='Post', form=form)
    # ------------------------ Post a New Post -------------------------------------------------------------------------
    if request.method == 'POST':
        # ------------------------ Successful Posting ------------------------------------------------------------------
        if form.validate_on_submit():
            new_post = Post(body=form.body.data, id=post_id, timestamp=datetime.utcnow())
            db.session.add(new_post)
            db.session.commit()
            flash('You post is changed successfully!')
            return redirect(url_for('index'))  # prevent user from submit the form by refreshing the page
        # ------------------------ Failed Posting ----------------------------------------------------------------------
        else:
            return render_template('post.html', title='Post', form=form)


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
                if not next_page or url_parse(next_page).netloc != '':
                    return redirect(url_for('index'))

                # return redirect(url_for(next_page))
                return redirect(url_for('index'))
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
            user = User(username=form.username.data.lower(), email=form.email.data.lower())
            user.set_password(password=form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('You are not registered!', 'success')
            return redirect(url_for('index'))
        # ------------------------ Failed Registration -----------------------------------------------------------------
        else:
            flash('Something went wrong!', 'danger')
            return render_template('registration.html', title='Register', form=form)


# ------------------------------------------ Reset Password Page -------------------------------------------------------
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # ------------------------------------------ User Already Logged In ------------------------------------------------
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        form = ResetPasswordRequestForm()
        # ------------------------------------------ Default Render of Page --------------------------------------------
        if request.method == 'GET':
            return render_template('reset_password_request.html',
                                   title='Reset Password', form=form)
        # ------------------------------------------ Send Reset Request ------------------------------------------------
        elif request.method == 'POST' and form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            # If the user exists:
            if user:
                send_password_reset_email(user=user)
                flash('Check your email for the instructions to reset your password', 'success')
                return redirect(url_for('login'))
            else:
                session.clear()
                flash('Invalid email address', 'danger')
                return redirect('reset_password_request')
        else:
            pass


# ------------------------------------------ Reset Password Request ----------------------------------------------------
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # ------------------------------------------ User Already Logged In ------------------------------------------------
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # ------------------------------------------ Default Render of Page ------------------------------------------------
    else:
        # ------------------------------------------ Default Render of Page --------------------------------------------
        form = ResetPasswordForm()
        if request.method == 'GET':
            return render_template('reset_password.html', form=form)
        # ------------------------------------------ Send Reset Request ------------------------------------------------
        elif request.method == 'POST':
            user = User.verify_reset_password_token(token)
            # User does not exist:
            if not user:
                return redirect(url_for('index'))
            # Successful request:
            if form.validate_on_submit():
                user.set_password(form.password.data)
                db.session.commit()
                flash('Your password has been reset.', 'success')
                return redirect(url_for('login'))


# ------------------------------------------ User Profile Page ---------------------------------------------------------
@app.route('/user/<username>', methods=['GET'])
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    print(user)
    return render_template('user.html', user=user)


# ------------------------------------------ Edit User Profile Page ----------------------------------------------------
@app.route('/<username>/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first()
    form = EditProfileForm(obj=user)
    # ------------------------ Loading the Edit Profile Page -----------------------------------------------------------
    if request.method == 'GET':
        return render_template('edit_profile.html', form=form)
    # ------------------------ Posting the Edit Profile Form -----------------------------------------------------------
    elif request.method == 'POST':
        user.username = form.username.data
        user.email = form.email.data
        user.about_me = form.about_me.data
        if form.validate_on_submit():
            db.session.commit()
            flash('Changes have been accepted!', 'success')
            # ------------------------ If User was in a page -------------------------------------------------------
            next_page = request.args.get('next')  # the next page argument is added to the url after ?next=...

            # ------------------------ Not Valid Next Page or an Attack --------------------------------------------
            if not next_page or url_parse(next_page).netloc != '':
                return redirect(url_for('index'))

            return redirect(url_for(next_page))
        else:
            flash('Something went wrong!', 'danger')
            return render_template('edit_profile.html', form=form)
    else:
        return redirect(url_for('index'))


# ------------------------------------------ Admin Dashboard -----------------------------------------------------------
@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    users = User.query.all()
    # ------------------------ Default Page View -----------------------------------------------------------------------
    if request.method == 'GET':
        return render_template('admin.html', title='Admin Panel', users=users)
    else:
        pass


# ------------------------------------------ Home Page -----------------------------------------------------------------
@app.route('/admin_dashboard/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    users = User.query.all()
    # ------------------------ Default Page View -----------------------------------------------------------------------
    if request.method == 'GET':
        return render_template('admin.html', title='Admin Panel', users=users)
    else:
        pass