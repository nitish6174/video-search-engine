from shared_variables import mysql as db


class User(db.Model):
    user_name = db.Column(db.String(30), unique=True, primary_key=True)
    user_pass = db.Column(db.String(30))

    def __init__(self, user_name, user_pass):
        self.user_name = user_name
        self.user_pass = user_pass

    def __repr__(self):
        return '<User %r>' % self.user_name
