import os
import sys
import json
import sqlalchemy as sql
from pymongo import MongoClient
from py2neo import authenticate, Graph, Node, Relationship
import flaskapp.config as config

data_file_folder = "./data/"


# Main function
def main():
    video_data = read_data_files()
    setup_mysql_db(video_data)
    mongo_ids = setup_mongo_db(video_data)
    setup_neo4j_db(video_data, mongo_ids)


# Store videoInfo from data files into an array
def read_data_files():
    print("Reading data files . . . ", end="")
    sys.stdout.flush()
    video_data = []
    global data_file_folder
    if not(data_file_folder.endswith("/")):
        data_file_folder = data_file_folder + "/"
    for fname in os.listdir(data_file_folder):
        with open(data_file_folder + fname, "r") as f:
            parsed = json.loads(f.read())
        video_data.append(parsed)
    print("Done!")
    for i in range(len(video_data)):
        video_data[i] = video_data[i]["videoInfo"]
        for x in video_data[i]["statistics"]:
            video_data[i]["statistics"][x] = int(
                video_data[i]["statistics"][x])
    print("Files found :", len(video_data))
    print("-" * 40)
    return video_data


# Define schema for MySQL
def setup_mysql_db(video_data):
    db = connect_to_db("mysql")
    # Define schema
    print("MySQL setup completed")
    print("-" * 40)


# Insert videoInfo in MongoDB
def setup_mongo_db(video_data):
    db = connect_to_db("mongo")
    print("Clearing existing data . . . ", end="")
    sys.stdout.flush()
    db.videos.remove({})
    print("Done!")
    print("Inserting data in MongoDB . . . ", end="")
    sys.stdout.flush()
    res = db.videos.insert_many(video_data)
    print("Done!")
    print("MongoDB setup completed")
    print("-" * 40)
    return res.inserted_ids


# Make graph relations in Neo4j using MongoDB document ids
def setup_neo4j_db(video_data, mongo_ids):
    db = connect_to_db("neo4j")
    print("Clearing existing data . . . ", end="")
    sys.stdout.flush()
    db.delete_all()
    print("Done!")
    insert_graph_data(db, video_data, mongo_ids)
    print("Neo4j setup completed")
    print("-" * 40)


# Connect to database
def connect_to_db(db_type):
    print("Connecting to", db_type, "database . . . ", end="")
    sys.stdout.flush()
    db_conn = None
    try:
        if db_type == "mysql":
            url = "mysql://" + config.mysql_user + ":" + config.mysql_pass \
                  + "@" + "localhost:3306/" + config.mysql_name
            db_conn = sql.create_engine(url)
            # db_conn = MySQLdb.connect(user=config.mysql_user, \
            #                           passwd=config.mysql_pass).cursor()
        elif db_type == "mongo":
            db_conn = MongoClient('localhost', 27017)[config.mongo_name]
        elif db_type == "neo4j":
            authenticate('localhost:7474',
                         config.neo4j_user, config.neo4j_pass)
            db_conn = Graph()
            # db_conn = Graph(user=config.neo4j_user,
            #                 password=config.neo4j_pass)
    except:
        print("\n\nERROR : Can't connect to database")
    if db_conn is None:
        exit(1)
    print("Done!")
    return db_conn


# Neo4j utility to insert graph data
def insert_graph_data(db, video_data, mongo_ids):
    l = len(video_data)
    node_list = []
    # Insert videoId and corresponding mongoId as a node
    print("Creating nodes . . . ", end="")
    sys.stdout.flush()
    tx = db.begin()
    for (obj, mongo_id) in zip(video_data, mongo_ids):
        node = Node("Video", videoId=obj["id"], mongoId=str(mongo_id))
        node_list.append(node)
        tx.create(node)
    print("Done!")
    print("Commiting the nodes . . . ", end="")
    sys.stdout.flush()
    tx.commit()
    print("Done!")
    # Loop through each video and add edges with related videos
    print("Creating edges . . . ", end="\r")
    sys.stdout.flush()
    for i in range(l):
        tx = db.begin()
        u = node_list[i]
        d1 = video_data[i]
        for j in range(i + 1, l):
            v = node_list[j]
            d2 = video_data[j]
            # Same channel relation
            if d1["snippet"]["channelId"] == d2["snippet"]["channelId"]:
                tx.create(Relationship(u, "SameChannel", v))
                tx.create(Relationship(v, "SameChannel", u))
            # Common tag relation
            common_tags = commonTagCount(d1["snippet"], d2["snippet"])
            if common_tags > 0:
                tx.create(Relationship(u, "CommonTags", v, weight=common_tags))
                tx.create(Relationship(v, "CommonTags", u, weight=common_tags))
            # Common description relation
            common_desc = commonDescription(d1["snippet"], d2["snippet"])
            if common_desc > 0:
                tx.create(Relationship(u, "CommonDesc", v, weight=common_desc))
                tx.create(Relationship(v, "CommonDesc", u, weight=common_desc))
        tx.commit()
        print("Creating edges . . . {}%".format(int(i * 100 / l)), end="\r")
        sys.stdout.flush()
    print("Creating edges . . . Done!")


# Find no of common tags b/w 2 videos
def commonTagCount(x, y):
    if ("tags" in x) and ("tags" in y):
        return len(set(x["tags"]) & set(y["tags"]))
    return 0


# Find no of common words b/w 2 videos
def commonDescription(x, y):
    reject_list = set([line.rstrip('\n') for line in open("common_words.txt")])
    desc1 = wordsInDescription(x["description"])
    desc2 = wordsInDescription(y["description"])
    common_set = (desc1 & desc2) - (reject_list)
    return len(common_set)


# Utility function to return set of words in a description
def wordsInDescription(s):
    a = list(map(lambda x: x.lower(), s.split()))
    a = filter(lambda x: len(x) > 2 and len(x) < 15, a)
    return set(a)


# Run main function
main()
