import twitter
import networkx as nx
import re

g = nx.DiGraph()

def get_tweets():
	twitter_search = twitter.Twitter(domain="search.twitter.com")
	search_results = []
	for page in range(1,6):
		search_results.append(twitter_search.search(q="SNL", rpp=100, page=page))
	return search_results

def get_all_tweets():
	search_results = get_tweets()
	return [ tweet
	  for page in search_results
		  for tweet in page["results"] ]

def get_rt_sources(tweet):
	rt_patterns = re.compile(r"(RT|via)((?:\b\W*@\w+)+)", re.IGNORECASE)
	return [ source.strip()
	  for tuple in rt_patterns.findall(tweet)
		  for source in tuple
			  if source not in ("RT", "via")]

all_tweets = get_all_tweets()
for tweet in all_tweets:
	rt_sources = get_rt_sources(tweet["text"])
	if not rt_sources: continue
	for rt_source in rt_sources:
		g.add_edge(rt_source, tweet["from_user"], {"tweet_id" : tweet["id"]})
