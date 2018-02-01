# Twitter API Doc: https://developer.twitter.com/en/docs/tweets/search/overview/basic-search
import twitter #https://python-twitter.readthedocs.io/en/latest/getting_started.html
import random

api = twitter.Api(
    consumer_key='your_consumer_key',
    consumer_secret='your_consumer_secret',
    access_token_key='your_access_token_key',
    access_token_secret='your_access_token_secret',
)

hashtag = "cssdaybr17"
# GetSearch returns up to 100 tweets
results = api.GetSearch(
	raw_query="q=%23{hashtag}&src=typd&count=100".format(
		hashtag=hashtag
	)
)

users = [{'username': i.user.screen_name, 'name': i.user.name, 'id': i.id} for i in results]
sorted_users = sorted(users, key=lambda x: x['id'])

# Get more tweets forward
while len(results) > 1:
	next_user_id = sorted_users[0]['id']
	results = api.GetSearch(
		raw_query="q=%23{hashtag}&src=typd&count=100&max_id={next}".format(
			hashtag=hashtag,
			next=next_user_id
		)
	)
	new_users = [{'username': i.user.screen_name, 'name': i.user.name, 'id': i.id} for i in results]
	users = users + new_users
	sorted_users = sorted(users, key=lambda x: x['id'])

index = random.randint(0, len(users))
selected_user = users[index]
print(selected_user)