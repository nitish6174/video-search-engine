import datetime
from flaskapp.shared_variables import mysql as db


class User(db.Model):
    user_name = db.Column(db.String(30), unique=True, primary_key=True)
    user_pass = db.Column(db.String(30))

    def __init__(self, user_name, user_pass):
        self.user_name = user_name
        self.user_pass = user_pass

    def __repr__(self):
        return "User %r" % self.user_name


class Log(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    user_name = db.Column(db.String(30), primary_key=True)
    clicked_video = db.Column(db.String(30))

    def __init__(self, user_name, clicked_video):
        self.timestamp = datetime.datetime.now()
        self.user_name = user_name
        self.clicked_video = clicked_video

    def __repr__(self):
        return "Log %r User %r" % (self.timestamp, self.user_name)


class VideoLog(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    user_name = db.Column(db.String(30), primary_key=True)
    current_video = db.Column(db.String(30), primary_key=True)
    clicked_video = db.Column(db.String(30))

    def __init__(self, user_name, clicked_video, current_video):
        self.timestamp = datetime.datetime.now()
        self.user_name = user_name
        self.clicked_video = clicked_video
        self.current_video = current_video

    def __repr__(self):
        return "VideoLog %r User %r Current Video %r" % (self.timestamp,
                                                         self.user_name,
                                                         self.current_video)


class SearchLog(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    user_name = db.Column(db.String(30), primary_key=True)
    query = db.Column(db.String(3000))
    clicked_video = db.Column(db.String(30))

    def __init__(self, user_name, clicked_video, query):
        self.timestamp = datetime.datetime.now()
        self.user_name = user_name
        self.clicked_video = clicked_video
        self.query = query

    def __repr__(self):
        return "SearchLog %r User %r Query %r" % (self.timestamp,
                                                  self.user_name,
                                                  self.query)
