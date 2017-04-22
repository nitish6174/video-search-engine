from py2neo import Graph, Node, Relationship
from datetime import datetime
import os
import uuid

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

graph = Graph(url + '/db/data/', username=username, password=password)


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
        return graph.exists(Relationship(self.find(), 'Subscriber', Channel(channel_name).find()))

    def unsubscribe(self, channel_name):
        if self.is_subscribed(channel_name):
            return graph.separate(Relationship(self.find(), 'Subscriber', Channel(channel_name).find()))

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

    def clear_rel_with_video(self, video_id):
        user = self.find()
        Video(video_id).dislike(user)

    def liked_videos(self):
        query = '''
        MATCH (user:User)-[:Likes]-(video:Video)
        WHERE user.username = {user}
        RETURN DISTINCT video.videoId
        '''
        return graph.run(query, user=self.username)

    def disliked_videos(self):
        query = '''
        MATCH (user:User)-[:Dislikes]-(video:Video)
        WHERE user.username = {user}
        RETURN DISTINCT video.videoId
        '''
        return graph.run(query, user=self.username)


class Channel:

    def __init__(self, channel_name):
        self.name = channel_name

    def find(self):
        channel = graph.find_one('Channel', 'channelTitle', self.name)
        return channel

    def subscribers(self):
        query = '''
        MATCH (user:User)-[:Subscriber]-(channel:Channel)
        WHERE channel.channelTitle = {channel}
        RETURN DISTINCT user.username
        '''
        return graph.run(query, channel=self.name)

    def subscriber_count(self):
        query = '''
        MATCH (user:User)-[:Subscriber]-(channel:Channel)
        WHERE channel.channelTitle = {channel}
        RETURN COUNT(DISTINCT user)
        '''
        return graph.run(query, channel=self.name)

    def video_count(self):
        query = '''
        MATCH (video:Video)-[:HasChannel]-(channel:Channel)
        WHERE channel.channelTitle = {channel}
        RETURN COUNT(DISTINCT video)
        '''
        return graph.run(query, channel=self.name)

    def videos(self):
        query = '''
        MATCH (video:Video)-[:HasChannel]-(channel:Channel)
        WHERE channel.channelTitle = {channel}
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
        RETURN COUNT(DISTINCT user.username)
        '''
        return graph.run(query, video_id=self.id)

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
        RETURN COUNT(DISTINCT user.username)
        '''
        return graph.run(query, video_id=self.id)

    def like(self, user):
        self.clear_user_rel(user)
        graph.create(Relationship(user, "Likes", self.find()))

    def dislike(self, user):
        self.clear_user_rel(user)
        graph.create(Relationship(user, "Dislikes", self.find()))

    def clear_user_rel(self, user):
        graph.separate(user, self.find())
