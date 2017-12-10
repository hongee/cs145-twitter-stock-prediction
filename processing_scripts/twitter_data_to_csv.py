import json
import csv
import sys
import multiprocessing as mp
from datetime import datetime, timedelta
import time
import pandas as pd

def read_stock_data(path):
    stock_data = pd.read_csv(path, index_col=0, parse_dates=True)
    return stock_data

def file_writer_process(q, path):
    file_path = path + ".csv"
    fieldnames = ["created_at", "text", "stock_val", "stock_val_1hr_delta", "stock_val_2hr_delta", "stock_val_6hr_delta", "after_hours"]
    print "Output to %s" % file_path
    with open(file_path, 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        count = 0
        while 1:
            try:
                d = q.get()
            except (KeyboardInterrupt, SystemExit):
                print("Printer Exiting...")
                break

            count += 1
            if count % 10000 == 0:
                print "Processed %d so far..." % count
            if d == "done":
                break
            try:
                writer.writerow(d)
            except Exception as e:
                print e
                continue
            q.task_done()
    return
    
def parse_and_query_stock(lineq, writequeue, stock_data):
    processed = 0
    while True:
        try:
            line = lineq.get()
        except (KeyboardInterrupt, SystemExit):
            print("Worker Exiting...")
            break
        afterhours = False
        if line == "done":
            lineq.task_done()
            break

        data = json.loads(line)
        if data.get('lang') != "en":
            lineq.task_done()
            continue
        timestamp = int(data.get("timestamp_ms"))//1000
        try:
            posted_time = datetime.fromtimestamp(timestamp)
        except Exception as e:
            print e
            lineq.task_done()
            continue

        try:
            # occurs before hour trading
            if posted_time.hour <= 4:
                posted_time = datetime(posted_time.year, posted_time.month, posted_time.day, 6, 0)
                afterhours = True
            
            if posted_time.hour >= 13:
                posted_time = datetime(posted_time.year, posted_time.month, posted_time.day + 1, 6, 0)
                afterhours = True
    
            current_stock = stock_data.iloc[stock_data.index.get_loc(posted_time,method='nearest')]
            if current_stock.name.day != posted_time.day:
                # Not a trading day
                lineq.task_done()
                continue
            in_1_hour = posted_time + timedelta(0, 60*5)
            in_2_hours = posted_time + timedelta(0, 2*60*5)
            in_6_hours = posted_time + timedelta(0, 6*60*5)

            curr = current_stock['Close']
            in_1_hour_d = curr - stock_data.iloc[stock_data.index.get_loc(in_1_hour,method='nearest')]['Close'] 
            in_2_hour_d = curr - stock_data.iloc[stock_data.index.get_loc(in_2_hours,method='nearest')]['Close']
            in_6_hour_d = curr - stock_data.iloc[stock_data.index.get_loc(in_6_hours,method='nearest')]['Close']
            writequeue.put({
                "created_at": posted_time,
                "text": data["text"].replace("\n", "\\n").encode('utf-8'),
                "stock_val": curr,
                "stock_val_1hr_delta": in_1_hour_d,
                "stock_val_2hr_delta": in_2_hour_d,
                "stock_val_6hr_delta": in_6_hour_d,
                "after_hours": afterhours
            })
            lineq.task_done()
            processed += 1

        except Exception as e:
            print e
            lineq.task_done()
            continue
    return processed



def process_data(path, stock_data):
    manager = mp.Manager()
    queue = manager.Queue()
    line_queue = manager.Queue()
    pool = mp.Pool(mp.cpu_count() + 1)

    file_writer = pool.apply_async(file_writer_process, (queue, path))
    
    print "Using %s workers" % mp.cpu_count()
    jobs = []
    for i in xrange(mp.cpu_count()):
        j = pool.apply_async(parse_and_query_stock, (line_queue, queue, stock_data))
        jobs.append(j)

    with open(path, 'r') as twitter_data:
        for i, line in enumerate(twitter_data):
            line_queue.put(line)

    for j in jobs:
        line_queue.put("done")

    for i,j in enumerate(jobs):
        res = j.get()
        print "Job %d processed %d entries." % (i, res)

    queue.put("done")
    pool.close()



def main():
    print "Reading stock data from ", sys.argv[1]
    sd = read_stock_data(sys.argv[1])
    print "Reading tweet data from ", sys.argv[2]
    num_lines = sum(1 for line in open(sys.argv[2]))
    print "Total data count: ", num_lines
    process_data(sys.argv[2], sd)
        

if __name__ == '__main__':
    main()

