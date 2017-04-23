from py2neo import authenticate, Graph, Node, Relationship
from datetime import datetime
import os
import uuid

import flaskapp.config as config

# url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
# username = os.environ.get('NEO4J_USERNAME')
# password = os.environ.get('NEO4J_PASSWORD')
# graph = Graph(url + '/db/data/', username=username, password=password)

authenticate("localhost:7474", config.neo4j_user, config.neo4j_pass)
graph = Graph()


class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one('User', 'username', self.username)
        return user

    def subscribe(self, channel_name):
        if not self.is_subscribed(channel_name):
            Channel(channel_name).subscribe(self.find())
            return True
        return False

    def is_subscribed(self, channel_name):
        query = """
        MATCH (n:User)-[r]-(v:Channel)
        WHERE n.username={user} and v.channelId={vid}
        RETURN COUNT(r) as count
        """
        return graph.data(query, user=self.find()['username'], vid=channel_name)[0]['count']

    def unsubscribe(self, channel_name):
        query = """
        MATCH (n:User)-[r]-(v:Channel)
        WHERE n.username={user} and v.channelId={vid}
        DELETE r
        """
        graph.run(query, user=self.find()['username'], vid=channel_name)

    def register(self):
        if not self.find():
            user = Node('User', username=self.username)
            graph.create(user)
            return True
        else:
            return False

    def like_video(self, video_id):
        user = self.find()
        Video(video_id).like(user)

    def dislike_video(self, video_id):
        user = self.find()
        Video(video_id).dislike(user)

    def is_liked_video(self, video_id):
        query = """
        MATCH (n:User)-[r:Likes]-(v:Video)
        WHERE n.username={user} and v.videoId={vid}
        RETURN COUNT(r) as count
        """
        return graph.data(query, user=self.find()['username'], vid=video_id)[0]['count']

    def is_disliked_video(self, video_id):
        query = """
        MATCH (n:User)-[r:Dislikes]-(v:Video)
        WHERE n.username={user} and v.videoId={vid}
        RETURN COUNT(r) as count
        """
        return graph.data(query, user=self.find()['username'], vid=video_id)[0]['count']

    def clear_rel_with_video(self, video_id):
        user = self.find()
        Video(video_id).clear_user_rel(user)

    def liked_videos(self):
        query = '''
        MATCH (user:User)-[:Likes]-(video:Video)
        WHERE user.username = {user}
        RETURN DISTINCT video.mongoId
        '''
        return graph.data(query, user=self.username)

    def disliked_videos(self):
        query = '''
        MATCH (user:User)-[:Dislikes]-(video:Video)
        WHERE user.username = {user}
        RETURN DISTINCT video.mongoId
        '''
        return graph.data(query, user=self.username)


class Channel:

    def __init__(self, channel_name):
        self.name = channel_name

    def find(self):
        channel = graph.find_one('Channel', 'channelId', self.name)
        return channel

    def subscribers(self):
        query = '''
        MATCH (user:User)-[:Subscriber]-(channel:Channel)
        WHERE channel.channelId = {channel}
        RETURN DISTINCT user.username
        '''
        return graph.run(query, channel=self.name)

    def subscriber_count(self):
        query = '''
        MATCH (user:User)-[:Subscriber]-(channel:Channel)
        WHERE channel.channelId = {channel}
        RETURN COUNT(DISTINCT user)
        '''
        return graph.run(query, channel=self.name)

    def video_count(self):
        query = '''
        MATCH (video:Video)-[:HasChannel]-(channel:Channel)
        WHERE channel.channelId = {channel}
        RETURN COUNT(DISTINCT video)
        '''
        return graph.run(query, channel=self.name)

    def videos(self):
        query = '''
        MATCH (video:Video)-[:HasChannel]-(channel:Channel)
        WHERE channel.channelId = {channel}
        RETURN DISTINCT video.videoId
        '''
        return graph.run(query, channel=self.name)

    def subscribe(self, user):
        graph.create(Relationship(user, "Subscriber", self.find()))


class Video:

    def __init__(self, id_):
        self.id = id_

    def find(self):
        video = graph.find_one('Video', 'videoId', self.id)
        return video

    def liked_by(self):
        query = '''
        MATCH (user:User)-[:Likes]-(video:Video)
        WHERE video.videoId = {video_id}
        RETURN DISTINCT user.username
        '''
        return graph.run(query, video_id=self.id)

    def liked_by_count(self):
        query = '''
        MATCH (user:User)-[:Likes]-(video:Video)
        WHERE video.videoId = {video_id}
        RETURN COUNT(DISTINCT user.username) as count
        '''
        return graph.data(query, video_id=self.id)[0]['count']

    def disliked_by(self):
        query = '''
        MATCH (user:User)-[:Dislikes]-(video:Video)
        WHERE video.videoId = {video_id}
        RETURN DISTINCT user.username
        '''
        return graph.run(query, video_id=self.id)

    def disliked_by_count(self):
        query = '''
        MATCH (user:User)-[:Dislikes]-(video:Video)
        WHERE video.videoId = {video_id}
        RETURN COUNT(DISTINCT user.username) as count
        '''
        return graph.data(query, video_id=self.id)[0]['count']

    def like(self, user):
        self.clear_user_rel(user)
        graph.create(Relationship(user, "Likes", self.find()))

    def dislike(self, user):
        self.clear_user_rel(user)
        graph.create(Relationship(user, "Dislikes", self.find()))

    def clear_user_rel(self, user):
        query = """
        MATCH (n:User)-[r]-(v:Video)
        WHERE n.username={user} and v.videoId={vid}
        DELETE r
        """
        graph.run(query, user=user['username'], vid=self.find()['videoId'])        
