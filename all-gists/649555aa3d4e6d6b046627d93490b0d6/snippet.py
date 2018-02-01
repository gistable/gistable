import string
import re
import nltk

def normalize(text):
	# remove punctuation
	text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
	# split into words
	# nltk.data.path.append("/nltk_data")
	from nltk.tokenize import word_tokenize
	tokens = word_tokenize(text)
	# convert to lower case
	tokens = [w.lower() for w in tokens]
	# remove remaining tokens that are not alphabetic
	words = [word for word in tokens if word.isalnum()]
	# filter out stop words
	from nltk.corpus import stopwords
	stop_words = set(stopwords.words('english'))
	words = [w for w in words if not w in stop_words]
	return ' '.join(words)


def find_tags(lambda_input):
	job_ad_text = normalize(lambda_input)
	from subprocess import Popen, PIPE, STDOUT
	p = Popen(['./fasttext', 'predict-prob', 'model_alnum_gom.bin', '-', '4'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
	stdout_data = p.communicate(input=job_ad_text)[0]
	return stdout_data.strip()

def handler(event, context):
	return find_tags(event['job_ad_text'])
