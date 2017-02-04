# util.py
# Various utilities for our system.

# Built-in
import corpus, re, sys, os, pickle
from collections import defaultdict, Counter

# Libraries
from lib import twokenize
import wikipedia as wiki
#from lib.ark_tweet import CMUTweetTagger

# Custom code
from tweet import Tweet
from trie import Trie
from ark import TweetTagger

## GLOBALS ##

# Whether to print debug statements.
DEBUG = True

# How often to print debug statements when looping over tweets.
DEBUG_FREQ = 100

# List of stopwords, read in automatically.
STOPWORDS = corpus.read_stopwords()

# Regex patterns for Twitter entities.
HASHPAT = re.compile('#.+')
USERPAT = re.compile('@.+')

# List of words that can start an award phrase.
SUPERLATIVES = ['most', 'least', 'best', 'worst', 'favorite']

# Entity mappings discovered so far.
ENTITIES = {}

## DEBUGGING ##

def debug(msg):
	if DEBUG:
		sys.stderr.write('%s\n' % msg)

## PICKLING ##

def save(dObj, sFilename):
  """Given an object and a file name, write the object to the file using pickle."""
  f = open(sFilename, "w")
  p = pickle.Pickler(f)
  p.dump(dObj)
  f.close()

def load(sFilename):
  """Given a file name, load and return the object stored in the file."""
  f = open(sFilename, "r")
  u = pickle.Unpickler(f)
  dObj = u.load()
  f.close()
  return dObj

def load_or_create(fname, fn, *args):
	if os.path.exists(fname):
		return load(fname)
	obj = fn(*args)
	save(obj, fname)
	return obj

## TWEET PROCESSING ##

def process_tweet(tweet, tagger):
	# tweet.tokens = tweet.tokens or tokenize(tweet.text) # Done better by tag_tweet()
	if not tweet.tags:
		tagger.tag_tweet(tweet)
	tweet.entities = tweet.entities or find_entities(tweet.tokens, tweet.tags)
	tweet.phrases = tweet.phrases or find_phrases(tweet.tokens)

def process_tweets(tweets):
	with TweetTagger() as tt:
		tweet_count = len(tweets)
		for i, tweet in enumerate(tweets):
			if i % DEBUG_FREQ == 0:
				debug('Processing tweet %s / %s' % (i, tweet_count))
			process_tweet(tweet, tt)

## TOKENIZATION AND TAGGING ##

def tokenize(text):
	return twokenize.tokenizeRawTweetText(text)

"""def tokenize_tweets(tweets, override=False):
	# Takes 30-60 seconds on my computer.
	for i, tweet in enumerate(tweets):
		if not tweet.tokens or override:
			tweet.tokens = tokenize(tweet.text)"""

"""def tag_tweets(tweets, override=False):
	# Takes the place of tokenization.
	with TweetTagger() as tt:
		for tweet in tweets:
			if not tweet.tags or override:
				tt.tag_tweet(tweet)"""

## ENTITY RECOGNITION ##

def canonicalize(entity):
	if entity not in ENTITIES:
		try:
			winner = wiki.page(entity)
			ENTITIES[entity] = winner.title
			debug('Successfully found a wikipedia page pertaining to this query %s' % winner.title.encode('utf-8'))
		except wiki.exceptions.WikipediaException as e:
			if not isinstance(e, wiki.exceptions.DisambiguationError) and \
				not isinstance(e, wiki.exceptions.PageError):
				debug('Unknown error occurred for: %s' % entity.encode('utf-8'))
			ENTITIES[entity] = None
			debug('Could not find a wikipedia page for this query %s' % entity)
	return ENTITIES[entity]

def find_entities(toks, tags):
	"Return a list of entities (consecutive proper nouns) found in the tweet."
	entities = []
	make_new = True
	for tok, tag in zip(toks, tags):
		if tag == '^':
			if make_new:
				entities.append([])
				make_new = False
			entities[-1].append(tok)
		else:
			make_new = True
	return [' '.join(entity) for entity in entities]

"""def assign_entities(tweets, override=False):
	for i, tweet in enumerate(tweets):
		if not tweet.entities or override:
			tweet.entities = find_entities(tweet)"""

## PHRASES ##

def is_phrasal(tok):
	"Return True if tok is a capitalized word or stopword."
	return (tok[0].isupper() and tok[1:].islower()) or tok.lower() in STOPWORDS

def is_phrasal_extended(tok):
	"Return True if tok is a capitalized word, hashtag, user, or stopword."
	return (tok[0].isupper() and tok[1:].islower() and tok.lower() not in STOPWORDS) or \
			bool(HASHPAT.match(tok)) or bool(USERPAT.match(tok)) #or \
			#tok.lower() in STOPWORDS

def find_phrases(toks):
	"Return a list of lists of words selected by is_phrasal()."
	phrasals = []
	make_new = True
	for tok in toks:
		if is_phrasal(tok):
			if make_new:
				phrasals.append([])
				make_new = False
			phrasals[-1].append(tok)
		else:
			make_new = True
	return [tuple(phrase) for phrase in phrasals]

def trim_trailing_stopwords(toks):
	index = 0
	for i in reversed(range(len(toks))):
		if toks[i] not in STOPWORDS:
			index = i + 1
			break
	return toks[:index]

"""def assign_phrases(tweets, override=False):
	for tweet in tweets:
		if not tweet.phrases or override:
			tweet.phrases = find_phrases(tweet.tokens)"""

## AWARDS ##

def is_superlative(phrase):
	return phrase[0].lower() in SUPERLATIVES

def phrase_to_award(phrase):
	if not is_superlative(phrase):
		return None
	phrase = trim_trailing_stopwords(phrase)
	return phrase if len(phrase) > 1 else None

def get_raw_awards(tweets):
	awards = []
	for tweet in tweets:
		for phrase in tweet.phrases:
			award = phrase_to_award(phrase)
			if award:
				awards.append(award)
	return awards

def get_best_awards(awards, cutoff=10):
	c = Counter(awards)
	best_awards = []
	for award, n in c.most_common():
		if n < cutoff:
			break
		best_awards.append(award)
	return best_awards

def assign_awards(tweets, awards):
	award_bins = dict((award, set()) for award in awards)
	for tweet in tweets:
		for phrase in tweet.phrases:
			award = phrase_to_award(phrase)
			if award in award_bins:
				tweet.awards.append(award)
				award_bins[award].add(tweet)
	return award_bins

def make_awards_trie(awards, default=set):
	return Trie(awards, [default() for award in awards])
