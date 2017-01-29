import pandas as pd

gtfs = ""

stops = pd.read_csv(gtfs + "stops.txt")[["stop_id", "stop_lat", "stop_lon", "platform_code"]]
transfers = pd.read_csv(gtfs + "transfers.txt")
routes = pd.read_csv(gtfs + "routes.txt")[["route_id", "route_short_name", "route_long_name", "route_type"]]
trips = pd.read_csv(gtfs + "trips.txt")[["route_id", "trip_id"]]
stop_times = pd.read_csv(gtfs + "stop_times.txt")[["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"]]


def remove_platform(x):
    return int(str(x).split(":")[0])

def first(x):
    return x.iloc[0]

transfers = transfers[transfers.transfer_type != 3]
transfers = transfers.drop("transfer_type", 1)
transfers["from_stop_id"] = transfers["from_stop_id"].apply(remove_platform)
transfers["to_stop_id"] = transfers["to_stop_id"].apply(remove_platform)
transfers = transfers.drop_duplicates()
transfers = transfers[transfers.from_stop_id != transfers.to_stop_id]


stops["stop_id"] = stops["stop_id"].apply(remove_platform)
stops["platform_code"] = stops["platform_code"].fillna(0)
stops = stops.groupby("stop_id").agg({"stop_lat": first, "stop_lon": first, "platform_code": pd.Series.nunique})
stops = stops.reset_index()

stop_times["stop_id"] = stop_times["stop_id"].apply(remove_platform)

stop_times.to_csv("stop_times.txt")
trips.to_csv("trips.txt")
routes.to_csv("routes.txt")
transfers.to_csv("transfers.txt")
stops.to_csv("stops.txt")

stop_times.head().to_csv("stop_times.txt.mini")
trips.head().to_csv("trips.txt.mini")
routes.head().to_csv("routes.txt.mini")
transfers.head().to_csv("transfers.txt.mini")
stops.head().to_csv("stops.txt.mini")


