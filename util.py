# util.py
# Various utilities for our system.

import corpus, re
from collections import defaultdict, Counter
from lib import twokenize
from lib.ark_tweet import CMUTweetTagger

STOPWORDS = corpus.read_stopwords()

HASHPAT = re.compile('#.+')
USERPAT = re.compile('@.+')

def is_special(tok):
	"Return True if tok is a capitalized word, hashtag, user, or stopword."
	return (tok[0].isupper() and tok[1:].islower() and tok.lower() not in STOPWORDS) or \
			bool(HASHPAT.match(tok)) or bool(USERPAT.match(tok)) #or \
			#tok.lower() in STOPWORDS

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
def find_superlatives(tweets):
	supers = []
	for tweet in tweets:
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
		self.d = defaultdict(Trie)
		self.obj = None
		if items and values:
			for item, value in zip(items, values):
				self.insert(item, value)
		elif items:
			for item in items:
				self.insert(item)

	def __getitem__(self, item):
		if len(item) == 0:
			return self
		elif item[0] in self.d:
			return self.d[item[0]][item[1:]]
		else:
			return None

	def __setitem__(self, item, value):
		self.insert(item, value)

	def __contains__(self, item):
		return bool(self[item])

	def __delitem__(self, item):
		if len(item) == 0:
			self.d[item[0]].obj = None
		else:
			del self.d[item[0]][item[1:]]
			if len(self.d[item[0]].d) == 0:
				del self.d[item[0]]

	def insert(self, item, obj=None):
		obj = obj if obj is not None else item
		if len(item) == 0:
			self.obj = obj
		else:
			self.d[item[0]].insert(item[1:], obj)

def get_best_awards(tweet_toks, cutoff=10):
	supers = find_superlatives(tweet_toks)
	c = Counter(supers)
	awards = []
	for award, n in c.most_common():
		if n >= cutoff:
			awards.append(award)
		else:
			break
	return awards

def make_awards_trie(awards):
	return Trie(awards, [{} for award in awards])





