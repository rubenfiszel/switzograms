
# coding: utf-8

# In[451]:

import pandas as pd
import numpy as np
import math
import warnings
warnings.filterwarnings('ignore')


# # Create hexagon map of Switzerland

# ## QGIS -  Geographic Information System

# **QGIS** is a great software to create and edit geospatial information. In order to create an hexagon map of Switzerland, we used the **MMQGIS** plugin which facilitates manipulating vector map layers. We proceded as follows:
# * *Obtain Swtizerland bounderies*: bounderies of all countries can be obtained from the shape file *50m_admin_0_countries.shp* from *Natural Earth* data.
# * *Create hexagon tiles*: MMQGIS plugin offers the possibility to create hexagonal *grid layers*.
# * *Combine layers*: we obtain the desired hexagons by doing an intersection between the country layer and the grid layer.
# * *Tile ID and coordinates*: we add to the table attributes of the grid layer and ID to each hexagonal tile and the coordinates of the center
# * *Export hexagonal tiles*: we can export with MMQGIS a CSV file containing the table attributes

# ### Generate centers of hexagons

# Centers are converted into coordinates suitable for **WebGL**. They are centered and divided by 1000.

# In[452]:

centers = pd.read_csv("../qgis/hexagons_centers.csv", usecols = ['x','y','ID'])


means = centers.mean()


# In[454]:

centers['x'] = (centers['x']-means['x'])/1000.0


# In[455]:

centers['y'] = (centers['y']-means['y'])/1000.0


# ### Merge stations and hexagonal tiles

# The stops with their coordinates (obtained from *https://transport.opendata.ch*)are imported in QGIS as as CSV file. We perform an intersection between the stops and the grid layer including attributes of both tables to get the tile ID for each stop. We can then export a file *stops_with_tile_ids.csv*.

# ## Create the JSON file for the stops

# In[43]:

points = pd.read_csv("../qgis/stops_coordinates.csv", usecols = ['x','y','stop_id'])
stops_with_ids = pd.read_csv("../qgis/stops_with_tile_ids.csv")
points['x'] = (points['x'] - means['x'])/1000.0
points['y'] = (points['y'] - means['y'])/1000.0

# In[45]:

temp = pd.merge(stops_with_ids, points, how='inner')


# In[47]:

points = pd.merge(temp, centers[['ID', 'h']])


# In[51]:

points.to_json("../res/stops.json", orient="records")


# # Create JSON of Cities with geolocalisation and population

# We need a JSON file containing the different cities of Switzerland with their respective population and geographical coordinates in order to display the most important ones on the map.

# The population file comes from the *Federal Statistical Office* and can be downloaded here: *https://www.bfs.admin.ch/bfs/en/home/statistics/population/surveys/statpop.html*. We need to get the coordinates of each city so we use the *GeoNames* server.

# In[ ]:

cities = pd.read_csv("qgis/cities_population.csv")

# In[36]:

from geopy.geocoders import GeoNames
geolocator = GeoNames(country_bias="Switzerland",username="ada_dream_team")

for i in cities.index[2001:]:
    newName = cities.ix[i,'Commune'][5:]
    location = geolocator.geocode(newName)
    if location:
        cities.ix[i,'x'] = location.longitude
        cities.ix[i,'y'] = location.latitude
        cities.ix[i,'Commune'] = newName
    else:
        cities.ix[i,'x'] = np.nan
        cities.ix[i,'y'] = np.nan


# In[52]:

cities_complete = cities.dropna()


# In[58]:

cities_complete.to_csv("map_js/cities_coordinates.csv", index=False)


# ### Inbetween we took the tile ID with QGIS, now we create the json

# In[28]:

c = pd.read_csv("map_js/cities_full.csv")

# In[30]:

import json
import unicodedata
cities_json = {}
for name, pop, tile_id, x , y in zip(c.Commune, c.Total, c.ID, c.x, c.y):
    if isinstance(name, str):
        n = str(unicodedata.normalize('NFD', name).encode('ascii', 'ignore'))[2:-1]
        cities_json[n] = {"population": str(pop), "ID": str(tile_id), "x":str(x),"y":str(y)}

# In[32]:

json.dumps(cities_json)


# In[71]:

with open('map_js/cities.json', 'w') as outfile:
    json.dump(cities_json, outfile)


# In[21]:

stops = pd.read_csv("../qgis/stops_with_tile_ids.csv")

# ## Population tile-heights

from sklearn import preprocessing


# In[457]:

stops_n_pop = pd.read_csv('../qgis/cities_full.csv')
grouped_pop = stops_n_pop.groupby('ID').agg({'Total': sum})


# In[458]:

def counter(df):
    if df['ID'] in grouped_pop.index:
        return grouped_pop.loc[int(df['ID'])]['Total']
    else:
        return 0.0

centers['h'] = (centers.apply(counter, axis=1))

x = centers['h'].values #returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler(feature_range=(1,50))

# Root-scaling
root = lambda x: math.pow(x, 0.6)
x_rooted = centers.h.apply(root)
x_rooted = min_max_scaler.fit_transform(x_rooted)
centers['h'] = x_rooted


# * x, y and ID are already in "qgis/hexagons_centers.csv". Need to add height h (affluence) and export JSON as "centers.json"
# * need to do the same for the heights of stops: "qgis/stops_with_tile_ids.csv", add corresponding height of the tile

centers.to_csv("../res/centers.csv", index=False)


centers.to_json("../res/centers.json",orient="records")
