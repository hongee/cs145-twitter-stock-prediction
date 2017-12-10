import json
import os
import math
import matplotlib.pylab as plt
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import multiprocessing as mp
import csv
import re
import pandas as pd
import requests
import datetime
import time

#####################################################################################
#Zhang's code for getting stock info                                                #
#####################################################################################

def get_google_finance_intraday(ticker, period=60, days=1):
    uri = 'http://finance.google.com/finance/getprices' \
          '?i={period}&p={days}d&f=d,o,h,l,c,v&df=cpct&q={ticker}'.format(ticker=ticker, period=period, days=days)
    page = requests.get(uri)
    reader = csv.reader(page.content.splitlines())
    columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    rows = []
    times = []
    for row in reader:
        if re.match('^[a\d]', row[0]):
            if row[0].startswith('a'):
                start = datetime.datetime.fromtimestamp(int(row[0][1:]))
                times.append(start)
            else:
                times.append(start+datetime.timedelta(seconds=period*int(row[0])))
            rows.append(map(float, row[1:]))
    if len(rows):
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'),
                            columns=columns)
    else:
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'))

#####################################################################################
#                                                                                   #
#####################################################################################

def filter(filenameout):

    datax = dict()
    length = dict()
    datalist = list()
    scorelist = list()
    base = 0;

    # nltk.download() #<--You may need to run this first to get it to work.
    sid = SentimentIntensityAnalyzer()

    # pathname = os.getcwd()  #Looks at current directory. Change this to whatever directory your code is.
    pathname = "../nvda/"
    files = os.listdir(pathname)
    files.sort(key=lambda x: os.path.getmtime(pathname + x))   #Sorts by time created.

    for filename in files:
        if filename.endswith(".txt"):
            print filename
            with open(pathname + filename, 'r') as input:
                for tweet in input:
                     try:
                        old_data = []
                        old_data.append(json.loads(tweet))
                        ss = sid.polarity_scores(str(old_data[0]['text']))      #Gives the sentiment score.
                        timestamp1 = old_data[0]['created_at']
                        timestamp1 = timestamp1[0:19] + timestamp1[25:30]
                        t1 = datetime.datetime.strptime(timestamp1, "%a %b %d %H:%M:%S %Y")
                        t1 = t1.replace(hour = t1.hour - 8,minute=0, second=0, microsecond=0)
                        index = str(t1.strftime("%m") + t1.strftime("%d") + t1.strftime("%H"))
                        # scores_formatted = "{\"neg\": " + str(ss['neg']) + ", \"neu\": " + str(
                        #     ss['neu']) + ", \"pos\": " + str(ss['pos']) \
                        #                    + ", \"compound\": " + str(ss['compound']) + "}"
                        # new_data = "{\"created_at\":\"" + str(
                        #     old_data[0]['created_at']) + "\",\"scores\":" + scores_formatted + \
                        #            ",\"retweets\":" + str(old_data[0]['retweet_count']) + "}"
                        if base == 0:
                            base = t1
                        if ss['compound'] != 0:
                            if index in datax:
                                datax[index][0] = datax[index][0] + ss['compound']
                                length[index] += 1
                            else:
                                templist = list()
                                templist.append(ss['compound'])
                                templist.append(t1)
                                datax[index] = templist
                                length[index] = 1
                     except:    #Code doesn't like newlines so this just passes over them if it sees one.
                        pass
    for key in datax:
        datax[key][0] /= length[key]
        datax[key][0] = 1/(1 + math.exp(datax[key][0]))     #This part is doing log reg and spitting out a probability
        datalist.append((key,datax[key]))

    # x,y = zip(*datalist)
    # w,z = zip(*y)
    # for entry in z:
    #     entry = (entry - base).total_seconds()/86400
    # plt.plot(z,w)
    # plt.show()

    df = get_google_finance_intraday("NVDA", 3600, 35)  # Zhang's code for getting the google finance thing.
    df.to_csv("./nvda_stock_data.csv")
    with open('nvda_stock_data.csv', 'rb') as input:
        reader = csv.reader(input)
        for row in reader:
            for key in datax:
                print "Key:" + str(datax[key][1])
                if str(row[0]) == str(datax[key][1]):
                    riseorfall = 1 if float(row[4]) - float(row[1]) > 0 else -1
                    scorelist.append((row[0], datax[key][0], riseorfall))

    print(scorelist)

    with open(filenameout, 'w') as output:
        for item in scorelist:
            output.write(' '.join(str(s) for s in item) + '\n')

if __name__ == '__main__':
    filename = "nvda-scorelist.txt"  #name of file you will be getting results in.
    filter(filename)