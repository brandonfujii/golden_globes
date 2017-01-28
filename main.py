# EECS 337: Golden Globes

# 1. Find the names of the hosts
# 2. For each award, find the name of the winner 
# 3. For each award, find the name of the presenter(s)
# 4. Add something special to it
 
import re
import tweet_reader as tr


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


tweets = tr.read_tweet_file("goldenglobes.tab")

print naiveSearch(tweets, ["award", "Award"])