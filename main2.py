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
from collections import defaultdict, Counter
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
	global tweets, raw_awards, best_awards, award_bins, ENTITIES

	ENTITIES = load_or_create('entities.dat', dict)
	tweets = load_or_create('tweets.dat', read_tweets)
	process_tweets(tweets)
	save(tweets, 'tweets.dat')
	raw_awards = load_or_create('raw_awards.dat', get_raw_awards, tweets)
	best_awards = load_or_create('best_awards.dat', get_best_awards, raw_awards)
	award_bins = load_or_create('award_bins.dat', assign_awards, tweets, best_awards)

	with open('phrases.csv') as phrases_csv:
		win_triggers = [phrase for phrase in csv.reader(phrases_csv)]

	winner_related_tweets = identifyAwardWinners(award_bins, win_triggers) #Returns a award_bins that contain only tweets filtered to be related to the winners of that award
	blacklist = ["Golden", "Globes", "SeriesTV", "TVSeries", "Series", "TV", "Congrats", "Congratulations", "Movie", "Limited"]
	entity_frequencies = {}
	for award in winner_related_tweets:
		entity_frequencies[award] = Counter()
		for tweet in winner_related_tweets[award]:
			entity_frequencies[award].update([canonicalize(entity) for entity in tweet.entities])
	print entity_frequencies
	save(ENTITIES, 'entities.dat')

	return entity_frequencies

if __name__ == '__main__':
	main()


