from urllib import parse

from flask import request, render_template, redirect, session

from flaskapp.shared_variables import *
from flaskapp.routes import routes_module
from flaskapp.routes.process import *


# Home page
@routes_module.route("/", methods=["GET"])
def home_page():
    if request.method == "GET":
        lists = [
            fetch_recently_watched_videos(),
            fetch_most_watched_videos()
        ]
        return render_template("home.html", lists=lists)


# Search results page
@routes_module.route("/search/<query>", methods=["GET"])
def search_results_page(query):
    if request.method == "GET":
        query = parse.unquote(query)
        res = fetch_search_results(query)
        return render_template("search.html", query=query,
                               video_results=res["video_results"],
                               channel_results=res["channel_results"])


# Render video by requested Id
@routes_module.route("/watch/<video_id>", methods=["GET"])
def video_page(video_id):
    if request.method == "GET":
        mongo_db = mongo.db
        disp_video = mongo_db.videos.find_one({"id": video_id})
        if disp_video is not None:
            # Update view count of requested video
            mongo_db.videos.update_one(
                {"id": video_id},
                {"$inc": {"statistics.viewCount": 1}},
                upsert=False
            )
            # Add video to user"s recently watched videos
            add_recent_watched_video(disp_video["_id"])
            # Find related videos to the current one
            related_videos = fetch_related_videos(video_id)
            return render_template("watch.html",
                                   display_video=disp_video,
                                   related_videos=related_videos)
        else:
            return render_template("error.html",
                                   message="Requested video not found")


# Channel page
@routes_module.route("/channel/<channel_id>", methods=["GET"])
def channel_page(channel_id):
    if request.method == "GET":
        mongo_db = mongo.db
        # Find most viewed videos of the requested channel
        channel_videos = mongo_db.videos.find({
            "snippet.channelId": channel_id
        }).sort("statistics.viewCount", -1).limit(24)
        channel_videos = list(channel_videos)
        # Check if this channel exists using length of returned results
        if len(channel_videos) > 0:
            channel_name = channel_videos[0]["snippet"]["channelTitle"]
            return render_template("channel.html",
                                   channel_id=channel_id,
                                   channel_name=channel_name,
                                   channel_videos=channel_videos)
        else:
            return render_template("error.html",
                                   message="Requested channel does not exist")


# User recently watched videos page
@routes_module.route("/recently-watched", methods=["GET"])
def recently_watched_page():
    if request.method == "GET":
        if session.get("user_name"):
            lists = [fetch_recently_watched_videos()]
            return render_template("home.html", lists=lists)
        else:
            return redirect("/login")
