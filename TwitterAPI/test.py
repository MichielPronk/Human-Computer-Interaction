import tweepy


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, tweet):
        print(tweet.text)


auth = tweepy.OAuthHandler("HH33gBISI6lxtWXXmaEEc9GwR", "I48FawYnm26bw0XNjjDdAxBzLrEiW6bXjcO3uUlGaeCqEz5wCr")
auth.set_access_token("1374325048153145344-mBQM6axfajmd3tSL5EZA5imPwv0CAf", "q2PkyIXF4SqGzRFhu3dGJvzA7bjo2Ry75Xx2hPgii2LOk")

api = tweepy.API(auth)

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
myStream.filter(track=['trump'])
