import datetime
from flaskapp.shared_variables import mysql as db


class User(db.Model):
    user_name = db.Column(db.String(30), unique=True, primary_key=True)
    user_pass = db.Column(db.String(30))

    def __init__(self, user_name, user_pass):
        self.user_name = user_name
        self.user_pass = user_pass

    def __repr__(self):
        return '<User %r>' % self.user_name


class Log(db.Model):
    timestamp = db.Column(db.DateTime(), primary_key=True)
    user_name = db.Column(db.String(30), primary_key=True)
    current_video = db.Column(db.String(30))
    clicked_video = db.Column(db.String(30))

    def __init__(self, user_name, current_video, clicked_video):
        self.timestamp = datetime.datetime.now()
        self.user_name = user_name
        self.current_video = current_video
        self.clicked_video = clicked_video

    def __repr__(self):
        return "Log %s User %s" % (self.timestamp, self.user_name)

    def data(self):
        return {
                'timestamp': self.timestamp,
                'username': self.user_name,
                }
