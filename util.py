# util.py
# Various utilities for our system.

# Built-in
import corpus, re
from collections import defaultdict, Counter

# Libraries
from lib import twokenize
#from lib.ark_tweet import CMUTweetTagger

# Custom code
from tweet import Tweet
from trie import Trie

## GLOBALS ##

# List of stopwords, read in automatically.
STOPWORDS = corpus.read_stopwords()

# Regex patterns for Twitter entities.
HASHPAT = re.compile('#.+')
USERPAT = re.compile('@.+')

# List of words that can start an award phrase.
SUPERLATIVES = ['most', 'least', 'best', 'worst', 'favorite']

## TOKENIZATION ##

def tokenize(text):
	return twokenize.tokenizeRawTweetText(text)

def tokenize_tweets(tweets):
	# Takes 30-60 seconds on my computer.
	for tweet in tweets:
		tweet.tokens = tokenize(tweet.text)

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

def assign_phrases(tweets):
	for tweet in tweets:
		tweet.phrases = find_phrases(tweet.tokens)

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
