from flask import Blueprint,request,render_template,redirect
from py2neo import Graph
import config
from shared_variables import *
from mysql_schema import *

routes_module = Blueprint('routes_module', __name__)


@routes_module.route('/', methods=["GET"])
def homePage():
    if request.method == 'GET':
        mysql_db = mysql
        mongo_db = mongo.db
        neo4j_db = Graph(user=config.neo4j_user,password=config.neo4j_pass)
        # test_db(mysql_db,mongo_db,neo4j_db)
        return render_template('home.html')


def test_db(mysql_db,mongo_db,neo4j_db):
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
