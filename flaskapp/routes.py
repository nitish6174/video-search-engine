from flask import Blueprint, request, render_template, jsonify, redirect, url_for
from bson.objectid import ObjectId
from py2neo import Graph
import flaskapp.config as config
from flaskapp.shared_variables import *
from flaskapp.mysql_schema import User, VideoLog, SearchLog
from sqlalchemy import and_

routes_module = Blueprint('routes_module', __name__)


# Home page showing top videos (and recommended videos if signed in)
@routes_module.route('/', methods=["GET"])
def home_page():
    if request.method == 'GET':
        mongo_db = mongo.db
        top_videos = doc_list(mongo_db.videos.find()
                              .sort("statistics.viewCount", -1).limit(12))
        return render_template('home.html', top_videos=top_videos)


# Render video by requested Id
@routes_module.route('/watch/<video_id>/', methods=["GET"])
def video_page(video_id):
    if request.method == 'GET':
        mongo_db = mongo.db
        disp_video = mongo_db.videos.find_one({"id": video_id})
        if disp_video is not None:
            neo4j_db = Graph(user=config.neo4j_user,
                             password=config.neo4j_pass)
            source_node = neo4j_db.find_one("Video", "videoId", video_id)
            common_tag_edges = [
                rel for rel in
                neo4j_db.match(
                    start_node=source_node,
                    rel_type="CommonTags"
                )
            ]
            related_nodes = [
                {
                    "mongoId": (x.end_node())["mongoId"],
                    "weight": x["weight"]
                }
                for x in common_tag_edges
            ]
            related_nodes.sort(key=lambda x: x["weight"], reverse=True)
            related_nodes = related_nodes[:10]
            mongo_ids = [ObjectId(x["mongoId"]) for x in related_nodes]
            related_videos = doc_list(mongo_db.videos.find({
                "_id": {"$in": mongo_ids}
            }))
            return render_template('watch.html',
                                   display_video=disp_video,
                                   related_videos=related_videos)
        else:
            return render_template('error.html',
                                   message="Requested video not found")


# Login page
@routes_module.route('/login', methods=["GET"])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        form_data = request.form
        if valid_login(form_data['user_name'], form_data['user_pass']):
            return redirect(url_for('/'))


# Sign Up page
@routes_module.route('/signup', methods=["GET", "POST"])
def signup_page():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        form_data = request.form
        user_name = form_data['user_name']
        user_name = form_data['user_pass']
        if user_name and user_pass:
            return create_user(user_name, user_pass)
        else:
            return jsonify({'error': 'User Exists'})


# Utility function to make document array from cursor
def doc_list(doc_cursor):
    return [x for x in doc_cursor]


# mysql_db = mysql
# mongo_db = mongo.db
# neo4j_db = Graph(user=config.neo4j_user,password=config.neo4j_pass)
# test_db(mysql_db,mongo_db,neo4j_db)

def test_db(mysql_db, mongo_db, neo4j_db):
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


@routes_module.route('/log/video', methods=["POST"])
def add_video_log():
    if request.method == "POST":
        new_log = VideoLog(request.form['user_name'],
                      request.form['clicked_video'],
                      request.form['current_video'])
        log_data = repr(new_log)
        try:
            mysql.session.add(new_log)
            mysql.session.commit()
        except Exception as e:
            return jsonify({'error': e})
        else:
            return jsonify(log_data)


@routes_module.route('/log/search', methods=["POST"])
def add_search_log():
    if request.method == "POST":
        new_log = SearchLog(request.form['user_name'],
                      request.form['clicked_video'],
                      request.form['query'])
        log_data = repr(new_log)
        try:
            mysql.session.add(new_log)
            mysql.session.commit()
        except Exception as e:
            return jsonify({'error': e})
        else:
            return jsonify(log_data)


def create_user(user_name, user_pass):
    new_user = User(user_name, user_pass)
    try:
        mysql.session.add(new_user)
        mysql.session.commit()
    except Exception as e:
        return jsonify({'error': e})
    else:
        return jsonify({'response': 'Success'})


def valid_login(user_name, user_pass):
    query = mysql.session.query(User)
    return query.filter(and_(User.user_name == user_name,
                             User.user_pass == user_pass)).count()
