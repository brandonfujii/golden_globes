# ark.py
# Python wrapper for CMU's Ark tweet tagger.
# Adapted from CMUTweetTagger.py.

import shlex
from subprocess import Popen, PIPE

JAR_PATH = 'lib/ark-tweet-nlp-0.3.2-mod.jar' # Modified build that fixes the stdin bug.
JAR_ARGS = '--input-format text --output-format pretsv --no-confidence'
JAR_CMD = 'java -XX:ParallelGCThreads=2 -Xmx500m -jar %s %s' % (JAR_PATH, JAR_ARGS)

class TweetTagger(object):
	def __init__(self, cmd=JAR_CMD):
		self.cmd = cmd
		self.p = None

	def __enter__(self):
		return self.open()

	def __exit__(self, type, value, traceback):
		self.close()

	def open(self):
		if self.p:
			return self
		cmd = shlex.split(self.cmd)
		self.p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
		return self

	def close(self):
		self.p.terminate()

	def tag_tweet(self, tweet):
		text = tweet.text.replace('\n', ' ').replace('\t', ' ')
		if not text.strip(): # skip blank tweets
			return
		self.p.stdin.write(text.encode('utf-8') + '\n')
		line = self.p.stdout.readline()
		if line.count('\t') != 2:
			raise Error('Unexpected number of tabs in tweet output!')
		tokens, tags, text = line.split('\t')
		tweet.tokens = tokens.split()
		tweet.poses = tags.split()
