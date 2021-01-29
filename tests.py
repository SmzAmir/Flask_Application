from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post


class UserModelTest(unittest.TestCase):
    def setUp(self):
        # create a db in the memory
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='test')
        u.set_password(password='test1')
        self.assertTrue(u.check_password(password='test1'))
        self.assertFalse(u.check_password(password='test2'))

    def test_avatar(self):
        u = User(username='test', email='test@example.com')
        self.assertEqual(first=u.avatar(size=128),
                         second='https://www.gravatar.com/avatar/'
                                '55502f40dc8b7c769880b10874abc9d0'
                                '?d=identicon&s=128')

    def test_follow(self):
        user_1 = User(username='test1', email='test1@example.com')
        user_2 = User(username='test2', email='test2@example.com')
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()

        self.assertEqual(first=user_1.followed.all(), second=[])  # no following at the beginning
        self.assertEqual(first=user_2.followed.all(), second=[])  # no following at the beginning

        user_1.follow(user_2)
        db.session.commit()
        self.assertTrue(user_1.is_following(user_2))
        self.assertEqual(first=user_1.followed.count(), second=1)  # user_1 has one followed
        self.assertEqual(first=user_1.followed.first().username, second='test2')
        self.assertEqual(first=user_2.followers.count(), second=1)
        self.assertEqual(first=user_2.followers.first().username, second='test1')

        user_1.unfollow(user_2)
        db.session.commit()
        self.assertFalse(user_1.is_following(user_2))
        self.assertEqual(first=user_1.followed.count(), second=0)
        self.assertEqual(first=user_2.followers.count(), second=0)

    def test_follow_posts(self):
        # create four users
        user_1 = User(username='user_1', email='user_1@example.com')
        user_2 = User(username='user_2', email='user_2@example.com')
        user_3 = User(username='user_3', email='user_3@example.com')
        user_4 = User(username='user_4', email='user_4@example.com')
        db.session.add_all([user_1, user_2, user_3, user_4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from user_1", author=user_1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from user_2", author=user_2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from user_3", author=user_3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from user_4", author=user_4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        user_1.follow(user_2)  # user_1 follows user_2
        user_1.follow(user_4)  # user_1 follows user_4
        user_2.follow(user_3)  # user_2 follows user_3
        user_3.follow(user_4)  # user_3 follows user_4
        db.session.commit()

        # check the followed posts of each user
        f1 = user_1.followed_posts().all()
        f2 = user_2.followed_posts().all()
        f3 = user_3.followed_posts().all()
        f4 = user_4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
