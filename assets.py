from flask_assets import Bundle
from webassets.filter import get_filter

# Asset object
def getAssets():
    bundles = { 
        'common_css': Bundle(
            'css/ext/bootstrap.min.css',
            'css/common.css',
            'css/navbar.css',
            'css/search_bar.css',
            output='public/common.%(version)s.css',
            filters='cssmin'),
        'common_js': Bundle(
            'js/ext/jquery.min.js',
            'js/ext/bootstrap.min.js',
            output='public/common.%(version)s.js',
            filters='jsmin'),

        'home_css': Bundle(
            'css/home.css',
            output='public/home.%(version)s.css',
            filters='cssmin'),
        'home_js': Bundle(
            'js/home.js',
            output='public/home.%(version)s.js',
            filters='jsmin')
    }
    return bundles
