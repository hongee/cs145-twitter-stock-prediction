#!/bin/bash

echo "Running sentiment logistic regression..."
bash ./logistic_regression/run.sh

echo "Running SVM..."
bash ./svm/run.sh
