import tweepy


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, tweet):
        print(tweet.text)


auth = tweepy.OAuthHandler("IPUUHSwAjXkV1vT64pjFHDtbd", "H7Ruj5ik5Pe445V7wmcqavrbPkEnbBiAXp5YzM6SudmHNt3Dan")
auth.set_access_token("1374325048153145344-jFOOCdgEOEz7goiRwzzwDaVulZkL2g", "wrbHJdiuHeLhPPtj8fHbJVjWJWkVisOoSkwI9TTihpxpv")

api = tweepy.API(auth)

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
myStream.filter(track=['test'])
