import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from sklearn.decomposition import LatentDirichletAllocation as LDA
import os
import sklearn as sklearn_lda
import string
import nltk
import csv
from nltk.corpus import stopwords
import sys

stops = set(stopwords.words("english"))
stops.add('said')
stops.add('')
stops.add('•')
stops.add('–')
stops.add('©')

def test_topic_ks(text, ck = 20, number_words = 10): #text is a list of documents
    print("cleaning and vectorizing....")

    for i in range(len(text)):

        text[i] = text[i].replace('‘', '\'').replace('’', '\'').replace('“','"').replace('”','"').replace('—', '-').replace('\n', ' ')

        text[i] = text[i].translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).lower()

        word_list = text[i].split(" ")

        go_words = [word for word in [word for word in word_list if word not in stops]]

        text[i] = ' '.join(go_words)

    count_vectorizer = CountVectorizer(stop_words='english')
    count_data = count_vectorizer.fit_transform(text)
    # plot_10_most_common_words(count_data, count_vectorizer)

    print("Testing Numbers of Topics (k)")
    cks = range(ck)
    candidate_ks = cks[1:] #could filter to every other, but for now keep as is
    prev_prep = 0

    print("{:<3}\t{:<7}\t{:<7}".format('k:', 'perplexity:', 'delta:'))
    for number_topics in candidate_ks:
        # print("K =", number_topics)
        lda = LDA(n_components=number_topics, n_jobs=-1)
        lda.fit(count_data)

        perp = lda.perplexity(count_data)

        print("{:<3}\t{:<7.3f}\t{:<7.3f}".format(number_topics, perp, perp - prev_prep))
        prev_prep = perp


#main
fn = sys.argv[1]
csv.field_size_limit(524288)
print("reading in text data...")
text = []
with open(fn, newline='') as data:

    reader = csv.reader(data)

    for line in reader:

        text.append(line[1])

test_topic_ks(text)
