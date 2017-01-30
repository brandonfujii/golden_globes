# EECS 337: Golden Globes

# 1. Find the names of the hosts
# 2. For each award, find the name of the winner 
# 3. For each award, find the name of the presenter(s)
# 4. Add something special to it
 
import re
from corpus import *
from util import *
import pickle, os

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
			if findWholeWord(key)(tweet[0]):
				matchingTweets.append(tweet[0])

	return matchingTweets

def findWholeWord(w):
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


#tweets = read_tweets("goldenglobes.tab")


##for each in naiveSearch(tweets, corp.read_phrases()):
##	print each, '\n'


##Loads Award Bins from Save File##
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
		print "Did as intended"
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


