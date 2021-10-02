from datetime import timezone
from flask_sqlalchemy import SQLAlchemy
from src import app
from src.auth import login_manager, UserMixin

db = SQLAlchemy(app)

# class LocalData(db.Model):
#     __tablename__ = 'Local Data'
#     id = db.Column(db.Integer, primary_key=True)
#     city = db.Column(db.String(25))
#     country = db.Column(db.String(25))
#     longitude = db.Column(db.Float(20))
#     latitude = db.Column(db.Float(20))
#     datetime = db.Column(db.DateTime(timezone=True))
#     landslide = db.Column(db.Boolean())
    
#     def __init__(self, city=None, country=None):
#         pass

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30), unique=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))