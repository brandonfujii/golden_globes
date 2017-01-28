import csv

# Delimiter for TSV/CSV file.
DELIM = '\t'
TWEETS_FILE = 'goldenglobes.tab'
STOPWORD_FILE = 'stopwords.txt'

def read_tweets(fname=TWEETS_FILE, fields=5, delim=DELIM):
	with open(fname) as fin:
		cr = csv.reader(fin, delimiter=DELIM)
		raw_lines = [l for l in cr]
		lines, buffer = [], []
		for line in raw_lines:
			if len(line) == fields:
				prefix = '\n'.join(buffer)
				tweet = prefix + '\n' + line[0] if prefix else line[0]
				lines.append([tweet] + line[1:])
				buffer = []
			else:
				buffer += line
		return lines

def read_stopwords(fname=STOPWORD_FILE):
	with open(fname) as fin:
		return [line.strip() for line in fin]
