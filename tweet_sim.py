import tweepy
import random
import numpy as np
import os
import time
import schedule
import json
import dotenv
import markovify

dotenv.load_dotenv()

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
OAUTH_TOKEN = os.environ.get('OAUTH_TOKEN')
OAUTH_TOKEN_SECRET = os.environ.get('OAUTH_TOKEN_SECRET')

numSentences = random.randint(1, 4)
maxSentenceChars = 70

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, "oob")

try:
    url = auth.get_authorization_url()
except tweepy.TweepError:
    print("Failed to get request token")

print(url)

verifier = input('Enter PIN: ')

try:
    auth.get_access_token(verifier)
except tweepy.TweepError:
    print("Failed to get access token")



auth.set_access_token(auth.access_token, auth.access_token_secret)

api = tweepy.API(auth)

print("Successfully logged in!")

trends = api.trends_place(23424977)[0]['trends']

def simulate():

    trend = trends[random.randint(0, len(trends) - 1)]

    while trend['tweet_volume'] == None:
        trend = trends[random.randint(0, len(trends) - 1)]

    trendVol = 500

    query = trend['query']
    hashtag = ('#' + (query.replace("+", "_").replace("%22", "").replace("%26", "&").replace("%23", "")))

    print(hashtag)

    print("Scanning tweets...")
    search = [status for status in tweepy.Cursor(api.search, q=query, tweet_mode="extended", wait_on_rate_limit=True).items(trendVol)]
    dataFile = open("tweets.txt", "w", encoding="utf-8")

    for result in search:
        if hasattr(result, "retweeted_status"):
            dataFile.write((result.retweeted_status.full_text).replace("\n", "..."))
            dataFile.write("\n")
        else:
            dataFile.write((result.full_text).replace("\n", "..."))
            dataFile.write("\n")

    dataFile.close()

    text = open("tweets.txt", "r", encoding="utf-8").read()

    print("Generating tweet...")
    model = markovify.NewlineText(text, well_formed=False)

    chain = ""

    for i in range(numSentences):
        try:
            chain += (model.make_short_sentence(maxSentenceChars, tries=1000)).replace("...", "\n")
            if (chain[-1] != "." and chain[-1] != "!" and chain[-1] != "?"):
                chain += "."
            chain += " "
        except:
            print("NoneType sentence")
            break

    tweet = chain.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    api.update_status(status=(hashtag + tweet))
    print("Tweet sent!")

schedule.every().day.at("10:00").do(simulate)
schedule.every().day.at("14:00").do(simulate)
schedule.every().day.at("18:00").do(simulate)
