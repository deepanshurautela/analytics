import tweepy
from sentiment import sentiment_measure 
import json
from datetime import datetime

def twitter_sentiment(consumer_key, consumer_secret, access_token, access_token_secret,search_handle, search_size):
	results = []
	try:
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)

		api = tweepy.API(auth)

		public_tweets = api.user_timeline(id=search_handle, count=search_size)
		for tweet in public_tweets:    
	   		analysis = sentiment_measure(tweet.text)
	   		time = tweet.created_at
	   		time = time.strftime("%d")
	   		results.append({"text" : tweet.text.rstrip('\n') ,"created_at" : time, "source_url" : tweet.source_url, "analysis": analysis})
	except tweepy.TweepError:
		print('Error! Failed to get access token.')
		return None
	return json.dumps(results)

