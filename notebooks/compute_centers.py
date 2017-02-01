
# coding: utf-8

# In[1]:

import networkx as nx
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import sys
import math
import pickle
import jsonpickle
import csv

n_tiles = pd.read_csv('../qgis/hexagons_centers.csv').shape[0]
print("# of tiles: ", n_tiles)

stops_with_ids = pd.read_csv("../qgis/stops_with_tile_ids.csv", usecols = ['ID','stop_id'])
stops_with_ids = stops_with_ids.set_index('stop_id')

# # Computing centers of hexagons
# ## Graph
G = nx.read_gpickle('../graph/complete.graph')

stops_with_ids['degree'] = 0

# For the hexagons where no affluence data is available from official **SBB/CFF** sources, we use the max node-degree in the cell as affluence.

nodes = G.nodes()

errors = 0
for n in nodes:
    try:
        stops_with_ids.loc[n].degree = G.degree(n)
    except KeyError:
        errors += 1

print("Nodes missing in graph: {}/{}, when matched with `stops_with_ids`".format(errors, len(nodes)))

# Groupby the hexagon ID and aggregate by max affluence.

grouped_by_degree = stops_with_ids.reset_index().groupby('ID')['stop_id', 'degree'].agg({'degree': max})
grouped_by_degree.columns = grouped_by_degree.columns.droplevel()
grouped_by_degree.head()

missing = grouped_by_degree[grouped_by_degree.degree == 0].shape[0]
total = grouped_by_degree.shape[0]
print("After grouping, missing degree data for {}/{} cells".format(missing, total))

# ## Affluence for available nodes

affluence = pd.read_csv("passagierfrequenz.csv", sep=';')
affluence['x'], affluence['y'] = affluence.geopos.str.split(',', 1).str
affluence = affluence.drop(['Bahnhof_Haltestelle', 'DWV', 'Bemerkungen', 'lod', 'geopos', 'Eigner', 'Bezugsjahr'], axis=1)
affluence.columns = ['Code', 'Affluence', 'x', 'y']
affluence['stop_id'] = 0

affluence_with_ids = pd.read_csv("../qgis/affluence_with_tile_ids.csv")

joined_aff = affluence.join(affluence_with_ids, rsuffix='_r').drop(
        ['x', 'y', 'Code_r', 'stop_id', 'Code'], axis=1)
grouped_by_affluence = joined_aff.groupby('ID').agg(max).reset_index()

print("Centers with affluence data: {}".format(grouped_by_affluence.shape[0]))

# ## Combine results

affluence = affluence.join(affluence_with_ids, rsuffix='_r').drop(['Code_r'], axis=1)

stops = pd.read_csv('../gtfs/stops.txt').drop(['Unnamed: 0', 'platform_code'], axis=1)

# ### Get closest stop match by euclidean distance between coordinates -> heuristic
# Result stored in `gtfs/affluence_with_stopid.csv`
#
# **WARNING**: takes some time to compute

print("Matching affluence data coordinates with closest stop_id")
MAX_SIZE = sys.maxsize
for i in range(affluence.shape[0]):
    min_ = MAX_SIZE
    min_id = None
    x1 = float(affluence.loc[i].x)
    y1 = float(affluence.loc[i].y)
    for j in range(stops.shape[0]):
        x2 = float(stops.loc[j].stop_lat)
        y2 = float(stops.loc[j].stop_lon)
        dist = math.sqrt(pow(abs(x1-x2),2) + pow(abs(y1 - y2),2))
        if dist < min_:
            min_ = dist
            min_id = stops.loc[j].stop_id
    affluence.set_value(i, 'stop_id', min_id)
    if (i%25 == 0):
        print("{}/{}".format(i, affluence.shape[0]))

affluence.to_csv('affluence_with_stopid.csv')

# **Instead** use pre-computed file below

affluence = pd.read_csv('affluence_with_stopid.csv')
affluence.drop(['Unnamed: 0'], axis=1, inplace=True)

# Merge max affluence nodes for each cell with corresponding stop_id (gtfs format).

affluence_stop_ids = grouped_by_affluence.merge(affluence, left_on=['ID', 'Affluence'],
                          right_on=['ID', 'Affluence'])[['ID', 'stop_id']]

# Combine the results from affluence and degree to one collection

cell_centers = grouped_by_degree.drop(['degree'], axis=1)
for i in range(affluence_stop_ids.shape[0]):
    cell_id = affluence_stop_ids.loc[i].ID
    stop_id = affluence_stop_ids.loc[i].stop_id
    cell_centers.set_value(cell_id, 'stop_id', stop_id)


# Get list of all centers
#
# ## IMPORTANT: sort the centers by tile-id

cell_centers = cell_centers.reindex(range(1, n_tiles+1), fill_value=0)

lst_centers = list(map(lambda x: int(x), cell_centers.stop_id))

nodes = G.nodes()
filt_centers = []
for c in lst_centers:
    if c in nodes:
        filt_centers.append(c)
    else:
        filt_centers.append(0)

with open('../res/center_nodes', 'wb') as f:
    pickle.dump(filt_centers, f)
