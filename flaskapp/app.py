from flask import Flask,request,send_from_directory
from flask_compress import Compress
from flask_assets import Bundle, Environment
from flask_scss import Scss

import config
import shared_variables as var
from assets import getAssets
from routes import routes_module

# Initialize and configure app
app = Flask(__name__)

# Static assets
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = config.static_file_max_age
assets = Environment(app)
assets.register(getAssets())

# Gzip compression
Compress(app)

# MySQL with SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
url = "mysql://"+config.mysql_user+":"+config.mysql_pass \
      +"@"+"localhost:3306/"+config.mysql_name
app.config['SQLALCHEMY_DATABASE_URI'] = url
var.mysql.init_app(app)

# MongoDB
app.config['MONGO_DBNAME'] = config.mongo_name
var.mongo.init_app(app,config_prefix='MONGO')

# Blueprint routes
app.register_blueprint(routes_module)

# Run app
if __name__ == '__main__':
    app.run(host='0.0.0.0')
