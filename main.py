import tweepy 
from flask import Flask, redirect, session, request, render_template
from twitter_sentiment import twitter_sentiment
import json
import os
import pandas
import random

consumer_key = "MO84RWScQLb31dfQczBPb9g3J"								
consumer_secret= "xy4GjgBAp9z3hJOz9Xw1i607eIGJgAEOy3CozSC6zCIaQq484M"								

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(10)


df = pandas.read_csv("celeb.csv")
rows = len(df.index)

@app.route('/')
def index():
	return redirect("/search/@"+ df['twitter'][random.randint(1,rows)] +"/10")

@app.route('/verifier/')
def verify():
	if request.args.get('denied') is None:
		session['verifier'] = request.args.get('oauth_verifier')
		verifier = session['verifier']

		try:
			auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
			if 'request_token' not in session:
				print("Token is not present")
				return redirect('/login') 
			token = session['request_token']
			auth.request_token = {'oauth_token' : token,'oauth_token_secret' : verifier }
			auth.get_access_token(verifier)
		
		except tweepy.TweepError:
			print('Error! Failed to get access token.')

		session['access_token'] = auth.access_token
		session['access_token_secret'] = auth.access_token_secret

		return redirect('/')
	else:
		return render_template('404.html', message="Didn't authenticate"), 404


@app.route('/search/<user>/')
@app.route('/search/<user>/<size>/')
def search(user, size=10):
	#Add the logged in condition here 
	if 	not 'access_token' in session:
		return redirect("/login")
	else:
		access_token = session['access_token']
		access_token_secret = session['access_token_secret']
		result = twitter_sentiment(consumer_key, consumer_secret, access_token,access_token_secret, user, size)
		if result is None:
			return render_template('404.html'), 404
		return render_template('page.html',result=json.loads(result), twitter_handle = user)


@app.route('/api/search/<user>/')
@app.route('/api/search/<user>/<size>/')
def api_search(user, size=None):
	if 	not 'access_token' in session:
		print('No access_token redirecting to login page')
		return redirect("/login")
	else:
		access_token = session['access_token']
		access_token_secret = session['access_token_secret']
		result = twitter_sentiment(consumer_key, consumer_secret, access_token,access_token_secret, user, size)
		if result is None:
			return render_template('404.html'), 404
		return result

@app.route('/login')
def login():
	try:
		auth_session = tweepy.OAuthHandler(consumer_key, consumer_secret)
		redirect_url = auth_session.get_authorization_url()
		session['request_token'] = auth_session.request_token
	except tweepy.TweepError as e:
		print('Error! Failed to get request token.' + str(e))
		return render_template('404.html', message = "Couldn't fetch redirect url"), 404
	return redirect(redirect_url)


@app.route('/logout')
def logout():
	if  'access_token' in session or  'access_token_secret' in session:
		session.pop('access_token')
		session.pop('access_token_secret')
	return redirect("/")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
	app.run(debug=True)
