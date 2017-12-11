import csv
from sklearn.svm import SVC
import math
import pandas

def svm(filename):

    Kfolds = 4
    with open(filename,'r') as input:
        data = pandas.read_csv("raw_data.csvvectors.csv", header=None, error_bad_lines=False)
        filtered = data[data[55] == False]
        filtered = filtered[filtered[53] != 0]
        print filtered.shape[0]

        filtered.sample(frac=1)
        subsetsize = filtered.shape[0] / Kfolds

        data = filtered.iloc[:subsetsize,1:51]
        classlabel = filtered.iloc[:subsetsize, 53]
        classlabel = [1 if y0 > 0 else -1 for y0 in classlabel]
        clf = SVC(verbose = True, kernel= 'linear')
        clf.fit(data, classlabel)


        for k in range(0,Kfolds - 1):
            test_data = filtered.iloc[subsetsize*k:(k+1)*subsetsize,1:51]
            test_cl = filtered.iloc[subsetsize*k:(k+1)*subsetsize, 53]
            test_cl = [1 if y0 > 0 else -1 for y0 in test_cl]
            predictions = clf.predict(test_data)
            count = 0.0
            tp = 0.0
            for itemp, itemgt in zip(predictions, test_cl):
                count +=1
                if itemp == itemgt:
                    tp += 1

            print "Accuracy: ", tp/count

if __name__ == '__main__':
    filename = "raw_data.csvvectors.csv"
    svm(filename)