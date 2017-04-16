import os, json
import MySQLdb
from pymongo import MongoClient
from py2neo import Graph, Node, Relationship
import config

data_file_folder = "./data/"


def main():
    video_data = read_data_files()
    setup_mysql_db(video_data)
    setup_mongo_db(video_data)
    setup_neo4j_db(video_data)


def read_data_files():
    print("Reading data files")
    video_data = []
    global data_file_folder
    if not(data_file_folder.endswith("/")):
        data_file_folder = data_file_folder+"/"
    for fname in os.listdir(data_file_folder):
        with open(data_file_folder+fname,"r") as f:
            parsed = json.loads(f.read())
        video_data.append(parsed)
    print("Files reading done :",len(video_data),"files found")
    print("-"*20)
    return video_data


def setup_mysql_db(video_data):
    cursor = connect_to_db("mysql")
    q = [
          "DROP DATABASE IF EXISTS "+config.mysql_name+";" ,
          "CREATE DATABASE IF NOT EXISTS "+config.mysql_name+";" ,
          "USE "+config.mysql_name+";"
        ]
    print("Inserting data in MySQL . . .")
    for x in q:
        print("Running MySQL :",x)
        cursor.execute(x)
    # Create tables
    # Insert data
    print("MySQL setup done!")
    print("-"*20)


def setup_mongo_db(video_data):
    db = connect_to_db("mongo")
    print("Inserting data in MongoDB . . .")
    db.videos.remove({})
    db.videos.insert_many(video_data)
    print("MongoDB setup done!")
    print("-"*20)


def setup_neo4j_db(video_data):
    neo4j_cursor = connect_to_db("neo4j")
    print("Inserting data in Neo4j . . .")
    neo4j_cursor.delete_all()
    # Insert nodes
    # Insert edges
    print("Neo4j setup done!")
    print("-"*20)


def connect_to_db(db_type):
    print("Connecting to",db_type,"database . . .")
    db_conn = None
    if db_type=="mysql":
        db_conn = MySQLdb.connect(user=config.mysql_user,passwd=config.mysql_pass).cursor()
    elif db_type=="mongo":
        db_conn = MongoClient('localhost', 27017)[config.mongo_name]
    elif db_type=="neo4j":
        db_conn = Graph(user=config.neo4j_user,password=config.neo4j_pass)
    if db_conn==None:
        exit(1)
    print("Database connected")
    print("-"*20)
    return db_conn


main()
