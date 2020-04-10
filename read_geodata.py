import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def reduce_GDF(gdf,cols):
	cols = ['building','geometry','amenity','healthcare','healthcare:speciality','building:levels','school_type','type','members']
	return gdf[cols].copy()


def getCentromerCoordiantes(buildings):
	centroid_coords = [x.centroid for x  in buildings['geometry']]
	#centroid_coords_y = [x.centroid.y for x  in buildings['geometry']]
	return centroid_coords

def getArea(buildings):
	return [x.area for x  in buildings['geometry']]

def closest_n(list_of_n,point):
    '''return index of nearest neighbourhood center'''
    distances = [point.distance(x) for x in list_of_n]        
    return distances.index(min(distances)) 	
	


if __name__ == "__main__":

	# Specify the name that is used to seach for the data
	place_name_1 = "Heinsberg, Nordrhein-Westfalen, Germany"
	place_name_2 = "Gangelt, Kreis Heinsberg, Nordrhein-Westfalen, Germany"
	
	# definied center of neihbourhoods - freely choosen 
	list_of_n_1 = [Point(6.1,51.06),Point(6.075,51.05),Point(6.145,51.035),Point(6.07,51.10)] 
	list_of_n_2 = [Point(5.99,51.03),Point(6.05,51.01),Point(6.04,50.098),Point(5.99,50.99)] 

	places = {1: [place_name_1,list_of_n_1], 2: [place_name_2,list_of_n_2]}

	

	# Fetch OSM street network from the location, only once! takes forever  
	graph = ox.graph_from_place(places[1][0])
	area = ox.gdf_from_place(places[1][0])
	buildings = ox.footprints_from_place(places[1][0])

	# reduced columns
	cols = ['building','geometry','amenity','healthcare','healthcare:speciality','building:levels','school_type','rooms','type','members']

	red_buildings = reduce_GDF(buildings,cols)

	centroid_coords = getCentromerCoordiantes(buildings)

	red_buildings['building_coordinates_x']=[c.x for c in centroid_coords]
	red_buildings['building_coordinates_y']=[c.y for c in centroid_coords]
	red_buildings['building_area']=getArea(buildings)

	
	#add neighbourhoods

	# definied center of neihbourhoods - freely choosen 
	list_of_n = [Point(6.1,51.06),Point(6.075,51.05),Point(6.145,51.035),Point(6.07,51.10)] 

	neighbourhoods = [closest_n(places[1][0],x) for x in centroid_coords]
	red_buildings['neighbourhood'] = neighbourhoods

	#save gdf as geojason objects 
	area.to_file('datafiles/Area_'+place_name.split(',')[0]+'.geojson', driver='GeoJSON')


	red_buildings.to_file('datafiles/Buildings_'+place_name.split(',')[0]+'.geojson', driver='GeoJSON')
	df = pd.DataFrame(red_buildings)
	df.to_csv('datafiles/Buildings_'+place_name.split(',')[0]+'.csv')


