import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
import argparse
import sys

def getOptions(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(description="Parses command.")
	parser.add_argument("-l", "--location", type=int, help="Choose your location (1) Heinsberg (2) Gerangel")
	parser.add_argument("-ma", "--min_area", type=int, help="default 3  (*1e-8) to reduce locations")
	parser.add_argument("-fa", "--from_adress", type=bool, help=" uses osmnx footprints_from_address with 2000 m")
	#parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode.")
	options = parser.parse_args(args)
	return options

def reduce_GDF(gdf,cols):
	#cols = ['building','geometry','amenity','shop','leisure', 'sport','healthcare','healthcare:speciality','building:levels','school_type','type','members']
	
	return gdf[cols].copy()


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


# definied center of neihbourhoods - freely choosen 
list_of_n_1 = [Point(6.1,51.06),Point(6.075,51.05),Point(6.145,51.035),Point(6.07,51.10)] 
list_of_n_2 = [Point(5.99,51.03),Point(6.05,51.01),Point(6.04,50.98),Point(5.99,50.99)]
list_of_n_3 = [Point(-2.08,52.42)]
list_of_n_4 = [Point(0.06,51.41)]
list_of_n_5 = [Point(-1.70,52.19)]
list_of_n_6 = [Point(12.57,55.76)]
list_of_n_7 = [Point(12.60,56.03)]
list_of_n_8 = [Point(14.88,55.11)]


places = {1: [place_name_1,list_of_n_1],
		  2: [place_name_2,list_of_n_2],
		  3: [place_name_3,list_of_n_3],
		  4: [place_name_4,list_of_n_4],
		  5: [place_name_5,list_of_n_5],
		  6: [place_name_6,list_of_n_6],
		  7: [place_name_7,list_of_n_7],
	      8: [place_name_8,list_of_n_8]}	


# Fetch OSM street network from the location, only once! takes forever  
#graph = ox.graph_from_place(places[loc][0])
#area = ox.gdf_from_place(places[loc][0])
if not options.from_adress:
 buildings = ox.footprints_from_place(places[loc][0])
else:
 buildings = ox.footprints_from_address(places[loc][0],2500)  

try:
	#Fetch OSM street network from the location, only once! takes forever  
	graph = ox.graph_from_place(places[loc][0])
	area = ox.gdf_from_place(places[loc][0])
	#traffic network
	edges = ox.graph_to_gdfs(graph, nodes=False)
	streets = edges[['access','geometry']].copy() # saving without this caused problems 
except:
	print('graph and or area not passed')	


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
try:
	area.to_file('datafiles/Area_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson', driver='GeoJSON')
	streets.to_file('datafiles/Streets_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson', driver='GeoJSON')
	#locations.to_file('datafiles/Buildings_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson', driver='GeoJSON')
except:
	print('streets and area is not saved')
df = pd.DataFrame(locations)
df.to_csv('datafiles/Buildings_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.csv')

print( 'generate: datafiles/Buildings_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.csv')
#print( 'generate: datafiles/Area_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson')
#print( 'generate: datafiles/Buildings_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson')
#print( 'generate: datafiles/Streets_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson')


