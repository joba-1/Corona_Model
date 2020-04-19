import numpy as np
import random
import pandas as pd


class World(object):
    def __init__(self, geofile_name='datafiles/Buildings_Gangelt_MA_3.csv', from_file=True, number_of_locs=100):
        self.from_file = from_file
        self.geofile_name = geofile_name
        self.number_of_locs = number_of_locs
        self.df_buildings = pd.read_csv(self.geofile_name)

        if self.from_file:
            self.locations = self.initialize_locs_from_file()
        else:
            self.locations = self.initialize_locs_random()
        self.neighbourhoods = self.initialize_neighbourhoods()

    def initialize_locs_random(self):  # orginal
        locations = {}
        for n in range(self.number_of_locs):
            loc_type = random.sample(['home','work','public','school'],1)[0]
            locations[n]=Location(n, (n,0), loc_type, 1, 1e-8)

        locations[3] = Location(3, (3, 0), 'hospital', 1, 1e-8)
        locations[0] = Location(0, (0, 0), 'hospital', 1, 1e-8)
        return locations

    def assign_location_classifier(self):
        '''Build reference lists for assign_building_type() from given dataframe.
        Should be produced by read_geodata.py.
        Possible classes and therefore dictionary keys are:
        'excluded_buildings' = buildings not included because they do not fit any class
        'hospital' = hospitals
        'work' = anything a person can work at
        'public' = right now religous and sport buildings #FIXME-Discussion: restaurantes, bars, cafe?
        'school' = places with a lot of young people
        Sorting idea as of right now everything is work place if not in any other list
        : return: location class dictionary loc_class_dic['school'] = ['school','university','kindergarten']

        '''
        loc_class_dic = {}

        loc_class_dic['excluded_buildings'] = ['garage', 'roof', 'shed', 'bungalow', 'barn', 'silo']
        loc_class_dic['hospital'] = ['hospital']
        loc_class_dic['cemetery'] = ['cemetery']
        
        loc_class_dic['work'] = ['industrial','greenhouse','cowshed','shed','commercial','warehouse','office','farm']\
                                    +list(self.df_buildings['amenity'].unique())\
                                    +list(self.df_buildings['shop'].unique())

        #What is a public place or just work place e.g. restaurante, cafe...
        
        loc_class_dic['public'] = ['public','chapel','church']\
                                        +list(self.df_buildings['leisure'].unique())\
                                        +list(self.df_buildings['sport'].unique())

        
        loc_class_dic['school'] = ['school','university','kindergarten'] 
        #Cleaning the list public place of nan
        loc_class_dic['public'] = [x for x in loc_class_dic['public'] if ~pd.isnull(x)]
        #Removing values from workplace_list that are in work place and in another list
        for x in loc_class_dic['hospital'] + [np.nan] + loc_class_dic['public'] + loc_class_dic['school']:
            while x in loc_class_dic['work']: loc_class_dic['work'].remove(x)  

        return loc_class_dic

    def initialize_locs_from_file(self):
        ''' Initialize locations from file. Right now .csv dataframe made from read_geodata.py
        : return: dictionary with loaction objects: locations[int(ID)]: Loaction_Object

        '''
        locations = {}

        loc_class_dic = self.assign_location_classifier()
        # Columns important to classify building type and therefore which location type it is
        col_names = ['building', 'amenity', 'shop', 'leisure', 'sport', 'healthcare']
        # start of boolcheck to see if at least one hospital in dataframe
        hospital_bool = False
        cemetery_bool = False
        #healthcare, work, public_place, school = self.location_classifier(self.df_buildings)

        col_names = ['building', 'amenity', 'shop', 'leisure', 'sport', 'healthcare']

        for i, x in enumerate(self.df_buildings.index):
            row = self.df_buildings.loc[x]

            building_type = self.assign_building_type(
                row[col_names].dropna().unique(), loc_class_dic)
            # check if hospital will be true if at least one in dataframe
            if building_type == 'hospital':
                hospital_bool = True
            elif building_type == 'cemetery':
                cemetery_bool = True

            #create location in dictionary, except excluded buildings
            if building_type != 'excluded_buildings':
                locations[i] = Location(x, (row['building_coordinates_x'], row['building_coordinates_y']),
                                        building_type,
                                        row['neighbourhood'],
                                        row['building_area'],)
        # if no hospital in dataframe, one is created in upper right corner, else model has problems #FIXME Future
        # if no cemetery in dataframe, one is created in low left corner, else model has problems #FIXME Future
        if not hospital_bool:
            distance = 0.00
            locations.update({len(self.df_buildings)+1: Location(len(self.df_buildings)+1,
                                                                 (max(self.df_buildings['building_coordinates_x'])+distance,
                                                                  max(self.df_buildings['building_coordinates_y'])+distance),
                                                                 'hospital',
                                                                 'no',
                                                                 9.321282e-08,)})
        if not cemetery_bool:
            locations.update({len(self.df_buildings)+2: Location(len(self.df_buildings)+2,
                                                                 (min(self.df_buildings['building_coordinates_x'])-distance,
                                                                  min(self.df_buildings['building_coordinates_y'])-distance),
                                                                 'cemetery',
                                                                 'no',
                                                                 9.321282e-06,)})

        return locations

    def assign_building_type(self, building_lst: list, loc_class_dic: dict):
        '''set building type according to value in building_lst and where it matches with reference lists

            : return: string with building type
        '''
        # auto assign is home
        building_type = 'home'
        # if any entry of building_lst matches any location class entry: it is assigned to that class
        for key in loc_class_dic:
            if any(elem in loc_class_dic[key] for elem in building_lst):
                building_type = key

        return building_type

    def initialize_neighbourhoods(self):
        if self.from_file:
            neighbourhoods = {}
            for loc in self.locations.values():
                neighbourhood_id = loc.neighbourhood_ID
                if neighbourhood_id in neighbourhoods.keys():
                    neighbourhoods[neighbourhood_id][loc.ID] = loc
                else:
                    neighbourhoods[neighbourhood_id] = {
                        loc.ID: loc}  # 1 schould be neighbourhood_id
        else:
            neighbourhoods = {1: Neighbourhood(self.locations)}
        return neighbourhoods


class Neighbourhood(object):
    def __init__(self, locations):
        self.locations = locations
        self.proximity_matrix = self.calculate_proximity_matrix()
        self.ID = 1  # todo

    def calculate_proximity_matrix(self):  # create distances
        matrix = np.zeros((len(list(self.locations)), len(list(self.locations))))  # create

        for i, x in enumerate(self.locations.values()):
            ids = []
            types = []
            for k, y in enumerate(self.locations.values()):
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
        infected = sum([p.get_infectivity() for p in self.people_present if p.status == 'I'])
        # / float(len(self.people_present))  # get fraction of infected individuals in location
        risk = function2specify(infected, self.location_factor)
        return risk

    def infection_interaction(self, n=1):  # this needs improvement, it's simple and preliminary
        for i in range(n):
            interaction_partner = np.random.choice(list(self.people_present))
            if interaction_partner.status == 'I':
                return(interaction_partner)

    def next_hospital(self):
        '''returns sorted list of IDs of the closest hospital in neighbourhood'''
        return self.closest_loc('hospital')[0]

    def closest_loc(self, loc_type):
        ''' returns sorted list ID of the closest Location of type : loc_type, if type is identical the distance is 0'''
        try:
            ids_of_type_in_neighbourhood = self.ids_of_location_types[loc_type]
        except:
            #print('location type: {} is not in the neighbourhood'.format(loc_type))
            return None
        distances_loc = {loc_id: self.distance_loc(loc_id)
                         for loc_id in self.ids_of_location_types[loc_type]}
        min_dist_index = list(distances_loc.values()).index(min(distances_loc.values()))
        sorted_items = sorted((value, key) for (key, value) in distances_loc.items())
        sorted_ids = [i for (v, i) in sorted_items]

        return sorted_ids

    def distance_loc(self, location_ID):
        # print(location_ID)
        return self.distances[location_ID]


def function2specify(x1, x2):
    return(x1*x2)
