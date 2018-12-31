from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

def sentiment_measure(sentence):
	score = analyser.polarity_scores(sentence)
	return score