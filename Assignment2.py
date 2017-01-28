from nltk.probability import FreqDist
import nltk
import re #import regex


#Define the text file and setup
text_file = open("goldenglobes.tab", "rU")
lines = text_file.read().split("\n")


#search words in file;
#input type: list
def searchWords(words):
	for word in words:
		for line in lines:
			fields = nltk.TabTokenizer().tokenize(line)
			ot = sorted([f for f in fields if word in f])
			if ot:
				print('{0}： {1}'.format(word, ot))


#search unusual words
#input type: nth line in tweet
#exp: for i in range(0, 30):
#     	print(unusual_words(i))
def unusual_words(n):
	line = lines[n]
	fields = nltk.TabTokenizer().tokenize(line)
	tokens = nltk.word_tokenize(fields[0])
	text_vocab = set(w.lower() for w in tokens if w.isalpha())
	english_vovab = set(w.lower() for w in nltk.corpus.words.words())
	unusual =  text_vocab.difference(english_vovab)
	return sorted(unusual)	
	

#search names
#input type: from 0 to nth line in tweet
def searchNames(n):
	names = nltk.corpus.names
	male_names = names.words('male.txt')
	female_names = names.words('female.txt')
	for i in range(0, n):
		line = lines[i]
		fields = nltk.TabTokenizer().tokenize(line)
		tokens = nltk.word_tokenize(fields[0])
		ot = sorted([token for token in tokens if token in male_names])
		if ot:
			print('Tweet# {0}: Name:{1}'.format(i, ot))

'''
#search synonym (nltk.corpus.wordnet.synsets)
print( nltk.corpus.wordnet.synsets('win'))
print(nltk.corpus.wordnet.synset('win.n.01').definition())
for synset in nltk.corpus.wordnet.synsets('win'):
	print (synset.lemma_names)

'''

##using regex to search
#input type: from 0 to nth line in tweet, and regex
#exp: searchNpsChat(400, '^[0-9]{4}$')
def searchRegex(n, regex):
	for i in range(0, n):
		line = lines[i]
		fields = nltk.TabTokenizer().tokenize(line)
		tokens = nltk.word_tokenize(fields[0])
		ot = sorted([token for token in tokens if re.search(regex, token)])
		if ot:
			print('Tweet# {0}: Words:{1}'.format(i, ot))




#part-of-speech tagger
#input type: nth line in tweet
#exp: for i in range(0, 30):
def POS(n):
	line = lines[n]
	fields = nltk.TabTokenizer().tokenize(line)
	tokens = nltk.word_tokenize(fields[0])
	PosList = nltk.pos_tag(tokens)
	print('Line# {0}:  POS list:{1}'.format(n, PosList))




phases = ['congratulations to', 'congrats to', 'for winning', 'wins for', 'wins', 'who won', 'performance', 'goes to', 'on winning', 'dedicates']
def searchPhase(words, lineNum):
	for word in words:
		line = lines[lineNum]
		fields = nltk.TabTokenizer().tokenize(line)
		tokens = nltk.word_tokenize(fields[0])
		#add PosList
		PosList = nltk.pos_tag(tokens)
		for tagged_token in PosList:
			if tagged_token[1] == 'NNP':
				print (tagged_token[0])

def POS2(n):
	line = lines[n]
	fields = nltk.TabTokenizer().tokenize(line)
	tokens = nltk.word_tokenize(fields[0])
	PosList = nltk.pos_tag(tokens)
	for tagged_token in PosList:
		print (tagged_token[1])





searchPhase(phases, 1)





#for i in range(20):
#	print (unusual_words(i))

#print(nltk.corpus.wordnet.synsets('win'))
#print(nltk.corpus.wordnet.synset('win.v.01').lemma_names())
#searchPhase(phases)


