import csv
import sqlite3

#Tweetの全履歴をダウンロードで得られるtweet.csvを指定する
file_path = "Downloads/tweet/tweets.csv"

f = open(file_path,'r')

reader = csv.reader(f)
header = next(reader)

c = sqlite3.connect('tweets.sqlite3')

c.execute("create table tweets('tweet_id', 'in_reply_to_status_id', 'in_reply_to_user_id', 'timestamp', 'source', 'text', 'retweeted_status_id', 'retweeted_status_user_id', 'retweeted_status_timestamp', 'expanded_urls');")

query = u"insert into tweets values(?,?,?,?,?,?,?,?,?,?);"
a=0

for row in reader:
    a+=1
    t = tuple(row)
    c.execute(query, t)
    if a%1000 == 0:
        c.commit()
        print("commited - " + str(a))

c.close()