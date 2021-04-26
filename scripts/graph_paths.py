import numpy as np
import sys
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import pickle
from collections import Counter

def read_matrices(base):

    matrices = []

    i = 1

    while True:

        csv_name = base + str(i) + "-" + base[base.rfind('/') + 1] + str(i + 1) + ".csv"

        my_file = Path(csv_name)

        if not my_file.is_file():
            break

        matrix = np.loadtxt(csv_name, delimiter=",")
        matrices.append(matrix)

        i += 1

    return matrices


def load_relevances(base, matrices):

    relevances = []

    for i in range(1, len(matrices) + 2):

        with open(base + str(i) + '_source_relevances.pickle', 'rb') as file:
            
            relevances.append(pickle.load(file))

    return relevances


def load_words(base, matrices):

    words = []

    for i in range(1, len(matrices) + 2):

        time = []

        raw_data = []

        with open(base + str(i) + "_term_relevances.pickle", 'rb') as file:
            raw_data = pickle.load(file)

        for j in range(len(raw_data)):

            word_data = raw_data[j][1]

            topic = Counter()

            for word, prob in word_data:
                topic[word] = prob

            time.append(topic)

        words.append(time)

    return words


def path_sources(paths, relevances, word_freq):

    for k, path in enumerate(paths):

        print("Path #{}, Color: {}".format(k + 1, path[1]))

        nodes = set()

        for edge in path[0]:
            nodes.add(edge[0])
            nodes.add(edge[1])
        
        times = set()
        sources = dict()

        word_rel = []

        for _ in range(len(relevances)):
            word_rel.append(Counter())

        for node in nodes:

            time = node[0]
            topic = node[1]

            if time not in times:
                times.add(time)

            for word in word_freq[time][topic]:

                phi = word_freq[time][topic][word]

                logprob = np.log(phi)

                marg_prob = sum([word_freq[time][i][word] for i in range(len(word_freq[time]))])

                loglift = np.log(phi / marg_prob)
                l = 0.6

                relevance = l * logprob + (1 - l) * loglift

                if word not in word_rel[time]:
                    word_rel[time][word] = float('-inf')

                word_rel[time][word] = max(word_rel[time][word], relevance)

            for source in relevances[time].keys():

                if source not in sources.keys():
                    sources[source] = np.array([float('-inf')] * len(relevances))

                relevance = relevances[time][source][topic]

                sources[source][time] = max(relevance, sources[source][time])

        word_cutoffs = np.array([float('-inf')] * len(relevances))

        for i in range(len(word_cutoffs)):

            if i in times:

                rels = [word_rel[i][word] for word in word_rel[i] if word_rel[i][word] > float('-inf')]

                word_cutoffs[i] = np.mean(rels) + np.std(rels)

        best_words = Counter()

        for i in range(len(word_rel)):

            for word in word_rel[i].keys():

                if word_rel[i][word] == float('-inf'):
                    print("ERROR")
                    return

                if word_rel[i][word] > word_cutoffs[i]:

                    best_words[word] += (word_rel[i][word] - word_cutoffs[i]) ** 3

        print("Top 5 Path Words: " + " ".join([word for word, count in best_words.most_common(5)]))

        cutoffs = np.array([float('-inf')] * len(relevances))

        for i in range(len(cutoffs)):

            if i in times:

                rels = [sources[source][i] for source in sources if sources[source][i] > float('-inf')]

                cutoffs[i] = np.mean(rels) + np.std(rels)

        order = sorted([(np.sum(sources[source] > cutoffs), source) for source in sources.keys()], reverse=True)

        used_times = sorted(times)

        print("Source info:")

        for n, source in order:

            if n == 0:
                break

            vis = ['+' if r else '-' for r in sources[source][sorted(list(used_times))] >= cutoffs[sorted(list(used_times))]]

            source_name = source

            if len(source) > 30:
                source_name = source[:27] + '...'

            print("{:<3} {:<30} {}".format(n, source_name, ''.join(vis)))


def valid_edges(edges, matrix, curr):

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] > 0.8 or (matrix[i][j] == max(matrix[i, :]) and matrix[i][j] > 0.6):
                edges.add(((curr, i), (curr + 1, j)))


def find_all_edges(matrices):

    edges = set()

    for i, matrix in enumerate(matrices):
        valid_edges(edges, matrix, i)

    return edges


def generate_graph(matrices, edges):

    G = nx.DiGraph()

    for i in range(len(matrices)):
        for j in range(len(matrices[i])):
            G.add_node((i, j), pos=(i + 1, j + 1))
    
    for j in range(len(matrices[-1][0])):
        G.add_node((len(matrices), j), pos=(len(matrices) + 1, j + 1))

    for edge in edges:
        G.add_edge(edge[0], edge[1])

    return G


def make_path(G, origin, color, matrices, edges):

    x, y = origin

    starts = set([y])
    ends = set([y])

    chain = set()

    # Iterate forwards
    for i in range(x, len(matrices)):

        used = [edge for edge in edges if edge[0][0] == i and edge[0][1] in starts]

        for edge in used:
            chain.add(edge)

        starts = set([edge[1][1] for edge in used])


    # Iterate backwards
    for i in range(x - 1, -1, -1):

        used = [edge for edge in edges if edge[1][0] == i + 1 and edge[1][1] in ends]

        # Color the valid edges here
        for edge in used:
            chain.add(edge)

        ends = set([edge[0][1] for edge in used])

    return (chain, color, origin)


def apply_colors(G, color_paths):

    edge_colors = []
    node_colors = []

    for edge in G.edges():
        edge_colors.append("black")
        for path in color_paths:
            if edge in path[0]:
                edge_colors[-1] = path[1]  

    for node in G.nodes():
        node_colors.append("black")
        for path in color_paths:
            if node == path[2]:
                node_colors[-1] = path[1]

    print(len(edge_colors), len(node_colors))

    return edge_colors, node_colors


def save_graph(G, edge_colors, node_colors, matrices):

    width = len(matrices) + 1
    height = max([max(len(m), len(m[0])) for m in matrices])

    f = plt.figure()
    ax = plt.subplot(111)
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw(G, pos, node_size=20, edge_color=edge_colors, node_color=node_colors) #, with_labels=True, font_size=4)
    plt.axis("on")
    plt.xticks(np.arange(1, width + 1))
    plt.yticks(np.arange(1, height + 1))
    plt.xlabel("Time")
    plt.ylabel("Topic")
    ax.set_xlim(0, width + 1)
    ax.set_ylim(0, height + 1)
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    plt.savefig(sys.argv[1] + "_paths.png", format="PNG", dpi=1000)


def main():

    # Load in the matrices here

    matrices = read_matrices(sys.argv[1])

    edges = find_all_edges(matrices)

    G = generate_graph(matrices, edges)

    color_paths = []

    if len(sys.argv) > 2:
        time = int(sys.argv[2]) - 1
        topic = int(sys.argv[3]) - 1
        color_paths.append(make_path(G, (time, topic), "r", matrices, edges))

    edge_colors, node_colors = apply_colors(G, color_paths)

    relevances = load_relevances(sys.argv[1], matrices)

    words = load_words(sys.argv[1], matrices)

    path_sources(color_paths, relevances, words)

    save_graph(G, edge_colors, node_colors, matrices)


if __name__ == '__main__':
    main()