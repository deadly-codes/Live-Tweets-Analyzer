from flask import Flask,render_template, redirect, request
import numpy as np
import tweepy 
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import re

app = Flask(__name__)

@app.route('/sentiment', methods = ['GET','POST'])
def sentiment():
    userid = request.form.get('fname')

    #======================Insert Twitter API Here==========================
    consumerKey = "ENTER YOUR CONSUMER KEY"
    consumerSecret = "ENTER YOUR CONSUMER SECRET KEY"
    accessToken = "ENTER YOUR ACCESS TOKEN KEY"
    accessTokenSecret = "ENTER YOUR ACCESS TOKEN SECRET KEY"
    #======================Insert Twitter API End===========================
    
    authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)
    authenticate.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(authenticate, wait_on_rate_limit = True)

    def cleanTxt(text):
        text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
        return text
    def getSubjectivity(text):
        return TextBlob(text).sentiment.subjectivity
    def getPolarity(text):
        return TextBlob(text).sentiment.polarity
    def getAnalysis(score):
            if score < 0:
                return 'Negative'
            elif score == 0:
                return 'Neutral'
            else:
                return 'Positive'

    if not(userid == ""):
        username = "@"+userid

        post = api.user_timeline(screen_name=userid, count = 200, lang ="en", tweet_mode="extended")
        twitter = pd.DataFrame([tweet.full_text for tweet in post], columns=['Tweets'])

        twitter['Tweets'] = twitter['Tweets'].apply(cleanTxt)
        twitter['Subjectivity'] = twitter['Tweets'].apply(getSubjectivity)
        twitter['Polarity'] = twitter['Tweets'].apply(getPolarity)

        twitter['Analysis'] = twitter['Polarity'].apply(getAnalysis)
        positive = twitter.loc[twitter['Analysis'].str.contains('Positive')]
        negative = twitter.loc[twitter['Analysis'].str.contains('Negative')]
        neutral = twitter.loc[twitter['Analysis'].str.contains('Neutral')]

        positive_per = round((positive.shape[0]/twitter.shape[0])*100, 1)
        negative_per = round((negative.shape[0]/twitter.shape[0])*100, 1)
        neutral_per = round((neutral.shape[0]/twitter.shape[0])*100, 1)
        #print(positive_per,negative_per)

        return render_template('pie.html', name=username,positive=[positive_per,positive.shape[0]],
        negative=[negative_per,negative.shape[0]],neutral=[neutral_per,neutral.shape[0]])
        

@app.route('/')
def home():
    return render_template('home.html')
    
@app.route('/front')
def front():
    return render_template('front.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__=='__main__':
    app.run(debug = True) #run on chrome
