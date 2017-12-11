Code for CS145 Project
===

### Requirements
- Python 2.7 / pip
- A virtualenv
- Graphviz
- Tested on Mac OS 10.13

### Dependencies
`pip install -r requirements.txt`
You may need to configure Jupyter for the algorithms on the notebooks to work properly.

Raw and pre-trained document vectors can be found at https://www.dropbox.com/home/CS145_DATA

### Running

For the Doc2Vec training, Doc2Vec Logistic Regression and Neural Network implementations,
we did the majority of our experimentation and programming on Jupyter notebooks, and with finals
and the limited timeframe it is difficult to provide a reasonable `run.sh` script. You can find
a nicely rendered version of the notebooks here, or you can run your own with `jupyter notebook`

- Doc2Vec Training - https://github.com/hongee/cs145-twitter-stock-prediction/blob/master/doc2vec/train_doc2vec.ipynb
- Logistic Reg/Neural Net - https://github.com/hongee/cs145-twitter-stock-prediction/blob/master/neural_net/NN.ipynb

To run the Log Reg/NN with the same data as us, download `data.csvvectors.csv.zip` from the above link, 
and unzip it in the Neural Net directory. You can do the same with the other files with Doc2Vec training, but it's
we think it's unlikely you'll want to sit around for an hour to train the document vectors.

A few other scripts that are part of the preprocessing pipeline:

- `processing_scripts/stock_data_to_csv.py`
This grabs the stock data of a particular ticker label from Google finance. It defaults to AMD, and needs to be changed within the code.

- `processing_scripts/twitter_data_to_csv.py`
This processes an input of streamed twitter data, where each line is the entire JSON payload for one tweet from Twitter. It takes
stock data (in CSV format) as the first input, and the path to the streamed data as the second. The files can again be found in the
dropbox folder above.
Example: `python twitter_data_to_csv.py amd_stock_data.csv amd-streamed-20171109-231920.txt`

- `processing_scripts/preprocess.py`
This script transforms the text column in the CSV to its corresponding document vector, and outputs a new CSV. Pretrained vectors can be
downloaded from Dropbox.
Example: `python preprocess.py doc2vec-model.gs data.csv`

The current run.sh hence only runs the SVM and the sentiment based logistic regression. The data file names are unfortunately also hardcoded,
and one would need to download the associated files to run them.