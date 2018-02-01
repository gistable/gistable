import staccato
import time

# must be replaced
consumer_key = "YOURS"
consumer_secret = "YOURS"
access_token_key = "YOURS"
access_token_secret = "YOURS"
TARGET = "username"
SLEEP_TIME = 5

def main():
  api = staccato.startup()
  api.auth(consumer_key, consumer_secret, access_token_key, access_token_secret)
  target_followings = api.friends_ids(screen_name=TARGET, count=5000)
  for user_id in target_followings["ids"]:
    api.friendships_create(user_id=user_id)
    time.sleep(SLEEP_TIME)
  
if __name__ == "__main__":
  main()