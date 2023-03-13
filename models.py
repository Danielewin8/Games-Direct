from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.Text, primary_key=True, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False, default="/static/images/default-pic.png")

    favorites = db.relationship("Favorite", cascade="all, delete", backref="user")

    @classmethod
    def register(cls, username, password, image_url):
        """Registers user info with hashed password"""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, image_url=image_url)

    @classmethod
    def authenticate(cls, username, password):
        """Authentication for username and password at login"""
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)
    game_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    background_image = db.Column(db.Text)


