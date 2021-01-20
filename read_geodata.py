import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
import argparse
import sys

def getOptions(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(description="Parses command.")
	parser.add_argument("-l", "--location", type=int, help= """Choose your location 
		1: Heinsberg, 
		2: Gangelt,
		3: Penkridge,
		4: Epping,
		5: Stratford-upon-Avon,  
		6: Charlottenlund,
		7: Helsingör,
		8: Bornholms Regionskommune,
		9: Bad Feilnbach,""")
	parser.add_argument("-ma", "--min_area", type=float, help="default 3  (*1e-8) to reduce locations")
	parser.add_argument("-fa", "--from_adress", type=bool, help=" uses osmnx footprints_from_address with 2000 m")
	#parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode.")
	options = parser.parse_args(args)
	return options

def reduce_GDF(gdf,cols):
	#cols = ['building','geometry','amenity','shop','leisure', 'sport','healthcare','healthcare:speciality','building:levels','school_type','type','members']
	cols_2 = [x for x in cols if x in gdf.columns]
	return gdf[cols_2].copy()


def getCentromerCoordiantes(buildings):
	centroid_coords = [x.centroid for x  in buildings['geometry']]
	#centroid_coords_y = [x.centroid.y for x  in buildings['geometry']]
	return centroid_coords

def getArea(buildings):
	return [x.area for x  in buildings['geometry']]

def exclude_small_buildings(red_buildings,minimal_area):
	return red_buildings[red_buildings['building_area']>minimal_area*1e-8].copy()

def closest_n(list_of_n,point):
	'''return index of nearest neighbourhood center'''
	distances = [point.distance(x) for x in list_of_n]        
	return distances.index(min(distances)) 	


options = getOptions(sys.argv[1:])

if options.location:
	#try:
	loc = options.location
	#except:	
else:
	loc = 2

if options.min_area:
	#try:
	min_area = options.min_area
	#except:	
else:
	min_area = 3

# Specify the name that is used to seach for the data
place_name_1 = "Heinsberg, Nordrhein-Westfalen, Germany"
place_name_2 = "Gangelt, Kreis Heinsberg, Nordrhein-Westfalen, Germany"
place_name_3 = "Penkridge, South Staffordshire, Staffordshire, West Midlands, England, ST19 5DJ, Vereinigtes Königreich"
place_name_4 = "Epping, Essex, East of England, England, CM16 4BD, Vereinigtes Königreich"
place_name_5 = "Stratford-upon-Avon, Warwickshire, West Midlands, England, CV37 6AH, Vereinigtes Königreich"
place_name_6 = "Charlottenlund"
place_name_7 = "Helsingör, Helsingør Municipality, Hauptstadtregion, 3000, Dänemark"
place_name_8 = "Bornholms Regionskommune, Hauptstadtregion, Dänemark"
place_name_9 = "Bad Feilnbach, Landkreis Rosenheim, Bayern, 83075, Germany"
#not working for me actually 8892, 7days incidence = 34.74 2.11.2020
place_name_10 = "Bockhorn, Landkreis Friesland, Niedersachsen, 26345, Germany"
#agents: 7399 actually 12431, 7days incidence = 46.7 3.11.2020 
place_name_11 = "Hessisch Lichtenau, Werra-Meißner-Kreis, Regierungsbezirk Kassel, Hessen, 37235, Germany"
#agents: 7447 actually 8242 , 7days incidence = 52.0 3.11.2020
place_name_12 = "Oranienbaum-Wörlitz, Wittenberg, Sachsen-Anhalt, 06785, Germany"
#agents: 9548 actually 9882, 7days incidence = 149.0 2.11.2020
place_name_13 = "Linsengericht, Main-Kinzig-Kreis, Hessen, 63589, Germany"
#agents: 9339 actually 9954, 7days incidence = 287.2 2.11.2020
place_name_14 = "Simbach a.Inn, Landkreis Rottal-Inn, Bayern, 84359, Germany"


# definied center of neihbourhoods - freely choosen 
list_of_n_1 = [Point(6.1,51.06),Point(6.075,51.05),Point(6.145,51.035),Point(6.07,51.10)] 
list_of_n_2 = [Point(5.99,51.03),Point(6.05,51.01),Point(6.04,50.98),Point(5.99,50.99)]
list_of_n_3 = [Point(-2.08,52.42)]
list_of_n_4 = [Point(0.06,51.41)]
list_of_n_5 = [Point(-1.70,52.19)]
list_of_n_6 = [Point(12.57,55.76)]
list_of_n_7 = [Point(12.60,56.03)]
list_of_n_8 = [Point(14.88,55.11)]
list_of_n_9 = [Point(47.7728352, 12.0062484),Point(47.7973373, 11.9747759),Point( 47.7610224, 12.0510184)]
list_of_n_10 = [Point(8.0172, 53.39422),Point(7.99973, 53.3675)]
list_of_n_11 = [Point(9.70088,51.22621),Point(9.69110,51.21141),Point(9.72293,51.19661),Point(9.76303,51.17931),Point(9.79662,51.21392),Point(9.82794,51.20514),Point(9.64599,51.19812)]
list_of_n_12 = [Point(12.42153,51.84190),Point(12.40572,51.79565),Point(12.34469,51.80463),Point(12.35341,51.84544)]
list_of_n_13 = [Point(9.17492,50.16440),Point(9.18954,50.15995),Point(9.21508,50.17192),Point(9.23338,50.18020),Point(9.19677,50.18895),Point(9.19646,50.14921)]
list_of_n_14 = [Point(13.00774,48.273556),Point(13.008913,48.260859),Point(13.020287,48.2657),Point(13.031493,48.27723),Point(13.04637,48.275227)]

places = {1: [place_name_1,list_of_n_1],
          2: [place_name_2,list_of_n_2],
          3: [place_name_3,list_of_n_3],
          4: [place_name_4,list_of_n_4],
          5: [place_name_5,list_of_n_5],
          6: [place_name_6,list_of_n_6],
          7: [place_name_7,list_of_n_7],
          8: [place_name_8,list_of_n_8],
          9: [place_name_9,list_of_n_9],
          10: [place_name_10,list_of_n_10],
          11: [place_name_11,list_of_n_11],
          12: [place_name_12,list_of_n_12],
          13: [place_name_13,list_of_n_13],
          14: [place_name_14,list_of_n_14]
         }

# Fetch OSM street network from the location, only once! takes forever  
#graph = ox.graph_from_place(places[loc][0])
#area = ox.gdf_from_place(places[loc][0])

buildings = ox.footprints_from_place(places[loc][0])


try:
    #Fetch OSM street network from the location, only once! takes forever  
    graph = ox.graph_from_place(places[loc][0])
    area = ox.gdf_from_place(places[loc][0])
    
except:
    print('graph and or area not passed')
try:
    #traffic network
    edges = ox.graph_to_gdfs(graph, nodes=False)
    streets = edges[['access','geometry']].copy() # saving without this caused problems 
except:
    print('streets not passed')

# reduced columns
#cols = ['building','geometry','amenity','shop','leisure', 'sport','healthcare','healthcare:speciality','building:levels']
cols = ['building','geometry','amenity','shop','leisure', 'sport','healthcare','building:levels', 'name']

print(buildings.columns)
try:
     red_buildings = reduce_GDF(buildings,cols)
except:
    for col in cols:
        if col not in list(buildings.columns):
            buildings[col] = [np.nan]*len(buildings)
            #red_buildings = buildings
            print(col+' not in buildings')
    red_buildings = reduce_GDF(buildings,cols)

centroid_coords = getCentromerCoordiantes(buildings)

red_buildings['building_coordinates_x']=[c.x for c in centroid_coords]
red_buildings['building_coordinates_y']=[c.y for c in centroid_coords]
red_buildings['building_area']=getArea(buildings)

#add neighbourhoods

# definied center of neihbourhoods - freely choosen 
#list_of_n = [Point(6.1,51.06),Point(6.075,51.05),Point(6.145,51.035),Point(6.07,51.10)] 

neighbourhoods = [closest_n(places[loc][1],x) for x in centroid_coords]
red_buildings['neighbourhood'] = neighbourhoods

locations = exclude_small_buildings(red_buildings,min_area)

#save gdf as geojason objects 
area.to_file('Area_'+places[loc][0].split(',')[0].replace(' ','_')+'_MA_'+str(min_area).replace('.','_')+'.geojson', driver='GeoJSON')
#streets export is buggy, thus small catcher build
try:
    streets.to_file('Streets_'+places[loc][0].split(',')[0].replace(' ','_')+'_MA_'+str(min_area).replace('.','_')+'.geojson', driver='GeoJSON')
    print( 'generate: datafiles/Streets_'+places[loc][0].split(',')[0].replace(' ','_')+'_MA_'+str(min_area).replace('.','_')+'.geojson')
except:
    pass
locations.to_file('Buildings_'+places[loc][0].split(',')[0].replace(' ','_')+'_MA_'+str(min_area).replace('.','_')+'.geojson', driver='GeoJSON')
df = pd.DataFrame(locations)
df.to_csv('Buildings_'+places[loc][0].split(',')[0].replace(' ','_')+'_MA_'+str(min_area).replace('.','_')+'.csv')

print( 'generate: datafiles/Buildings_'+places[loc][0].split(',')[0].replace(' ','_')+'_MA_'+str(min_area).replace('.','_')+'.csv')
print( 'generate: datafiles/Area_'+places[loc][0].split(',')[0].replace(' ','_')+'_MA_'+str(min_area).replace('.','_')+'.geojson')
print( 'generate: datafiles/Buildings_'+places[loc][0].split(',')[0].replace(' ','_')+'_MA_'+str(min_area).replace('.','_')+'.geojson')
