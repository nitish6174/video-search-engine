from flask import request, jsonify, session

from flaskapp.shared_variables import *
from flaskapp.mysql_schema import VideoLog, SearchLog
from flaskapp.routes import routes_module
from flaskapp.routes.process import *
from flaskapp.neo_schema import User, Video


# Suggest videos and channels when searching
@routes_module.route("/suggest", methods=["POST"])
def search_suggestions():
    if request.method == "POST":
        input_query = request.form["input_query"]
        res = fetch_suggestion_results(input_query)
        return jsonify(res)


# Add video to user's watch later list
@routes_module.route("/add-watch-later", methods=["POST"])
def add_watch_later():
    if request.method == "POST":
        doc_id = request.form["doc_id"]
        try:
            res = add_watch_later_video(doc_id)
            res = True
            if res is True:
                return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False})


# Remove video from user's watch later list
@routes_module.route("/remove-watch-later", methods=["POST"])
def remove_watch_later():
    if request.method == "POST":
        doc_id = request.form["doc_id"]
        try:
            res = remove_watch_later_video(doc_id)
            if res is True:
                return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False})


# Store log of click when watching a video
@routes_module.route("/log/video", methods=["POST"])
def add_video_log():
    user_name = session.get("user_name")
    if user is not None:
        if request.method == "POST":
            new_log = VideoLog(user_name,
                               request.form["clicked_video"],
                               request.form["current_video"])
            log_data = repr(new_log)
            try:
                mysql.session.add(new_log)
                mysql.session.commit()
            except Exception as e:
                return jsonify({"error": str(e)})
            else:
                return jsonify(log_data)


# Store log of click from search results
@routes_module.route("/log/search", methods=["POST"])
def add_search_log():
    user_name = session.get("user_name")
    if user is not None:
        if request.method == "POST":
            new_log = SearchLog(user_name,
                                request.form["clicked_video"],
                                request.form["search_query"])
            log_data = repr(new_log)
            try:
                mysql.session.add(new_log)
                mysql.session.commit()
            except Exception as e:
                return jsonify({"error": str(e)})
            else:
                return jsonify(log_data)


@routes_module.route("/like-video", methods=["POST"])
def like_video():
    user = session.get("user_name")
    if user is not None:
        user_obj = User(user)
        if request.method == "POST":
            user_obj.like_video(request.form['videoId'])
            return jsonify({'success': 1})
    return jsonify({'success': 0})


@routes_module.route("/dislike-video", methods=["POST"])
def dislike_video():
    user = session.get("user_name")
    if user is not None:
        user_obj = User(user)
        if request.method == "POST":
            user_obj.dislike_video(request.form['videoId'])
            return jsonify({'success': 1})
    return jsonify({'success': 0})


@routes_module.route("/clear-like", methods=["POST"])
def clear_like_video():
    user = session.get("user_name")
    if user is not None:
        user_obj = User(user)
        if request.method == "POST":
            user_obj.clear_rel_with_video(request.form['videoId'])
            return jsonify({'success': 1})
    return jsonify({'success': 0})


@routes_module.route("/check-interaction/<action_type>", methods=["POST"])
def check_action_status(action_type):
    user = session.get("user_name")
    if user is not None:
        user_obj = User(user)
        if request.method == "POST":
            if action_type == 'like':
                val = user_obj.is_liked_video(request.form['videoId'])
            elif action_type == 'dislike':
                val = user_obj.is_disliked_video(request.form['videoId'])
            elif action_type == 'subscribe':
                val = user_obj.is_subscribed(request.form['channelId'])
            return jsonify({'success': 1, "val": val})
    return jsonify({'success': 0})


@routes_module.route("/subscribe-channel", methods=["POST"])
def subscribe():
    user = session.get("user_name")
    if user is not None:
        user_obj = User(user)
        if request.method == "POST":
            user_obj.subscribe(request.form['channelId'])
            return jsonify({'success': 1})
    return jsonify({'success': 0})


@routes_module.route("/unsubscribe-channel", methods=["POST"])
def unsubscribe():
    user = session.get("user_name")
    if user is not None:
        user_obj = User(user)
        if request.method == "POST":
            user_obj.unsubscribe(request.form['channelId'])
            return jsonify({'success': 1})
    return jsonify({'success': 0})


@routes_module.route("/get-count", methods=["POST"])
def get_count():
    obj = Video(request.form['videoId'])
    if request.method == "POST":
        lc = obj.liked_by_count()
        dlc = obj.disliked_by_count()
        return jsonify({'success': 1, "lc": lc, "dlc": dlc})
