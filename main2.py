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
from collections import defaultdict, Counter, OrderedDict
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
				print "key word: ", key, "tweet text: ", tweet.text
				matchingTweets.append(tweet)

	return matchingTweets

def findWholeWord(w):
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def identifyAwardWinners(award_bins, win_triggers):
	award_winners = {}
	for award in award_bins:
		award_winners[award] = naiveSearch(award_bins[award], win_triggers)
	return award_winners
def seperateWinnersNominees(award_bins, winner_award_bins):
	nominee_award_bin = {}
	for award in award_bins:
		if set(award_bins[award]) == set(winner_award_bins[award]):
			print "Trouble in paradise"
		nominee_award_bin[award] = list(set(award_bins[award]) - set(winner_award_bins[award]))
	return nominee_award_bin

def main():
	global tweets, raw_awards, best_awards, award_bins, entities

	winner_entities = load_or_create('winner_entities.dat', dict)
	nominee_entities = load_or_create('nominee_entities.dat', dict)

	tweets = load_or_create('tweets.dat', read_tweets)
	process_tweets(tweets)
	save(tweets, 'tweets.dat')

	raw_awards = load_or_create('raw_awards.dat', get_raw_awards, tweets)
	best_awards = load_or_create('best_awards.dat', get_best_awards, raw_awards)
	award_bins = load_or_create('award_bins.dat', assign_awards, tweets, best_awards)

	with open('phrases.csv') as phrases_csv:
		win_triggers = [phrase[0] for phrase in csv.reader(phrases_csv)]

	winner_related_tweets = identifyAwardWinners(award_bins, win_triggers) #Returns a award_bins that contain only tweets filtered to be related to the winners of that award
	blacklist = ["Golden", "Globes", "SeriesTV", "TVSeries", "Series", "TV", "Congrats", "Congratulations", "Movie", "Limited"]

	nominee_related_tweets = seperateWinnersNominees(award_bins, winner_related_tweets)


	####Count Frequencies in winner entities ####
	winner_entity_frequencies = {}
	for award in winner_related_tweets:
		winner_entity_frequencies[award] = Counter()
		for tweet in winner_related_tweets[award]:
			winner_entity_frequencies[award].update([canonicalize(entity, winner_entities) for entity in tweet.entities])
	#print winner_entity_frequencies
	save(winner_entities, 'winner_entities.dat')

	nominee_entity_frequencies = {}
	for award in nominee_related_tweets:
		nominee_entity_frequencies[award] = Counter()
		for tweet in nominee_related_tweets[award]:
			nominee_entity_frequencies[award].update([canonicalize(entity, nominee_entities) for entity in tweet.entities])
	#print nominee_entity_frequencies
	save(nominee_entities, 'nominee_entities.dat')

	winners = decideWinners(winner_entity_frequencies)
	for award in winners:
		print ' '.join(award),": " ,winners[award]
	print "\n\n\n\n\n\n\n"


	nominees = decideNominees(nominee_entity_frequencies)
	nominees = filterNominees(nominees)
	for award in nominees:
		print ' '.join(award),": " ,nominees[award]

	#return entity_frequencies
def decideNominees(nominee_entity_frequencies):
	orderedNomineeKeys = {}
	for award in nominee_entity_frequencies:
		orderedNomineeKeys[award] = [sorted(nominee_entity_frequencies[award], key=nominee_entity_frequencies[award].get, reverse=True), sum(nominee_entity_frequencies[award].values()) - nominee_entity_frequencies[award][None] + 1]

	nominees = {}

	for award in orderedNomineeKeys:
		nominees[award] = []
		for key in orderedNomineeKeys[award][0]:
			if (float(nominee_entity_frequencies[award][key])/float(orderedNomineeKeys[award][1])) > .1:
				nominees[award].append(key)  

	return nominees


def filterNominees(nominees):
	# triggers = {
	# 	"actor" : ["actor"],
	# 	"actress" : ["actress"],
	# 	"film" : ["film", "movie"],
	# 	"tv" : ["tv", "television", "show"],
	# 	"series" : ["miniseries", "series", 'mini-series']
	# }
	triggers = OrderedDict([('actor', ["actor"]) , ("actress" , ["actress"]) , ("film" , ["film", "movie"]) , ("tv" , ["tv", "television", "show"]) , ("series" , ["miniseries", "series", 'mini-series'])])
	
	new_nominees = {}
	for award in nominees:
		new_nominees[award] = []
		toBreak = False 
		for key in triggers:
			if toBreak:
				break
			for term in triggers[key]:
				if findWholeWord(term)(' '.join(award)):
					wikiQuery(nominees, new_nominees, award, key)
					toBreak = True
					break
	return new_nominees

def wikiQuery(nominees, new_nominees, award, appendWord):
	for entity in nominees[award]:
		try: 
			if entity:
				page = wiki.page(entity + " " + appendWord)
				new_nominees[award].append(page.title)
		except wiki.exceptions.WikipediaException as e: 
			if not isinstance(e, wiki.exceptions.DisambiguationError) and \
			not isinstance(e, wiki.exceptions.PageError):
				print "Unknown error occurred"

def decideWinners(entity_frequencies):
	winners = {}
	for award in entity_frequencies:
		maxKey = None
		maxVal = float("-inf")
		for candidate in entity_frequencies[award]:
			if candidate:
				if entity_frequencies[award][candidate] > maxVal:
					maxVal = entity_frequencies[award][candidate]
					maxKey = candidate
		winners[award] = maxKey
		#maximum = max(entity_frequencies[award].iteritems(), key=operator.itemgetter(1))[0]  
		#winners[award] = maximum
	return winners

if __name__ == '__main__':
	main()


