from urllib import parse

from flask import Blueprint, request, render_template, \
    jsonify, redirect, session
from bson.objectid import ObjectId
from py2neo import Graph
from sqlalchemy import and_

import flaskapp.config as config
from flaskapp.shared_variables import *
from flaskapp.mysql_schema import User, VideoLog, SearchLog

routes_module = Blueprint('routes_module', __name__)


# Home page
@routes_module.route('/', methods=["GET"])
def home_page():
    if request.method == 'GET':
        mongo_db = mongo.db
        # Find most viewed videos
        top_videos = list(
            mongo_db.videos.find().sort("statistics.viewCount", -1).limit(12)
        )
        return render_template('home.html', top_videos=top_videos)


# Render video by requested Id
@routes_module.route('/watch/<video_id>/', methods=["GET"])
def video_page(video_id):
    if request.method == 'GET':
        mongo_db = mongo.db
        disp_video = mongo_db.videos.find_one({"id": video_id})
        if disp_video is not None:
            # Update view count of requested video
            mongo_db.videos.update_one(
                {'id': video_id},
                {'$inc': {'statistics.viewCount': 1}},
                upsert=False
            )
            # Find related videos to the current one
            related_videos = get_related_videos(video_id)
            return render_template('watch.html',
                                   display_video=disp_video,
                                   related_videos=related_videos)
        else:
            return render_template('error.html',
                                   message="Requested video not found")


# Channel page
@routes_module.route('/channel/<channel_id>/', methods=["GET"])
def channel_page(channel_id):
    if request.method == 'GET':
        mongo_db = mongo.db
        # Find most viewed videos of the requested channel
        channel_videos = mongo_db.videos.find({
            "snippet.channelId": channel_id
        }).sort("statistics.viewCount", -1).limit(24)
        channel_videos = list(channel_videos)
        # Check if this channel exists using length of returned results
        if len(channel_videos) > 0:
            channel_name = channel_videos[0]["snippet"]["channelTitle"]
            return render_template('channel.html',
                                   channel_id=channel_id,
                                   channel_name=channel_name,
                                   channel_videos=channel_videos)
        else:
            return render_template('error.html',
                                   message="Requested channel does not exist")


# Search results page
@routes_module.route('/search/<query>/', methods=["GET"])
def search_results_page(query):
    if request.method == 'GET':
        query = parse.unquote(query)
        res = search_util(query)
        return render_template('search.html', query=query,
                               video_results=res["video_results"],
                               channel_results=res["channel_results"])


# Search for a query
@routes_module.route('/search/', methods=["POST"])
def search_bar(query):
    if request.method == 'POST':
        query = parse.unquote(query)
        res = search_util(query)
        return jsonify(res)


# Login page
@routes_module.route('/login', methods=["GET", "POST"])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        form_data = request.form
        if valid_login(form_data['user_name'], form_data['user_pass']):
            session["user_name"] = form_data['user_name']
            return redirect('/')
        else:
            return render_template("error.html", message="Invalid user")


# Sign Up page
@routes_module.route('/signup', methods=["GET", "POST"])
def signup_page():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        form_data = request.form
        user_name = form_data['user_name']
        user_pass = form_data['user_pass']
        confirm_user_pass = form_data['confirm_user_pass']
        if(user_pass != confirm_user_pass):
            return render_template('error.html',
                                   message="Passwords do not match")
        if user_name and user_pass:
            res = create_user(user_name, user_pass)
            if(res == "Success"):
                session["user_name"] = user_name
                return redirect("/")
            else:
                return render_template("error.html", message=res)
        else:
            return render_template('error.html',
                                   message="All the fields are necessary")


# Logout page
@routes_module.route('/logout', methods=["GET"])
def logout_page():
    if request.method == "GET":
        session.pop('user_name', None)
        return redirect('/')


# Store log of click when watching a video
@routes_module.route('/log/video', methods=["POST"])
def add_video_log():
    user_name = session.get('user_name') or "anon"
    if request.method == "POST":
        new_log = VideoLog(user_name,
                           request.form['clicked_video'],
                           request.form['current_video'])
        log_data = repr(new_log)
        try:
            mysql.session.add(new_log)
            mysql.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)})
        else:
            return jsonify(log_data)


# Store log of click from search results
@routes_module.route('/log/search', methods=["POST"])
def add_search_log():
    user_name = session.get('user_name') or "anon"
    if request.method == "POST":
        new_log = SearchLog(user_name,
                            request.form['clicked_video'],
                            request.form['search_query'])
        log_data = repr(new_log)
        try:
            mysql.session.add(new_log)
            mysql.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)})
        else:
            return jsonify(log_data)


# Utility function to search
def search_util(search_query):
    from fuzzywuzzy import fuzz
    mongo_db = mongo.db
    # Fetch all documents
    all_videos = list(mongo_db.videos.find({}))
    # Get list of all video titles
    title_data = dict([(x['snippet']['title'].lower(), x) for x in all_videos])
    # Fetch all channel names
    channel_data = {}
    for x in all_videos:
        channel_id = x["snippet"]["channelId"]
        if channel_id not in channel_data:
            channel_data[channel_id] = {"name": x["snippet"]["channelTitle"]}
    # Break search query into lowercase words
    query_words = search_query.lower().split()
    # Calculate score of each video title using fuzzy matching
    video_results = []
    for key in title_data:
        score = 0
        for q in query_words:
            inc = fuzz.partial_ratio(q, key)
            if inc == 100:
                inc += len(q) * 20
            score += inc
        video_results.append([score, title_data[key]])
    # Calculate score of each channel name using fuzzy matching
    channel_results = []
    for key in channel_data:
        score = 0
        for q in query_words:
            inc = fuzz.partial_ratio(q, channel_data[key]["name"])
            if inc == 100:
                inc += len(q) * 20
            score += inc
        channel_results.append([score, {
            "channelId": key, "channelTitle": channel_data[key]["name"]
        }])
    # Add click log weightage to video result scores
    if session.get("user_name"):
        temp_res = {}
        for x in video_results:
            temp_res[x[1]["id"]] = {"0": x[0], "1": x[1]}
        log_res = SearchLog.query.filter_by(
            user_name=session.get("user_name"),
            search_query=search_query).all()
        for x in log_res:
            related_video_id = x.clicked_video
            if related_video_id in temp_res:
                temp_res[related_video_id]["0"] += 5
        video_results = [
            [temp_res[x]["0"], temp_res[x]["1"]]
            for x in temp_res
        ]
    # Sort results by score and return data
    video_results.sort(key=lambda x: x[0], reverse=True)
    channel_results.sort(key=lambda x: x[0], reverse=True)
    result = {
        "video_results": [x[1] for x in video_results[:24]],
        "channel_results": [x[1] for x in channel_results[:12]]
    }
    return result


# Find videos related to a particular video
def get_related_videos(video_id):
    mongo_db = mongo.db
    neo4j_db = Graph(user=config.neo4j_user,
                     password=config.neo4j_pass)
    # Find node corresponding to current video
    source_node = neo4j_db.find_one("Video", "videoId", video_id)
    # Get all edges from current node
    rel_edges = [
        rel for rel in
        neo4j_db.match(
            start_node=source_node
        )
    ]
    # Loop through each edge and update score of end node
    edge_end_nodes = {}
    for x in rel_edges:
        if x.type() == "SameChannel":
            weight = 5
        elif x.type() == "CommonTags":
            weight = 3 * x["weight"]
        elif x.type() == "CommonDesc":
            weight = x["weight"]
        mongo_id = (x.end_node())["mongoId"]
        related_id = (x.end_node())["videoId"]
        if related_id in edge_end_nodes:
            edge_end_nodes[related_id]["weight"] += weight
        else:
            edge_end_nodes[related_id] = {
                "mongoId": mongo_id,
                "weight": weight
            }
    # Add click log weightage to above score
    if session.get("user_name"):
        log_res = VideoLog.query.filter_by(
            user_name=session.get("user_name"),
            current_video=video_id).all()
        for x in log_res:
            related_video_id = x.clicked_video
            if related_video_id in edge_end_nodes:
                edge_end_nodes[related_video_id]["weight"] += 2
    # Construct array of related videos from above found nodes
    related_nodes = [
        {
            "videoId": x,
            "mongoId": edge_end_nodes[x]["mongoId"],
            "weight": edge_end_nodes[x]["weight"]
        }
        for x in edge_end_nodes
    ]
    # Filter top weighted nodes to get most relevant videos
    related_nodes.sort(key=lambda x: x["weight"], reverse=True)
    related_nodes = related_nodes[:10]
    # Fetch data of these videos from MongoDB
    mongo_ids = [ObjectId(x["mongoId"]) for x in related_nodes]
    related_videos = list(mongo_db.videos.find({
        "_id": {"$in": mongo_ids}
    }))
    # Sort the fetched documents using score found above
    for x in related_videos:
        x["weight"] = edge_end_nodes[x["id"]]["weight"]
    related_videos.sort(key=lambda x: x["weight"], reverse=True)
    return related_videos


# Create new user account
def create_user(user_name, user_pass):
    new_user = User(user_name, user_pass)
    try:
        mysql.session.add(new_user)
        mysql.session.commit()
    except:
        return "User already exists"
    else:
        return "Success"


# Find login attempt result
def valid_login(user_name, user_pass):
    query = mysql.session.query(User)
    return bool(query.filter(and_(User.user_name == user_name,
                             User.user_pass == user_pass)).count())
