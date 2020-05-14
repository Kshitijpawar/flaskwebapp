# from mongoengine import *
from datetime import datetime
from flaskblog import login_manager, db
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id= user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(max_length= 30, required= True, unique= True)
    email = db.EmailField(maxlenght= 120, required= True, unique= True)
    image_file = db.StringField(max_length= 50, default= 'default.jpg')
    password = db.StringField(max_length= 60, min_length = 8)
    posts = db.ReferenceField('Post')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Document):
    title = db.StringField(max_length= 100)
    date_posted = db.DateTimeField(default= datetime.utcnow)
    content = db.StringField()
    user_id = db.ReferenceField(User)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.user_id}')"

class Moviesdb(db.Document):
    movieId = db.IntField()
    title = db.StringField()
    genres = db.ListField(db.StringField())
    year = db.IntField()

    def __repr__(self):
        return f"Moviesdb('{self.title}', '{self.genres}', '{self.year}')"

class Ratings(db.Document):
    userId = db.ReferenceField(User)
    movieId = db.ReferenceField(Moviesdb)
    rating = db.FloatField(max_value= 10, min_value= 0)

    def __repr__(self):
        return f"Moviesdb('{self.userId}', '{self.movieId}', '{self.rating}')"
