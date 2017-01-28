# util.py
# Various utilities for our system.

import corpus, re
from lib import twokenize

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
				supers.append(special)
	return supers

def tokenize(text):
	return twokenize.tokenizeRawTweetText(text)

def tokenize_tweets(tweets):
	# Takes 30-60 seconds on my computer.
	return [tokenize(tweet) for tweet in tweets]