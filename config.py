import os

# Settings 

USER_AGENT = "Posts Saver Bot v0.1"
MIN_UPVOTES = 1000
MIN_COMMENTS = 2
START_RANGE = 1483228800
END_RANGE = 1514764799
SUBREDDIT_NAME = os.environ.get('SUBREDDIT_NAME', 'writingprompts')

# PRAW Constants
REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')
REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD')
REDDIT_APP_ID = os.environ.get('REDDIT_APP_ID')
REDDIT_APP_SECRET = os.environ.get('REDDIT_APP_SECRET')


FIREBASE_AUTH = {
    "apiKey": os.environ.get('FIREBASE_APIKEY'),
    "authDomain": "storiesapp-d6e91.firebaseapp.com",
    "databaseURL": "https://storiesapp-d6e91.firebaseio.com",
    "projectId": "storiesapp-d6e91",
    "storageBucket": "storiesapp-d6e91.appspot.com",
    "messagingSenderId": "55794856298"
}
