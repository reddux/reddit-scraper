import config
import requests
import csv
import praw


def load_log():
    """Loads the csv file and return a list of Reddit posts id's."""

    try:
        with open(config.LOG_FILE, "r", newline="") as csv_contents:
            return [item[0] for item in csv.reader(csv_contents)]
    except FileNotFoundError:
        with open(config.LOG_FILE, "w", newline="") as temp_contents:
            return []


def save_log(post_id):
    """Updates the csv file with the processed Reddit post id."""

    with open(config.LOG_FILE, "a", newline="") as csv_contents:
        csv_writer = csv.writer(csv_contents)
        csv_writer.writerow([post_id])


def firebase_login():
    """Logins the user to your Firebase database."""

    base_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(
        config.FIREBASE_APIKEY)

    credentials = dict()
    credentials["email"] = config.FIREBASE_EMAIL
    credentials["password"] = config.FIREBASE_PASSWORD
    credentials["returnSecureToken"] = True

    with requests.post(base_url, json=credentials) as login_response:

        # IF the login was successful we return the 'idToken', else we exit the program.
        if login_response.status_code == 200:
            print("Sucessfully logged to Firebase.")
            return login_response.json()["idToken"]
        else:
            print("Failed Login:", login_response.json()["error"]["message"])
            quit()


def get_subreddit_data():

    reddit = praw.Reddit(client_id=config.APP_ID, client_secret=config.APP_SECRET,
                         user_agent=config.USER_AGENT, username=config.REDDIT_USERNAME,
                         password=config.REDDIT_PASSWORD)

    subreddit = reddit.subreddit(config.SUBREDDIT_NAME)

    for submission in subreddit.submissions(config.START_RANGE, config.END_RANGE):

        post_id = submission.id

        if post_id not in SAVED_POSTS and submission.score >= config.MIN_UPVOTES:

            list_of_valid_comments = [comment for comment in submission.comments if (
                hasattr(comment, "body") and comment.distinguished == None)]

            if len(list_of_valid_comments) >= config.MIN_COMMENTS:

                top_comment = list_of_valid_comments[0]

                # Sometimes the top comment is deleted.
                try:
                    temp_dict = dict()
                    temp_dict["post_title"] = submission.title
                    temp_dict["post_author"] = submission.author.name
                    temp_dict["top_comment"] = top_comment.body
                    temp_dict["top_comment_author"] = top_comment.author.name
                    temp_dict["post_date"] = submission.created_utc
                    temp_dict["unique_id"] = submission.id
                    temp_dict["reddit_url"] = submission.url

                    save_to_firebase(temp_dict)

                except AttributeError:
                    pass

            else:
                print("Skipping post ID:", post_id, "not enough comments.")

        else:
            print("Skipping post ID:", post_id, "already saved.")


def save_to_firebase(subreddit_data):
    """
    Saves the repository data to the specified Firebase node.
    We use the repo name as its id for the Firebase database.
    """

    base_url = "https://{}.firebaseio.com/{}.json?auth={}".format(
        config.FIREBASE_PROJECTID, config.FIREBASE_NODE, AUTH_TOKEN)

    # We use the PATCH verb and send the data as a JSON string.
    with requests.post(base_url, json=subreddit_data) as response:

        # We now determine the status of the operation.
        if response.status_code == 200:
            print("Added {} with id: {}".format(
                subreddit_data["post_title"], subreddit_data["unique_id"]))
            save_log(subreddit_data["unique_id"])
        else:
            print(response.json()["error"])


if __name__ == "__main__":

    AUTH_TOKEN = firebase_login()
    SAVED_POSTS = load_log()
    get_subreddit_data()
