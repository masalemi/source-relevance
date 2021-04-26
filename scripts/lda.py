from gensim import corpora, models, similarities
import time
import pyLDAvis.gensim
import string
import nltk
import phrasemachine
import csv
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import pickle
import sys

stops = set(stopwords.words("english"))
stops.add('said')
stops.add('')
stops.add('•')
stops.add('–')
stops.add('©')

def get_doc_topic(corpus, model, id_to_bow): #this gets the distribution per doc back.
    id_to_topic = {}
    for id in id_to_bow.keys():
        top_arr = model.__getitem__(id_to_bow[id], eps=0)
        id_to_topic[id] = top_arr
    return id_to_topic

def run_lda(id_to_text, html_fn, n_topics):
    
    id_to_text = {i[0]:i[1].split(" ") for i in id_and_text}

    print("creating dictionaries...")
    dictionary = corpora.Dictionary(id_to_text.values())
    id_to_bow = {id:dictionary.doc2bow(text) for id, text in id_to_text.items()}
    corpus = [dictionary.doc2bow(text) for text in id_to_text.values()]

    print('starting LDA')
    start = time.time()
    lda = models.ldamodel.LdaModel(corpus,
                               num_topics=n_topics,
                               alpha='auto',
                               id2word=dictionary,
                               iterations=1000,
                               random_state=1)
    end = time.time()
    print('lda took: ', end-start, ' seconds')
    print('starting PyLDAvis')
    start = time.time()
    viz(lda, corpus, dictionary, html_fn)
    end = time.time()
    print('PyLDAvis took: ', end-start, ' seconds')

    return lda, get_doc_topic(corpus, lda, id_to_bow), dictionary

def viz(lda, corpus, dictionary, html_fn):
    lda_visualization = pyLDAvis.gensim.prepare(lda, corpus, dictionary, sort_topics=False)
    pyLDAvis.save_html(lda_visualization, html_fn)

#main <----------------
k = int(sys.argv[2])
fn = sys.argv[1]
csv.field_size_limit(524288)
print("reading in text data...")
id_and_text = []
id_to_source = dict()
with open(fn, newline='') as data:

    reader = csv.reader(data)

    for line in reader:

        idn = line[0]
        text = line[1]
        id_to_source[idn] = line[2]

        text = text.replace('‘', '\'').replace('’', '\'').replace('“','"').replace('”','"').replace('—', '-').replace('…', '...').replace('\n', ' ')

        text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation))).lower()

        word_list = text.split(" ")

        go_words = [word for word in [word for word in word_list if word not in stops]]

        text = ' '.join(go_words)

        id_and_text.append((idn, text))


lda, id_to_topic, dictionary = run_lda(id_and_text, sys.argv[3] + ".html", k)
with open(sys.argv[3] + "_article_topics.csv", "w") as out:
    topic_header = [str(r) for r in range(k)]
    out.write("id,source,"+",".join(topic_header)+"\n") #header
    for id in id_to_topic.keys():
        portion_strs = [str(p[1]) for p in id_to_topic[id]]
        out.write(id+","+id_to_source[id]+","+",".join(portion_strs)+"\n")

if (len(dictionary) != lda.get_topics().shape[1]):
    print("ERROR")

print(lda.get_topics().shape)
print(len(id_and_text))

with open(sys.argv[3] + '_term_relevances' + '.pickle', 'wb') as file:
    pickle.dump(lda.show_topics(num_topics=k, num_words=len(dictionary), formatted=False), file)

article_count = 0
sources = dict()
for id in id_to_topic.keys():
    source = id_to_source[id]
    if source not in sources.keys():
        sources[source] = np.zeros(k)
    for v in id_to_topic[id]:
        if v[1] >= 0.6:
            sources[source][v[0]] += 1
            article_count += 1

source_order = sorted([(i, source) for i, source in enumerate(sources.keys())])

table = np.zeros((k, len(source_order)))

for i, source in source_order:
    table[:, i] = sources[source]

for i in range(k):
    table[i, :] /= np.sum(table[i, :])

relevances = dict()
l = 0.6

for j, source in source_order:

    v = np.array([np.log(0)] * k)

    if (np.sum(sources[source]) > 0):
        for i in range(k):
            phi = table[i][j]
            logprob = np.log(phi)
            loglift = np.log(phi / (np.sum(sources[source]) / article_count))
            relevance = l * logprob + (1 - l) * loglift
            v[i] = relevance

    relevances[source] = v

with open(sys.argv[3] + '_source_relevances' + '.pickle', 'wb') as file:
    pickle.dump(relevances, file)
