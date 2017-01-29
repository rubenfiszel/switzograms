import networkx as nx
import warnings
warnings.filterwarnings('ignore')
from tqdm import tqdm
from collections import defaultdict
from helpers import *
import datetime
import jsonpickle
from tqdm import tqdm
import numpy as np
import jsonpickle.ext.numpy as jsonpickle_numpy
import pickle
jsonpickle_numpy.register_handlers()

def filter_stops(stop_tile, tile_stop):
    pass;

def process_graph(G, stop_tile):
    pass;

def compute_all_paths(G, nodes):
    print("Run dijkstra", datetime.datetime.now().time())
    print("End", datetime.datetime.now().time())
    n_to_i = {}
    i = 0
    for n in nodes:
        n_to_i[n] = i
        i += 1

    matrix = np.zeros((len(nodes), len(nodes)))
    for source in tqdm(nodes):
        length = nx.shortest_path_length(G, source=source, weight="weight")
        length = defaultdict(lambda: -1, length)
        for target in nodes:
            matrix[n_to_i[source]][n_to_i[target]] = float(length[target])

    return nodes, matrix.tolist()

def write_all_paths(nodes, matrix):
    with open("../res/full_nodes", "w+") as nodes_file:
        nodes_file.write(jsonpickle.encode(nodes))

    with open("../res/full_matrix", "w+") as matrix_file:
        matrix_file.write(jsonpickle.encode(matrix))

    nodes_file.close()
    matrix_file.close()

    print("Written", datetime.datetime.now().time())

def load_paths():
    with open("nodes", "w") as nodes_file:
        nodes = jsonpickle.decode(nodes_file.read())

    with open("matrix", "w") as matrix_file:
        matrix = jsonpickle.decode(matrix_file.read())

    return nodes, matrix

if __name__ == "__main__":
    print("Load graph", datetime.datetime.now().time())
    G = nx.read_gpickle("complete.graph")
    with open('../res/full_nodes', 'rb') as f:
        nodes = pickle.load(f)
    print(nodes[:10])
    # nodes = G.nodes()[:50] ##TOREPLACEALEXISBYYOURTHING
    nodes, matrix = compute_all_paths(G, nodes)
    write_all_paths(nodes, matrix)
