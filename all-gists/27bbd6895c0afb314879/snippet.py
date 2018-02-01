from urllib.request import urlretrieve
import praw


# ID for Reddit to monitor
user_agent = ("Wallpaper Downloader v1.0 by /u/80blite")
r = praw.Reddit(user_agent=user_agent)

# Subreddit objects
wall_top_ten = r.get_subreddit('wallpapers').get_hot(limit=10)
min_top_ten = r.get_subreddit('minimalwallpaper').get_hot(limit=10)

# List of top 10 submissions from r/wallpapers
wall_submissions = [submission for submission in wall_top_ten\
    if "imgur.com/" in submission.url]

# List of top 10 submissions from r/minimalwallpaper
min_submissions = [submission for submission in min_top_ten\
    if "imgur.com/" in submission.url]

# Download to wall_path folder with given name
for submission in wall_submissions:
    wall_path =\
        'c:/users/mike/desktop/Wallpapers/Popular/' + submission.title + '.jpg'
    urlretrieve(submission.url, wall_path)

# Download to min_path folder with given name
for submission in min_submissions:
    min_path =\
        'c:/users/mike/desktop/Wallpapers/Minimalist/' + submission.title + '.jpg'
    urlretrieve(submission.url, min_path)
