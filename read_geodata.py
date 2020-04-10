import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import argparse
import sys

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-l", "--location", type=int, help="Choose your location (1) Heinsberg (2) Gerangel")
    parser.add_argument("-ma", "--min_area", type=int, help="default 3  (*1e-8) to reduce locations")
    #parser.add_argument("-n", "--number", type=int, help="A number.")
    #parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode.")
    options = parser.parse_args(args)
    return options

def reduce_GDF(gdf,cols):
	cols = ['building','geometry','amenity','healthcare','healthcare:speciality','building:levels','school_type','type','members']
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

# definied center of neihbourhoods - freely choosen 
list_of_n_1 = [Point(6.1,51.06),Point(6.075,51.05),Point(6.145,51.035),Point(6.07,51.10)] 
list_of_n_2 = [Point(5.99,51.03),Point(6.05,51.01),Point(6.04,50.098),Point(5.99,50.99)] 

places = {1: [place_name_1,list_of_n_1], 2: [place_name_2,list_of_n_2]}



# Fetch OSM street network from the location, only once! takes forever  
graph = ox.graph_from_place(places[loc][0])
area = ox.gdf_from_place(places[loc][0])
buildings = ox.footprints_from_place(places[loc][0])

# reduced columns
cols = ['building','geometry','amenity','healthcare','healthcare:speciality','building:levels']

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
area.to_file('datafiles/Area_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson', driver='GeoJSON')


locations.to_file('datafiles/Buildings_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson', driver='GeoJSON')
df = pd.DataFrame(locations)
df.to_csv('datafiles/Buildings_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.csv')

print( 'generate: datafiles/Buildings_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.csv')
print( 'generate: datafiles/Area_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson')
print( 'generate: datafiles/Buildings_'+places[loc][0].split(',')[0]+'_MA_'+str(min_area)+'.geojson')


