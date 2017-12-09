from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import json
from datetime import date, datetime
import time
import sys
# import dateutil.parser

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        # print obj.isoformat()
        # r = dateutil.parser.parse(obj.isoformat())
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

consumer_key="N4G6GT86uWNo7uQTfbRPvp5lZ"
consumer_secret="03Ed9nfUiAc5A7oLNZmzwpadZEUzUAOlPoZ3Z4sgfnwgJHhVBf"
access_token="146893662-w6kGYqUlgVVnOQopPMirpiTUjORIYAfVjGjdJr2M"
access_token_secret="XOOpHt1E20uW6nyQRlgb4LOxrrVrJB33CzYClUepSSds9"

class StdOutListener(StreamListener):
    def on_data(self, data):
        with open(filename, "a") as myfile:
            myfile.write(data)
            print(data)
        return True

    def on_error(self, status):
        print("ERROR")
        print(status)
        if status == 420:
            return False

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)

# if __name__ == '__main__':
#
#     # Maximum number of tweets we want to collect
#     maxTweets = int(sys.argv[1])
#
#     # The twitter Search API allows up to 100 tweets per query
#     tweetsPerQry = 100
#
#     # auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
#     auth = OAuthHandler(consumer_key, consumer_secret)
#     auth.set_access_token(access_token, access_token_secret)
#     api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
#     # print api.rate_limit_status()['resources']['search']
#
#     if sys.argv[2] == "nvda":
#         search = 'nvda OR nvidia OR gtx OR "jensen huang" OR "chris malachowsky" OR "curtis priem" OR tesla OR gpu OR bitcoin OR gaming'
#     elif sys.argv[2] == "amd":
#         search = 'amd OR ryzen OR threadripper OR radeon OR "jerry sanders" OR "lisa su" OR gpu OR bitcoin OR gaming'
#
#     i = {}
#     i["tweets"] = []
#     cur = {}
#     cur["tweets"] = []
#     counter = 0
#
#     try:
#         for tweet in tweepy.Cursor(api.search, q=search, lang="en", rpp=tweetsPerQry, result_type="recent").items(maxTweets):
#             res = {}
#             res["text"] = tweet.text
#             res["id"] = tweet.id
#             res["date"] = tweet.created_at
#             i["tweets"].append(res)
#             cur["tweets"].append(res)
#             counter += 1
#             # print counter, res
#             if counter >= 5000:
#                 filename = "code/data/tweets" + time.strftime("%Y%m%d-%H%M%S") + ".txt"
#                 with open(filename, "a") as myfile:
#                     toWrite = json.dumps(cur, default=json_serial)
#                     myfile.write(toWrite)
#                 counter = 0
#                 cur["tweets"] = []
#
#         if counter > 0:
#             filename = "code/data/tweets" + time.strftime("%Y%m%d-%H%M%S") + ".txt"
#             with open(filename, "a") as myfile:
#                 toWrite = json.dumps(cur, default=json_serial)
#                 myfile.write(toWrite)
#             counter = 0
#             cur["tweets"] = []
#
#         # with open("sample_tweets.json", "wb") as myfile:
#         #     myfile.write(json.dumps(i, default=json_serial))
#     except:
#         if counter > 0:
#             filename = "code/data/tweets" + time.strftime("%Y%m%d-%H%M%S") + ".txt"
#             with open(filename, "a") as myfile:
#                 toWrite = json.dumps(cur, default=json_serial)
#                 myfile.write(toWrite)
#             counter = 0
#             cur["tweets"] = []
#
#     # print api.rate_limit_status()['resources']['search']

if __name__ == '__main__':
    filename = "code/data/streamed" + time.strftime("%Y%m%d-%H%M%S") + ".txt"
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    myStream = tweepy.Stream(auth, l)

    if sys.argv[1] == "nvda":
        search = ['nvda', 'nvidia', 'gtx', "jensen huang", "chris malachowsky", "curtis priem", 'tesla', 'gpu', 'bitcoin', 'gaming']
    elif sys.argv[1] == "amd":
        search = ['amd', 'ryzen', 'threadripper', 'radeon', "jerry sanders", "lisa su", 'gpu', 'bitcoin', 'gaming']

    myStream.filter(track=search)
