import json
import csv
import sys
import multiprocessing as mp
from datetime import datetime, timedelta
import time
import pandas as pd
import gensim
import itertools
import smart_open

def file_writer_process(q, path):
    file_path = path + "vectors.csv"
    print "Output to %s" % file_path
    with open(file_path, 'wb') as csvfile:
        writer = csv.writer(csvfile)
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
                print "WRITER ERR ", e
                print d
                continue
            q.task_done()
    return
    
def tweet2vec(lineq, writequeue, model):
    processed = 0
    while True:
        try:
            line = lineq.get()
        except (KeyboardInterrupt, SystemExit):
            print("Worker Exiting...")
            break

        if line == "done":
            lineq.task_done()
            break
        try:
            csv_reader = csv.reader([line.encode('utf-8')])
            for row in csv_reader:
                try:
                    if row[6] == "True":
                        break
                    text = row[1].decode('utf-8')
                    tokens = gensim.utils.simple_preprocess(text)
                    tokens = [ token.encode('utf-8') for token in tokens ]
                    vectors = list(model.infer_vector(tokens))

                except IndexError as e:
                    continue

                writequeue.put(list(itertools.chain([row[0],], vectors, row[2:])))
                lineq.task_done()
                processed += 1

        except Exception as e:
            print "WORKER ERR ",e
            lineq.task_done()
            continue
    return processed



def process_data(path, model):
    manager = mp.Manager()
    queue = manager.Queue()
    line_queue = manager.Queue()
    pool = mp.Pool(mp.cpu_count() + 1)

    file_writer = pool.apply_async(file_writer_process, (queue, path))
    
    print "Using %s workers" % mp.cpu_count()
    jobs = []
    for i in xrange(mp.cpu_count()):
        j = pool.apply_async(tweet2vec, (line_queue, queue, model))
        jobs.append(j)

    with smart_open.smart_open(path, encoding="utf-8") as twitter_data:
        twitter_data.readline()
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
    print "Loading Doc2Vec Gensim Model: ", sys.argv[1]
    model = gensim.models.doc2vec.Doc2Vec.load("doc2vec-model.gs")
    print "Reading tweet data from ", sys.argv[2]
    num_lines = sum(1 for line in open(sys.argv[2]))
    print "Total data count: ", num_lines
    process_data(sys.argv[2], model)
        

if __name__ == '__main__':
    main()

