import networkx as nx
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')
import time
from collections import defaultdict
from helpers import *

    
def create_graph(stop_times, trips, routes, transfers):
    G=nx.DiGraph()

    print("GRAPH CREATION ...")

    tqdm.pandas()
    
    s_id = None
    start_time = None
    pstop = None
    def to_time(x):        
        nonlocal s_id, start_time, pstop
        n_id = x["trip_id"]
        if s_id != n_id:
            start_time = t_str(x["departure_time"])
            time = 0
        else:
            time = t_str(x["arrival_time"]) - start_time                    
        s_id = n_id
        start_time = t_str(x["departure_time"])
        stop_id = x["stop_id"]
        if pstop == 8502204 and stop_id == 8504200:
            print("FIRST")
            print(time)
        pstop = stop_id
        return time

    print("shape of stop_times", stop_times.shape[0])
    stop_times["time"] = stop_times.progress_apply(to_time, axis=1)
    print(stop_times)
    
    print("TIME DISTANCE CALCULATED")
    trip_to_route = defaultdict(lambda: None)
    
    def assign(x):
        trip_to_route[x["trip_id"]] = x["route_id"]
        
    trips.progress_apply(assign, axis=1)
        
    stop_times["route_id"] = stop_times["trip_id"].progress_apply(lambda x: trip_to_route[x])
    print("ROUTE ADDED TO TRIPS")    

#    stop_times2 = stop_times.groupby(["route_id", "stop_sequence", "stop_id"]).min()
#    stop_times = stop_times2["time"].to_frame().reset_index()
    print("MEAN TIME DISTANCE")

 #   stop_times.to_pickle("tmpickle")

    s_id = None
    def stop_edge(x):
        nonlocal s_id
        ns_id = x["stop_id"]
        if x["stop_sequence"] != 0:
            if s_id == 8502204 and ns_id == 8504200:
                print(str(x["time"]) + " " + str(x["stop_sequence"]) + " " + str(type(x["stop_sequence"])))
            G.add_edge(s_id, ns_id, weight=x["time"])
        s_id = ns_id

    stop_times.progress_apply(stop_edge, axis=1)

    for a, b, c in G.edges(data=True):
            if a == 8502204 and b == 8504200:
                print("first")
                print(c)
    def transfer_edge(x):
        G.add_edge(x["from_stop_id"], x["to_stop_id"], weight=x["min_transfer_time"]/60)
        
    transfers.progress_apply(transfer_edge , axis=1)

    for a, b, c in G.edges(data=True):
            if a == 8502204 and b == 8504200:
                print("second")
                print(c)
    
    
    return G

if __name__ == "__main__":
    stops, transfers, routes, trips, stop_times = load_csv()
    G = create_graph(stop_times, trips, routes, transfers)
    nx.write_gpickle(G, "complete.graph")
    print(len(G.edges()))
    print(len(G.nodes()))

