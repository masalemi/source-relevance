# LDA Source Relevance

This repository contains a set of Python scripts to visualize source relevance in a NELA database.


## Prerequisites

The python scripts require Python 3.x and the following modules which can be installed using pip3.

* numpy
* gensim
* nltk
* pyldavis
* networkx

Note that if nltk stopwords have not been used before a `LookupError` may occur. This error can be resolved by running the following command.
```
python3 -m nltk.downloader stopwords
```

These scripts were written to support the NELA database schema. The example query uses text matching so in order to run it on a NELA database, run the following 

In order to run a query which uses keyword matching such as the example script first create a table with text indices. First run sqlite3 with the database selected:
```
sqlite3 ../databases/nela_eng-2020.db
```
Next, run the following commands in SQLite3:
```
DROP TABLE newscontent;
CREATE VIRTUAL TABLE newscontent USING fts5(textcontent, title);
INSERT INTO newscontent(rowid, textcontent, title)
SELECT rowid, content, title from newsdata;
```

The scripts provided do not require a NELA database. Any SQLite3 can be used on a database which returns rows in the form of:
```
(unique_id, text_content, text_source)
```

## Steps

To use the scripts, navigate to the scripts subdirectory and follow the below steps. Replace the path for the result working directory to an existing directory.

1. Edit `query.sql` to desired keywords, time period, and article limit.
1. Run `csv_query.py` to remove duplicate articles and generate `data.csv` containing relevant rows.\
Ex: `python3 csv_query.py ../databases/nela_eng-2020.db query.sql ../results/data1.csv`

1. (Optional) Run `lda_k.py` to find perplexities for each number of topics in range 1 to 20.\
Ex: `python3 lda_k.py ../results/data1.csv`

1. Run `lda.py` with a chosen number of topics to generate `period1_article_topics.csv` containing topic probably distribution per article and `period1.html` the pyLDAvis visualization for the given period. Two compressed pickle files containing topic probability distributions for each word and article are also created for later use.\
Ex: `python3 lda.py ../results/data1.csv 10 ../results/period1`

1. (Optional) Run `lda_sources.py` to generate contents for a source pyLDAvis visualization. To create the visualition, make a copy of the html file from the previous step and replace from the first `"Freq":` to before `, "R":` with the output.\
Ex: `python3 lda_sources.py ../results/data1.csv 10 ../results/period1`

1. Run `topic_similarity.py` to generate compressed pickle files containing pairwise cosine similarity between topics in adjacent time periods.\
Ex: `python3 topic_similarity.py ../results/period`

1. Run `graph_paths.py` to generate `period_paths.png`, a graph of topic similarity over time. If a specific time and topic is specified, the path containing the topic will be highlighted in the graph and the top words and sources for the path will be printed.\
Ex: `python3 graph_paths.py ../results/period 3 5`


## References

* NELA 2020 Database - TBD
* pyLDAvis - https://github.com/bmabey/pyLDAvis