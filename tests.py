import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, connect_db, User, Favorite

os.environ['DATABASE_URL'] = "postgresql:///GamesDB"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    def setUp(self):

        Favorite.query.delete()
        User.query.delete()

        self.client = app.test_client()

        db.session.commit()

    def test_user_model(self):
        '''Testing user model'''

        user = User.register(username='Test1', password='Test1')

        db.session.add(user)
        db.session.commit()
        
        users = User.query.all()

        self.assertEqual(len(users), 1)

        try:
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError:
            self.assertRaises(exc.IntegrityError)

    def test_authenticate(self):

        user = User.register(username='Test1', password='Test1')

        db.session.add(user)
        db.session.commit()

        username = 'Test1'
        password = 'Test1'

        user = User.authenticate(username, password)

        self.assertFalse(user)

    def test_favorite(self):

        user = User.register(username='Test1',password='Test1')

        db.session.add(user)
        db.session.commit()

        favorite = Favorite(username='Test1', game_slug='elden-ring')

        db.session.add(favorite)
        db.session.commit()

        favorites = Favorite.query.all()

        self.assertEqual(len(favorites), 1)
