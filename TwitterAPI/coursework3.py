import tweepy

consumer_key = "IPUUHSwAjXkV1vT64pjFHDtbd"
consumer_secret = "H7Ruj5ik5Pe445V7wmcqavrbPkEnbBiAXp5YzM6SudmHNt3Dan"
access_token = "1374325048153145344-jFOOCdgEOEz7goiRwzzwDaVulZkL2g"
access_token_secret = "wrbHJdiuHeLhPPtj8fHbJVjWJWkVisOoSkwI9TTihpxpv"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)


myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)

myStream.filter(track=['python'])