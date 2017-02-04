# EECS 337: Golden Globes

# 1. Find the names of the hosts
# 2. For each award, find the name of the winner (check if winner was nominated as well)
# 3. For each award, find the name of the presenter(s)
# 4. Add something special to it
 
import re
from corpus import *
from util import *
import pickle, os
import csv
from collections import defaultdict
from nltk.corpus import wordnet as wn
from nltk.tag import pos_tag
import wikipedia as wiki

##Globals Housing tweets and award data###
tweets = None
raw_awards = None
best_awards = None
award_bins = None

def naiveSearch(tweets, triggers):
  	"""
		Inputs: List of List of tweets , list of keywords
  	"""
	matchingTweets = []

	for tweet in tweets:
		for key in triggers:
			if findWholeWord(key)(tweet.text):
				matchingTweets.append(tweet)

	return matchingTweets

def findWholeWord(w):
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def identifyAwardWinners(award_bins, win_triggers):
	award_winners = {}
	for award in award_bins:
		award_winners[award] = naiveSearch(award_bins[award], win_triggers)
	return award_winners
		
def main():
	global tweets 
	global raw_awards 
	global best_awards
	global award_bins

	lFileList = []
	for fFileObj in os.walk(os.getcwd()): #Checks to see what files are in the current working directory
	    lFileList = fFileObj[2]
	    break

	if ('award_bins.dat' and 'best_awards.dat' and 'raw_awards.dat' and 'tweets.dat') in lFileList:
		award_bins = load('award_bins.dat')
		best_awards = load('best_awards.dat')
		raw_awards = load('raw_awards.dat')
		tweets = load('tweets.dat')
		print("Did as intended")
	else:
		tweets = read_tweets()
		tokenize_tweets(tweets)
		assign_phrases(tweets)
		raw_awards = get_raw_awards(tweets)
		best_awards = get_best_awards(raw_awards)
		award_bins = assign_awards(tweets, best_awards)
		save(award_bins,'award_bins.dat')
		save(best_awards, 'best_awards.dat')
		save(raw_awards, 'raw_awards.dat')
		save(tweets, 'tweets.dat')

	with open('phrases.csv') as phrases_csv:
		win_triggers = [phrase for phrase in csv.reader(phrases_csv)]

	winner_related_tweets = identifyAwardWinners(award_bins, win_triggers) #Returns a award_bins that contain only tweets filtered to be related to the winners of that award
	blacklist = ["Golden", "Globes", "SeriesTV", "TVSeries", "Series", "TV", "Congrats", "Congratulations", "Movie", "Limited"]
	entity_frequencies = {}

	total_tweets = sum(len(winner_related_tweets[award]) for award in winner_related_tweets)
	total_counter = 1
	award_counter = 1
	wiki_cache = {}
	for award in winner_related_tweets:

		tweet_counter = 1
		print "Award: %s - %s / %s" % (award, award_counter, len(winner_related_tweets))
		award_counter += 1

		entity_frequencies[award] = defaultdict(int)

		for tweet in winner_related_tweets[award]:

			if tweet_counter % 100 == 0:
				print "Tweet Number: %s / %s [%s / %s]" % (tweet_counter, len(winner_related_tweets[award]), total_counter, total_tweets)
			tweet_counter += 1
			total_counter += 1

			words = strip_tweet(tweet)
			proper_nouns = find_entities(words)
			filtered_nouns = [noun for noun in proper_nouns if noun not in award and noun not in blacklist]

			if (len(filtered_nouns)):
				query = " ".join(filtered_nouns)
				if query in wiki_cache:
					if wiki_cache[query]:
						entity_frequencies[award][wiki_cache[query]] += 1
				else:
					try:
						winner = wiki.page(query)
						entity_frequencies[award][winner.title] += 1
						wiki_cache[query] = winner.title
						print "Successfully found a wikipedia page pertaining to this query", winner.title.encode('utf-8')
					except (wiki.exceptions.DisambiguationError, wiki.exceptions.PageError, wiki.exceptions.WikipediaException) as e:
						if isinstance(e, wiki.exceptions.WikipediaException) and \
							not isinstance(e, wiki.exceptions.DisambiguationError) and \
							not isinstance(e, wiki.exceptions.PageError):
							print "Unknown error occurred for ", query.encode('utf-8'), e
						print "Could not find a wikipedia page for this query", query
						wiki_cache[query] = None
		
	print entity_frequencies
	return entity_frequencies

def find_entities(words):
	""" Given a list of words, returns a list of proper nouns contained within the list """
	tagged_words = pos_tag(words)
	return [word for word, pos in tagged_words if pos == 'NNP']

def strip_tweet(tweet):
	return [tok for tok in tweet.tokens if tok.upper() != 'RT' and tok[0] != '#' and tok[0] != '@']
  #return ' '.join(re.sub("(RT)|(@[A-Za-z0-9]+)|(#[A-Za-z0-9]+)|([^0-9A-Za-z \t])", "", tweet).split(' ')).strip()

##Code for Pickling##
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

if __name__ == '__main__':
	main()


