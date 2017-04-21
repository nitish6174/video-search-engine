import os
import shutil

import click
from flask import Flask
from flask_compress import Compress
from flask_assets import Environment

import flaskapp.config as config
import flaskapp.shared_variables as var
from flaskapp.assets import getAssets
from flaskapp.routes import routes_module

# Initialize and configure app
app = Flask(__name__)
app.secret_key = "Sab bik chuke hain"

# Static assets
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = config.static_file_max_age
assets = Environment(app)
assets.register(getAssets())

# Gzip compression
Compress(app)

# MySQL with SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
url = "mysql://" + config.mysql_user + ":" + config.mysql_pass \
      + "@" + "localhost:3306/" + config.mysql_name
app.config["SQLALCHEMY_DATABASE_URI"] = url
var.mysql.init_app(app)

# MongoDB
app.config["MONGO_DBNAME"] = config.mongo_name
var.mongo.init_app(app, config_prefix="MONGO")

# Blueprint routes
app.register_blueprint(routes_module)


# Click command for setting up database
@app.cli.command()
@click.option("--mode", nargs=1, default=0)
def create_db(mode):
    from flaskapp.setup_db import main as init_db
    from flaskapp.mysql_schema import User, VideoLog, SearchLog
    if mode % 2 == 1:
        click.echo("Running database setup script . . .")
        init_db()
    if mode > 1:
        click.echo("Initializing MySQL models . . .")
        var.mysql.create_all()
    if mode > 0:
        click.echo("Database setup done!")
    else:
        click.echo("USAGE : flask create_db --mode <1/2/3>")


# Click command for scaffolding
@app.cli.command()
@click.option("--page", nargs=1)
def scaffold(page):
    template_in = "flaskapp/templates/new_page.html"
    template_out = "flaskapp/templates/" + page + ".html"
    scss_out = "flaskapp/static/scss/" + page + ".scss"
    js_out = "flaskapp/static/js/" + page + ".js"
    # Check whether requested page name already exists
    if os.path.isfile(template_out) \
       or os.path.isfile(scss_out) \
       or os.path.isfile(js_out):
        click.echo("This page name is in conflict with existing files")
    else:
        click.echo("Following files will be created :")
        print("1.", template_out)
        print("2.", scss_out)
        print("3.", js_out)
        # Copy template file
        shutil.copyfile(template_in, template_out)
        # Make new css and js file for this page
        open(scss_out, "w").close()
        open(js_out, "w").close()
        # Set css and js import file names in template file
        with open(template_out) as f:
            text = f.read()
        text = text.replace("page_css", page + "_css")
        text = text.replace("page_js", page + "_js")
        with open(template_out, "w") as f:
            f.write(text)
        click.echo("Done!")
        assets_text = '''"page_css": Bundle(\n''' + \
                      '''    "css/page.css",\n''' + \
                      '''    output="public/page.%(version)s.css",\n''' + \
                      '''    filters="cssmin"),\n''' + \
                      '''"page_js": Bundle(\n''' + \
                      '''    "js/page.js",\n''' + \
                      '''    output="public/page.%(version)s.js",\n''' + \
                      '''    filters="jsmin"),\n'''
        assets_text = assets_text.replace("page", page)
        click.echo("\nAdd the below text in assets.py :\n")
        click.echo(assets_text)


# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0")
