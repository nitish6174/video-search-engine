from flask_assets import Bundle


# Asset object
def getAssets():
    bundles = {
        "common_css": Bundle(
            "css/ext/bootstrap.min.css",
            "css/common.css",
            "css/navbar.css",
            "css/search_bar.css",
            output="public/common.%(version)s.css",
            filters="cssmin"),
        "common_js": Bundle(
            "js/ext/jquery.min.js",
            "js/ext/bootstrap.min.js",
            "js/common.js",
            output="public/common.%(version)s.js",
            filters="jsmin"),

        "home_css": Bundle(
            "css/home.css",
            output="public/home.%(version)s.css",
            filters="cssmin"),
        "home_js": Bundle(
            "js/home.js",
            output="public/home.%(version)s.js",
            filters="jsmin"),

        "watch_css": Bundle(
            "css/watch.css",
            output="public/watch.%(version)s.css",
            filters="cssmin"),
        "watch_js": Bundle(
            "js/watch.js",
            output="public/watch.%(version)s.js",
            filters="jsmin"),

        "channel_css": Bundle(
            "css/channel.css",
            output="public/channel.%(version)s.css",
            filters="cssmin"),
        "channel_js": Bundle(
            "js/channel.js",
            output="public/channel.%(version)s.js",
            filters="jsmin"),

        "search_css": Bundle(
            "css/search.css",
            output="public/search.%(version)s.css",
            filters="cssmin"),
        "search_js": Bundle(
            "js/search.js",
            output="public/search.%(version)s.js",
            filters="jsmin"),

        "user_css": Bundle(
            "css/user.css",
            output="public/user.%(version)s.css",
            filters="cssmin"),
        "user_js": Bundle(
            "js/user.js",
            output="public/user.%(version)s.js",
            filters="jsmin"),

        "error_css": Bundle(
            "css/error.css",
            output="public/error.%(version)s.css",
            filters="cssmin"),
        "error_js": Bundle(
            "js/error.js",
            output="public/error.%(version)s.js",
            filters="jsmin")
    }
    return bundles
