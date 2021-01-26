from datetime import datetime
from hashlib import md5
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin  # make any class compatible with flask-login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
)


# ------------------------------------------ User Model ----------------------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary key
    # relational databases can do efficient search when the attributes are indexed
    username = db.Column(db.String(64), index=True, unique=True)  # we can search user by usernames
    email = db.Column(db.String(120), index=True, unique=True)  # we can email user by usernames
    password_hash = db.Column(db.String(128))
    posts = db.relation('Post', backref='author', lazy='dynamic')  # Define relation between User and Post class
                                                                   # backref adds attribute author to the posts
                                                                   # lazy='dynamic' makes the "posts" a query rather than a list
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),  # left side
        secondaryjoin=(followers.c.followed_id == id),  # right side
        backref=db.backref('followers', lazy='dynamic'),  # right side
        lazy='dynamic'  # left side
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size
        )

    def follow(self, user):
        if not self.is_following(user):  # avoid duplicate relationships for the same pair of users
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):  # if only user is following the other user then remove it
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0


# ------------------------------------------ Post Model ----------------------------------------------------------------
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Make User.id the foreign key for the posts

    def __repr__(self):
        return '<Post {}>'.format(self.body)


# For login session this function gets the user-id and returns the User object for the flask-login module
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
