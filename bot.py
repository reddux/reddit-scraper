import config
import requests
import praw
import pyrebase
import argparse
from datetime import datetime

def past_week_utc():
    dt = datetime.today() 
    return dt.timestamp() - 608400

def firebase_login():
    return pyrebase.initialize_app(config.FIREBASE_AUTH)

def get_subreddit_data():

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--startTime', default=past_week_utc())
    parser.add_argument('-e', '--endTime', default=None)
    args = parser.parse_args()

    reddit = praw.Reddit(client_id=config.REDDIT_APP_ID, client_secret=config.REDDIT_APP_SECRET,
                         user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                         password=config.REDDIT_PASSWORD)

    subreddit = reddit.subreddit(config.SUBREDDIT_NAME)

    for submission in subreddit.submissions(args.startTime, args.endTime):

        post_id = submission.id

        if submission.score >= config.MIN_UPVOTES:

            list_of_valid_comments = [comment for comment in submission.comments if (
                hasattr(comment, "body") and comment.distinguished == None)]

            if len(list_of_valid_comments) >= config.MIN_COMMENTS:

                top_comment = list_of_valid_comments[0]

                # Sometimes the top comment is deleted.
                try:
                    data = {
                        "post_title": submission.title,
                        "post_author": submission.author.name,
                        "top_comment": top_comment.body,
                        "top_comment_author": top_comment.author.name,
                        "post_date": submission.created_utc,
                        "unique_id": submission.id,
                        "reddit_url": submission.url
                    }

                    save_to_firebase(data)

                except AttributeError:
                    pass

            else:
                print("Skipping post ID:", post_id, "not enough comments.")

        else:
            print("Skipping post ID:", post_id, "upvote requirment not met.")


def save_to_firebase(subreddit_data):
    """
    Saves the repository data to the specified Firebase.
    Use the SUBREDDIT_NAME as the name of the table.
    """

    db = FIREBASE.database()

    # Check if post already exists
    duplicate = db.child(config.SUBREDDIT_NAME).order_by_child(
        "unique_id").equal_to(subreddit_data["unique_id"]).get()

    if len(duplicate.each()) < 1:
        response = db.child(config.SUBREDDIT_NAME).push(subreddit_data)
        print("Added {} with id: {}".format(subreddit_data["post_title"], subreddit_data["unique_id"]))
    else:
        print("Skipping post ID:",
              subreddit_data["unique_id"], "already saved.")


if __name__ == "__main__":
    FIREBASE = firebase_login()
    get_subreddit_data()
