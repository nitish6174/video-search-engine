from flask import Blueprint,request,render_template,redirect
from py2neo import Graph
import config
from shared_variables import *

routes_module = Blueprint('routes_module', __name__)


@routes_module.route('/', methods=["GET"])
def homePage():
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        db = mongo.db
        graph = Graph(user=config.neo4j_user,password=config.neo4j_pass)
        # test_db(cursor,db,graph)
        return render_template('home.html')


def test_db(cursor,db,graph):
    # q = "SELECT COUNT(*) FROM `videos`;"
    # print(cursor.execute(q))
    count = db.videos.count({})
    print(count)
    temp = graph.find_one(config.neo4j_name)
    print(temp)
    # s = "MATCH ()-[r]->() RETURN count(r)"
    # print(graph.evaluate(statement=s))
