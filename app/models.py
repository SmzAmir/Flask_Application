from app import db


# ------------------------------------------ User Model ----------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary key
    # relational databases can do efficient search when the attributes are indexed
    username = db.Column(db.String(64), index=True, unique=True)  # we can search user by usernames
    email = db.Column(db.String(120), index=True, unique=True)  # we can email user by usernames
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)