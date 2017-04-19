from flask import Blueprint,request,render_template,redirect
from py2neo import Graph
import config
from shared_variables import *

routes_module = Blueprint('routes_module', __name__)


# Home page showing top videos (and recommended videos if signed in)
@routes_module.route('/', methods=["GET"])
def home_page():
    if request.method == 'GET':
        mongo_db = mongo.db
        top_videos = mongo_db.videos.find().sort("statistics.viewCount",-1).limit(12)
        return render_template('home.html',top_videos=doc_list(top_videos))


# Login page
@routes_module.route('/login', methods=["GET"])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')


# Sign Up page
@routes_module.route('/signup', methods=["GET"])
def signup_page():
    if request.method == 'GET':
        return render_template('signup.html')


# Utility function to make document array from cursor
def doc_list(doc_cursor):
    return [ x for x in doc_cursor ]


# mysql_db = mysql
# mongo_db = mongo.db
# neo4j_db = Graph(user=config.neo4j_user,password=config.neo4j_pass)
# test_db(mysql_db,mongo_db,neo4j_db)

def test_db(mysql_db,mongo_db,neo4j_db):
    # MySQL
    # print(User.query.limit(1).all())
    # MongoDB
    count = mongo_db.videos.count({})
    print(count)
    # Neo4j
    temp = neo4j_db.find_one(config.neo4j_name)
    print(temp)
    # s = "MATCH ()-[r]->() RETURN count(r)"
    # print(neo4j_db.evaluate(statement=s))
