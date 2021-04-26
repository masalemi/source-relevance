import sqlite3
import csv
import sys
from collections import Counter


def clean(rows):

    exclude = set()
    tracker = dict()
    original = Counter()
    sources = set()

    repeats = 0
    non_english = 0
    both = 0

    for row in rows:

        id = row[0]
        text = row[1]
        source = row[2]

        if source not in tracker.keys():
            tracker[source] = set()

        if text not in tracker[source]:
            tracker[source].add(text)
            original[source] += 1
        else:
            exclude.add(id)
            repeats += 1

    minimum_articles = 0

    new_rows = []

    for row in rows:

        id = row[0]
        source = row[2]

        if id not in exclude and original[source] > minimum_articles:
            new_rows.append(row)
            sources.add(source)

    print("Total number of articles before cleaning: {}".format(len(rows)))
    print("Total number of articles after cleaning: {}".format(len(new_rows)))
    print("Removed {} total articles ({:.3f}%)".format(len(exclude), float(len(exclude)) / len(rows)))
    print("Articles came from {} sources".format(len(sources)))

    return new_rows
        

def main():

    conn = None
    try:
        conn = sqlite3.connect(sys.argv[1])
    except Error as e:
        print(e)
        return 1

    c = conn.cursor()

    sql_file = open(sys.argv[2], 'r');

    query = sql_file.read()

    sql_file.close()

    c.execute(query)

    rows = c.fetchall()

    rows = clean(rows)

    print("Writing", len(rows), "rows")

    max_len = 0

    with open(sys.argv[3], 'w', newline='') as file:

        writer = csv.writer(file)

        for row in rows:
            writer.writerow(row)
            max_len = max(max_len, len(row[1]))

    print("Max Field Length:", max_len)


if __name__ == '__main__':
    main()
