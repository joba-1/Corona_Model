import numpy as np
import random
import pandas as pd

class World(object):
    def __init__(self, geofile_name='datafiles/Buildings_Gangelt_MA_3.csv', from_file=False, number_of_locs=100):
        self.from_file = from_file
        self.geofile_name = geofile_name
        self.number_of_locs = number_of_locs

        if self.from_file:
            self.locations = self.initialize_locs_from_file()
        else:    
            self.locations = self.initialize_locs_random()
        self.neighbourhoods = self.initialize_neighbourhoods()    

    def initialize_locs_random(self):# orginal
        locations = {}
        for n in range(self.number_of_locs):
            loc_type = random.sample(['home','work','public_place','school'],1)[0]
            locations[n]=Location(n, (n,0), loc_type, 1, 1e-8)

        locations[3] = Location(3, (3, 0), 'hospital', 1, 1e-8)
        locations[0] = Location(0, (0, 0), 'hospital', 1, 1e-8)
        return locations

    def initialize_locs_from_file(self):
        locations = {}
        self.df_buildings = pd.read_csv(self.geofile_name)

        for i,x in enumerate(self.df_buildings.index):
            row = self.df_buildings.loc[x]
            try:
                if np.isnan(row['amenity']):
                    building_type = 'home'
                else:
                    building_type = random.sample(['work','school','public_place'],1)[0]#row['amenity']
            except:
                building_type = random.sample(['work','school','public_place'],1)[0]#row['amenity']

            #building_type = location_settings(row[col_names],work_place, healthcare)  
            locations[i] = Location(x, (row['building_coordinates_x'],row['building_coordinates_y']),
                                building_type,
                                row['neighbourhood'],
                                row['building_area'],)
            #locations[0] = Location(0, (0, 0), 'public_place', 1, 1e-8)
            #locations[1] = Location(1, (0, 2), 'school', 1, 1e-8)
        return locations

    def location_settings(building_lst, workplace:list, healthcare:list):
        building_type = 'home'
        if any(elem in healthcare for elem in building_lst):
            building_type = 'Healthcare'
        elif any(elem in workplace for elem in building_lst):
            building_type = 'Economy'
        return building_type        

    def initialize_neighbourhoods(self):
        if self.from_file:
            neighbourhoods = {}
            for loc in self.locations.values():
                neighbourhood_id = loc.neighbourhood_ID
                if neighbourhood_id in neighbourhoods.keys():
                    neighbourhoods[neighbourhood_id][loc.ID] = loc
                else:
                    neighbourhoods[neighbourhood_id] = {loc.ID: loc}   ## 1 schould be neighbourhood_id
        else:
            neighbourhoods = {1: Neighbourhood(self.locations)}
        return neighbourhoods


class Neighbourhood(object):
    def __init__(self, locations):
        self.locations = locations
        self.proximity_matrix = self.calculate_proximity_matrix()
        self.ID = 1  # todo

    def calculate_proximity_matrix(self): #create distances
        matrix = np.zeros((len(list(self.locations)),len(list(self.locations)))) # create  
        
        for i,x in enumerate(self.locations.values()):          
            ids = []
            types = []
            for k,y in enumerate(self.locations.values()):
                if y.location_type != 'home':
                    ids.append(y.ID)
                    types.append(y.location_type)
                    matrix[i, k] = np.sqrt(
                        (x.coordinates[0] - y.coordinates[0]) ** 2 + (x.coordinates[1] - y.coordinates[1]) ** 2)
            x.distances = dict(zip(ids, list(matrix[i, :])))
            location_types_in_neighbourhood = dict(zip(ids, types))
            ids_of_location_types = {}

            for t in list(set(list(location_types_in_neighbourhood.values()))):
                l = [x for x in location_types_in_neighbourhood if location_types_in_neighbourhood[x] == t]
                ids_of_location_types[t] = l
            x.ids_of_location_types = ids_of_location_types

        return matrix

class Location(object):
    def __init__(self, ID, coordinates, location_type, neighbourhood, area,
                 location_factor=0.002):  # runs good with 50 people and 10 infected and 5 location, add Neighbouhood_ID
        self.ID = ID
        self.people_present = set()
        self.location_factor = location_factor
        self.coordinates = coordinates  # () tuples
        self.location_type = location_type  # add 'hospital'
        self.neighbourhood_ID = neighbourhood
        self.distances = {}
        self.area = area
        self.ids_of_location_types = {}  # loc_id : distance

    def get_location_id(self):
        return self.ID

    def get_location_type(self):
        return self.location_type

    def enter(self, person):
        self.people_present.add(person)

    def leave(self, person):
        self.people_present.remove(person)

    def infection_risk(self):  # this needs improvement, it's simple and preliminary
        infected = sum([p.get_infectivity() for p in self.people_present if
                        p.status == 'I'])  # /float(len(self.people_present)) # get fraction of infected individuals in location
        risk = self.location_factor * infected
        return risk

    def next_hospital(self):
        '''returns sorted list of IDs of the closest hospital in neighbourhood'''
        return self.closest_loc('hospital')[0]
        
    def closest_loc(self, loc_type):
        ''' returns sorted list ID of the closest Location of type : loc_type, if type is identical the distance is 0'''
        try:
            ids_of_type_in_neighbourhood = self.ids_of_location_types[loc_type]
        except:
            print('location type: {} is not in the neighbourhood'.format(loc_type))
            return None
        distances_loc = {loc_id: self.distance_loc(loc_id) for loc_id in self.ids_of_location_types[loc_type]}
        min_dist_index = list(distances_loc.values()).index(min(distances_loc.values()))
        sorted_items = sorted((value, key) for (key,value) in distances_loc.items())
        sorted_ids = [i for (v,i) in sorted_items]
        
        return sorted_ids

    def distance_loc(self, location_ID):
        # print(location_ID)
        return self.distances[location_ID]
