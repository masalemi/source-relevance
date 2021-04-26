import pickle
import numpy as np
import sys
from pathlib import Path

def load_data(file_name):

    raw_data = []

    data = []

    with open(file_name, 'rb') as file:
        raw_data = pickle.load(file)

    for i in range(len(raw_data)):

        if raw_data[i][0] != i:
            print("Wrong index")
            return 0

        topic = dict()

        for word, prob in raw_data[i][1]:
            topic[word] = prob

        data.append(topic)

    return data


def process(topic1, topic2):

    all_words = set(topic1.keys()) | set(topic2.keys())

    v1 = np.zeros(len(all_words))
    v2 = np.zeros(len(all_words))

    index = 0

    for word in all_words:
        v1[index] = topic1.get(word, 0)
        v2[index] = topic2.get(word, 0)

        index += 1

    cos_sim = np.inner(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    return cos_sim


def num_label(s):

    i = -1

    for j, c in enumerate(s):
        if c.isdigit():
            i = j
            break

    num = ""
    while s[i].isdigit():
        num += str(s[i])
        i += 1

    return int(num)

def pair(data1, data2, base, n):

    m = np.zeros((len(data1), len(data2)))

    for i in range(len(data1)):
        for j in range(len(data2)):
            m[i][j] = process(data1[i], data2[j])

    np.set_printoptions(linewidth=np.inf)
    csv_name = base + str(n) + '-' + base[base.rfind('/') + 1:] + str(n + 1) + ".csv"
    np.savetxt(csv_name, m, delimiter=",", fmt='%f')

def main():

    base = sys.argv[1]

    matrices = []

    i = 1

    while True:

        file_name = base + str(i) + '_term_relevances' + ".pickle"

        my_file = Path("./" + file_name)

        if not my_file.is_file():
            break

        matrices.append(load_data(file_name))

        i += 1

    for i in range(len(matrices) - 1):

        pair(matrices[i], matrices[i + 1], base, i + 1)

main()