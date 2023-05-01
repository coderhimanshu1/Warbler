"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()
        
        user1 = User.signup('user1', 'user1@gmail.com', 'password', None)
        user_id1 = 1001
        user1.id = user_id1
        user2 = User.signup('user2','user2@gmail.com', 'password', None)
        user_id2 = 1002
        user2.id = user_id2
        
        db.session.commit()

        user1 = User.query.get(user_id1)
        user2 = User.query.get(user_id2)

        self.user1 = user1
        self.user_id1 = user_id1

        self.user2 = user2
        self.user_id2 = user_id2
        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    
    # =====================
    # tests for Following
    # =====================
        
    def test_user_follows(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user1.following), 1)

        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)

    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))
   
    
    # =====================
    # Tests for User.signup
    # =====================
    
    def test_signup(self):
        test_user = User.signup("new_test_user", "testt@gmail.com", "password", None)
        user_id = 10009
        test_user.id = user_id
        db.session.commit()

        test_user = User.query.get(user_id)
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user.username, "new_test_user")
        self.assertEqual(test_user.email, "testt@gmail.com")
        self.assertNotEqual(test_user.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(test_user.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None)
        user_id = 3198
        invalid.id = user_id
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("test", None, "password", None)
        user_id = 9876
        invalid.id = user_id
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("test", "email@gmail.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("test", "email@gmail.com", None, None)
    
    # =====================
    # Authentication Tests
    # =====================

    def test_authentication(self):
        user = User.authenticate(self.user1.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user_id1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("invalidusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "invalid"))     
        
    