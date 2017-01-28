# util.py
# Various utilities for our system.

import corpus, re
from collections import defaultdict, Counter
from lib import twokenize
#from lib.ark_tweet import CMUTweetTagger

STOPWORDS = corpus.read_stopwords()

HASHPAT = re.compile('#.+')
USERPAT = re.compile('@.+')

def is_special(tok):
	"Return True if tok is a capitalized word, hashtag, user, or stopword."
	return (tok[0].isupper() and tok[1:].islower()) or tok.lower() in STOPWORDS

"""def is_special(tok):
	"Return True if tok is a capitalized word, hashtag, user, or stopword."
	return (tok[0].isupper() and tok[1:].islower() and tok.lower() not in STOPWORDS) or \
			bool(HASHPAT.match(tok)) or bool(USERPAT.match(tok)) #or \
			#tok.lower() in STOPWORDS"""

def find_special(toks):
	"Return a list of lists of words selected by is_special()."
	specials = []
	make_new = True
	for tok in toks:
		if is_special(tok):
			if make_new:
				specials.append([])
				make_new = False
			specials[-1].append(tok)
		else:
			make_new = True
	return specials

SUPERLATIVES = ['most', 'least', 'best', 'worst', 'favorite']
def find_superlatives(tweet_toks):
	supers = []
	for tweet in tweet_toks:
		specials = find_special(tweet)
		for special in specials:
			if special[0].lower() in SUPERLATIVES:
				supers.append(tuple(special))
	return supers

def tokenize(text):
	return twokenize.tokenizeRawTweetText(text)

def tokenize_tweets(tweets):
	# Takes 30-60 seconds on my computer.
	return [tokenize(tweet) for tweet in tweets]

class Trie(object):
	def __init__(self, items=None, values=None):
		self.children = defaultdict(Trie)
		self.value = None
		if items and values:
			for item, value in zip(items, values):
				self.insert(item, value)
		elif items:
			for item in items:
				self.insert(item)

	def __getitem__(self, item):
		if len(item) == 0:
			return self
		elif item[0] in self.children:
			return self.children[item[0]][item[1:]]
		else:
			return None

	def __setitem__(self, item, value):
		self.insert(item, value)

	def __contains__(self, item):
		return bool(self[item])

	def __delitem__(self, item):
		if len(item) == 0:
			self.children[item[0]].value = None
		else:
			del self.children[item[0]][item[1:]]
			if len(self.children[item[0]].children) == 0:
				del self.children[item[0]]

	def __str__(self):
		return 'Trie(%s, %s children)' % (self.value, len(self.children))

	def insert(self, item, value=None):
		value = value if value is not None else item
		if len(item) == 0:
			self.value = value
		else:
			self.children[item[0]].insert(item[1:], value)

	def walk(self, fn, direction='down', prefix=None):
		"""
		Walk the trie and call fn on it and each of its subtries.

		fn should take three arguments:
		    trie  - the trie itself
		    key   - the key of the trie relative to its root
		    value - the trie's value

		direction can be 'down' (default) or 'up'.  'down'
		ensures that fn is called on a trie before any of that
		trie's children.  'up' ensures that fn is called on all
		of a trie's children before being called on the trie itself.
		"""
		if direction != 'down' and direction != 'up':
			raise ValueError('direction must be "up" or "down"!')
		prefix = prefix if prefix is not None else tuple()
		if direction == 'down':
			fn(self, prefix, self.value)
		for key in self.children:
			child = self.children[key]
			child.walk(fn, direction, prefix + (key,))
		if direction == 'up':
			fn(self, prefix, self.value)

def trim_trailing_stopwords(toks):
	index = 0
	for i in reversed(range(len(toks))):
		if toks[i] not in STOPWORDS:
			index = i + 1
			break
	return toks[:index]

def get_raw_awards(tweet_toks):
	supers = find_superlatives(tweet_toks)
	# Rule: Drop any stopwords from the end of an award.
	supers = [trim_trailing_stopwords(s) for s in supers]
	# Rule: Ignore one- or no-word awards.
	supers = [s for s in supers if len(s) > 1]
	return supers

def get_best_awards(tweet_toks, cutoff=10):
	awards = get_raw_awards(tweet_toks)
	c = Counter(awards)
	awards = []
	for award, n in c.most_common():
		if n < cutoff:
			break
		awards.append(award)
	return awards

def make_awards_trie(awards, default=dict):
	return Trie(awards, [default() for award in awards])


