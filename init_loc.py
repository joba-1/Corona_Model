import osmnx as ox
import geopandas as gpd
import pandas as pd 


#def initialize_locs(self, loc_file):
#
##	"""
#	initialize locations  from geo data. imported with osmnx from open streetmap


#	"""
#		locations = []
#		for n in range(self.number_of_locs):
#			locations.append(Location(n, (n,0), 'dummy_loc'))
#
#		locations[3] = Location(3, (3,0), 'hospital')
#		locations[0] = Location(0, (0,0), 'hospital')						
#		return locations

if __name__ == "__main__":

	#r1 = gpd.read_file('datafiles/Buildings_Heinsberg.geojson')
	df_buildings = pd.read_csv('datafiles/Buildings_Heinsberg.csv')
	#b_d = r1.to_dict('index')
	#print(r1.head())
	#Id coordinates type
	#Location()
	building_type = 'Residence'
	test_dict ={}
	#df_buildings = pd.DataFrame(r1)

	#for x in df_buildings.index:
	#	row = df_buildings.loc[x]
		
	#	if row['amenity'] != None:
	#		building_type = row['amenity']

	#	test_dict[x] = [(row['building_coordinates_x'],row['building_coordinates_y']),building_type]
	#print(df_buildings.head())
	
	#
	#df_buildings = pd.read_csv(building_filename)	 	
		#Location(x, (row['building_coordinates_x'],row['building_coordinates_y']),building_type )

	print(df_buildings['neighbourhood'].unique())
	df_buildings['building_coordinates_x']
		