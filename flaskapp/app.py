import subprocess

import click
from flask import Flask
from flask_compress import Compress
from flask_assets import Environment

import flaskapp.config as config
import flaskapp.shared_variables as var
from flaskapp.assets import getAssets
from flaskapp.routes import routes_module
from flaskapp.setup_db import main as init_db

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
url = "mysql://" + config.mysql_user + ":" + config.mysql_pass \
      + "@" + "localhost:3306/" + config.mysql_name
app.config['SQLALCHEMY_DATABASE_URI'] = url
var.mysql.init_app(app)

# MongoDB
app.config['MONGO_DBNAME'] = config.mongo_name
var.mongo.init_app(app, config_prefix='MONGO')

# Blueprint routes
app.register_blueprint(routes_module)


@app.cli.command()
def create_db():
    init_db()
    var.mysql.create_all()
    click.echo('Creating DB')


# Run app
if __name__ == '__main__':
    app.run(host='0.0.0.0')
