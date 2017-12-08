import json
import nltk
import pip
#from alpha_vantage.timeseries import TimeSeries
import os
import math
from datetime import datetime
import matplotlib.pylab as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def test(filename):
    #function = TIME_SERIES_INTRADAY & symbol = NVDA & interval = 60min & outputsize = full & apikey = 9WT5AOEK0XH0ZYNI
   # https: // www.alphavantage.co / query?function = TIME_SERIES_INTRADAY & symbol = MSFT & interval = 60min & apikey = demo
def filter(filenameout):
    #nltk.download() #<--You may need to run this first to get it to work.
    sid = SentimentIntensityAnalyzer()

    files = os.listdir(os.getcwd())     #Looks at current directory. Change this to whatever directory your code is.
    files.sort(key=lambda x: os.path.getmtime(x))   #Sorts by time created.

    with open(filenameout, 'a') as output:
        for filename in files:
            if filename.endswith(".txt") and filename != filenameout:
                print(filename)
                with open(filename, 'r') as input:
                    for line in input:
                         try:
                            old_data = []
                            old_data.append(json.loads(line))
                            sentence = str(old_data[0]['text'])
                            ss = sid.polarity_scores(sentence)      #Gives the sentiment score.
                            scores_formatted = "{\"neg\": " + str(ss['neg']) + ", \"neu\": " + str(
                                ss['neu']) + ", \"pos\": " + str(ss['pos']) \
                                               + ", \"compound\": " + str(ss['compound']) + "}"
                            new_data = "{\"created_at\":\"" + str(
                                old_data[0]['created_at']) + "\",\"scores\":" + scores_formatted + \
                                       ",\"retweets\":" + str(old_data[0]['retweet_count'])  + "}"
                            output.write(new_data)
                            output.write("\n")
                         except:    #Code doesn't like newlines so this just passes over them if it sees one.
                            pass

def classify(filename): #get the floor
    datax = dict()
    length = dict()
    datalist = list()
    base = 0;

    with open(filename, 'r') as data:
        for tweet in data:
            old_data = []
            old_data.append(json.loads(tweet))
            timestamp1 = old_data[0]['created_at']
            t1 = datetime.strptime(timestamp1, "%a %b %d %H:%M:%S %z %Y")
            t1 = t1.replace( minute=0,second=0,microsecond=0)
            index = int(t1.strftime("%m") + t1.strftime("%d") + t1.strftime("%H"))
            if base == 0:
                base = t1
            if old_data[0]['scores']['compound'] != 0:
                if index in datax:
                    datax[index][0] = datax[index][0] + old_data[0]['scores']['compound']
                    length[index] += 1
                else:
                    templist = list()
                    templist.append(old_data[0]['scores']['compound'])
                    templist.append(t1)
                    datax[index] = templist
                    length[index] = 1

    for key in datax:
        datax[key][0] /= length[key]
        datax[key][0] = 1/(1 + math.exp(datax[key][0]))
        datalist.append((key,datax[key]))

    #with open("logreglist.txt", 'w') as lrout:
    #    for item in datalist:
    #        print(item)
    #        lrout.write("{0}\n".format(item))

    x,y = zip(*datalist)
    w,z = zip(*y)
    for entry in z:
        entry = (entry - base).total_seconds()/3600
    plt.plot(z,w)
    plt.show()

if __name__ == '__main__':
    filename = "logreg.txt"
    #test("code20171119-132758.txt")
    #filter(filename)
    #classify(filename)