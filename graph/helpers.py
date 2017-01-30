import pandas as pd
from collections import defaultdict

def t_str(t):
    t = t.split(":")
    return int(t[0])*60 + int(t[1])

def load_csv(mini=False):
    gtfs = "../gtfs/"

    mini_str = ""
    if mini:
        mini_str += ".mini"

    stops = pd.read_csv(gtfs + "stops.txt" + mini_str)
    transfers = pd.read_csv(gtfs + "transfers.txt" + mini_str)
    routes = pd.read_csv(gtfs + "routes.txt" + mini_str)
    trips = pd.read_csv(gtfs + "trips.txt" + mini_str)
    stop_times = pd.read_csv(gtfs + "stop_times.txt" + mini_str)
    return stops, transfers, routes, trips, stop_times

def load_stop_tile():
    qgis = "qgis/"
    csv = pd.read_csv("stops_with_tile_ids.csv")
    stop_tile = {}
    tile_stop = defaultdict(list)        
    for _, t in csv.iterrows():
        stop_tile[t["stop_id"]] = t["tile_id"]
        tile_stop[t["tile_id"]].append(t["tile_id"])
    return stop_tile, tile_stop
        
