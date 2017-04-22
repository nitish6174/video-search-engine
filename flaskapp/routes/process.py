from flask import session
from bson.objectid import ObjectId
from py2neo import Graph
from sqlalchemy import and_

import flaskapp.config as config
from flaskapp.shared_variables import *
from flaskapp.mysql_schema import User, VideoLog, SearchLog


# Utility function to search
def fetch_search_results(search_query):
    from fuzzywuzzy import fuzz
    mongo_db = mongo.db
    # Fetch all documents
    all_videos = list(mongo_db.videos.find({}))
    # Get list of all video titles
    title_data = dict([(x["snippet"]["title"].lower(), x) for x in all_videos])
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
def fetch_related_videos(video_id):
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


# Fetch most watched videos
def fetch_most_watched_videos():
    mongo_db = mongo.db
    top_videos = list(
        mongo_db.videos.find().sort("statistics.viewCount", -1).limit(12)
    )
    res = {
        "list_title": "Top videos",
        "video_list": top_videos
    }
    return res


# Fetch user's recently watched videos
def fetch_recently_watched_videos():
    recently_watched = []
    if session.get("user_name"):
        mongo_db = mongo.db
        # Fetch array of watched videos of user
        recently_watched = mongo_db.users.find_one(
            {"user_name": session.get("user_name")},
            {"watched_videos": 1}
        )
        if recently_watched is not None:
            # Fetch documents of above found mongo ids
            recently_watched = list(mongo_db.videos.find({
                "_id": {"$in": recently_watched["watched_videos"]}
            }))
    res = {
        "list_title": "Recently watched",
        "video_list": recently_watched
    }
    return res


# Add video to user's recently watched videos
def add_recent_watched_video(video_mongo_id):
    user_name = session.get("user_name")
    if user_name:
        mongo_db = mongo.db
        user_doc = mongo_db.users.find_one(
            {"user_name": user_name},
            {"watched_videos": 1}
        )
        if user_doc is None:
            a = [video_mongo_id]
        else:
            a = user_doc["watched_videos"]
            if video_mongo_id in a:
                a.remove(video_mongo_id)
            a.append(video_mongo_id)
            a = a[:24]
        mongo_db.users.update_one(
            {"user_name": user_name},
            {"$set": {"watched_videos": a}},
            upsert=True
        )


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
