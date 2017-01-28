# tweet.py
# Class for storing tweets.

import re

RTPAT = re.compile('^RT @(\w+):')

class Tweet(object):
	def __init__(self, text=None, tweet_id=None, author=None, author_id=None, timestamp=None):
		self.text = text
		self.tweet_id = tweet_id
		self.author = author
		self.author_id = author_id
		self.timestamp = timestamp

		self.tokens = []
		self.poses = []
		self.phrases = []
		self.awards = []

	def is_retweet(self):
		return bool(RTPAT.match(self.text))

	def retweet_user(self):
		m = RTPAT.match(self.text)
		return m.group(1) if m else None
