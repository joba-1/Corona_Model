import numpy as np
import random
import pandas as pd
import ctypes
from random import choice as choosing_one
from gerda.core.neighbourhood import Neighbourhood
from gerda.core.location import Location


class World(object):
    def __init__(self, geofile_name='input_data/geo/Buildings_Gangelt_MA_3.csv', from_file=True, number_of_locs=100):
        self.from_file = from_file
        self.geofile_name = geofile_name
        self.number_of_locs = number_of_locs
        self.df_buildings = pd.read_csv(self.geofile_name)

        if self.from_file:
            self.locations = self.initialize_locs_from_file()
        else:
            self.locations = self.initialize_locs_random()
        self.neighbourhoods = self.initialize_neighbourhoods()
        self.calculate_proximity_matrix()

        for l in self.locations:
            self.locations[l].world_ref = id(self)
            self.locations[l].special_locations['morgue'] = self.locations[l].get_other_loc_by_id(
                self.locations[l].next_location_of_type('morgue'))
            self.locations[l].special_locations['hospital'] = self.locations[l].get_other_loc_by_id(
                self.locations[l].next_location_of_type('hospital'))
        self.loc_class_dic = self.assign_location_classifier()

    def initialize_locs_random(self):  # orginal
        locations = {}
        for n in range(self.number_of_locs):
            loc_type = random.sample(['home', 'work', 'public', 'school'], 1)[0]
            locations[n] = Location(n, (n, 0), loc_type, 1, 1e-8)

        locations[3] = Location(3, (3, 0), 'hospital', 1, 1e-8)
        locations[0] = Location(0, (0, 0), 'morgue', 1, 1e-8)
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

        loc_class_dic['excluded_buildings'] = ['garage',
                                               'roof',
                                               'shed',
                                               'bungalow',
                                               'silo', ]
        loc_class_dic['hospital'] = ['hospital']
        loc_class_dic['morgue'] = ['morgue']
        loc_class_dic['mixing_loc'] = ['mixing_loc']

        cols = ['amenity', 'shop', 'leisure', 'sport', 'building']
        for col in cols:
            try:
                list(self.df_buildings[col].unique())
            except:
                self.df_buildings[col] = [np.nan]*len(self.df_buildings)

        loc_class_dic['work'] = ['civic', 'commercial', 'company', 'construction', 'cowshed', 'farm', 'farm_auxiliary', 'fire_station', 'greenhouse', 'industrial',
                                 'manufacture', 'office', 'retail', 'service', 'shed', 'stable', 'transformer_tower', 'warehouse']\
            + list(self.df_buildings['amenity'].unique())\
            + list(self.df_buildings['shop'].unique())

        loc_class_dic['public'] = ['bank', 'cabin', 'cafe', 'car_wash', 'chapel', 'church', 'doctors', 'fast_food', 'grocery_store', 'hotel',
                                   'hut', 'parish_hall', 'place_of_worship', 'police', 'pub', 'public', 'restaurant', 'ruins', 'service', 'shelter',
                                   'social_facility', 'sports_centre', 'sports_hall', 'supermarket', 'temple', 'toilets', 'townhall', 'train_station']\
            + list(self.df_buildings['leisure'].unique())\
            + list(self.df_buildings['sport'].unique())

        loc_class_dic['school'] = ['school', 'university', 'kindergarten']
        # Cleaning the list public place of nan
        loc_class_dic['public'] = [x for x in loc_class_dic['public'] if ~pd.isnull(x)]
        # Removing values from workplace_list that are in work place and in another list
        for x in loc_class_dic['hospital'] + [np.nan] + loc_class_dic['public'] + loc_class_dic['school']:
            while x in loc_class_dic['work']:
                loc_class_dic['work'].remove(x)

        return loc_class_dic

    def initialize_locs_from_file(self):
        ''' Initialize locations from file. Right now .csv dataframe made from read_geodata.py
        : return: dictionary with loaction objects: locations[int(ID)]: Loaction_Object

        '''
        locations = {}

        loc_class_dic = self.assign_location_classifier()
        # Columns important to classify building type and therefore which location type it is
        # col_names = ['building', 'amenity', 'shop', 'leisure', 'sport', 'healthcare']
        # start of boolcheck to see if at least one hospital in dataframe
        hospital_bool = False
        morgue_bool = False
        mix_bool = False
        # healthcare, work, public_place, school = self.location_classifier(self.df_buildings)

        cols = ['building', 'amenity', 'shop', 'leisure', 'sport', 'healthcare']
        col_names = [x for x in cols if x in self.df_buildings.columns]

        for i, x in enumerate(self.df_buildings.index):
            row = self.df_buildings.loc[x]

            building_type = self.assign_building_type(
                row[col_names].dropna().unique(), loc_class_dic)
            # check if hospital will be true if at least one in dataframe
            if building_type == 'hospital':
                hospital_bool = True
            elif building_type == 'morgue':
                morgue_bool = True

            # create location in dictionary, except excluded buildings
            if building_type != 'excluded_buildings':
                locations[i] = Location(x, (row['building_coordinates_x'], row['building_coordinates_y']),
                                        building_type,
                                        row['neighbourhood'],
                                        row['building_area'],)
        # if no hospital in dataframe, one is created in upper right corner, else model has problems #FIXME Future
        # if no morgue in dataframe, one is created in low left corner, else model has problems #FIXME Future
        distance = 0.00
        if not hospital_bool:
            locations.update({len(self.df_buildings)+1: Location(len(self.df_buildings)+1,
                                                                 (max(self.df_buildings['building_coordinates_x'])+distance,
                                                                  max(self.df_buildings['building_coordinates_y'])+distance),
                                                                 'hospital',
                                                                 'no',
                                                                 9.321282e-08,)})
        if not morgue_bool:
            locations.update({len(self.df_buildings)+2: Location(len(self.df_buildings)+2,
                                                                 (min(self.df_buildings['building_coordinates_x'])-distance,
                                                                  min(self.df_buildings['building_coordinates_y'])-distance),
                                                                 'morgue',
                                                                 'no',
                                                                 9.321282e-06,)})
        if not mix_bool:
            locations.update({len(self.df_buildings)+3: Location(len(self.df_buildings)+3,
                                                                 (sum(self.df_buildings['building_coordinates_x'])/len(self.df_buildings['building_coordinates_x']),
                                                                  sum(self.df_buildings['building_coordinates_y'])/len(self.df_buildings['building_coordinates_y'])),
                                                                 'mixing_loc',
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

    def calculate_proximity_matrix(self):  # create distances
        matrix = np.zeros((len(list(self.locations)), len(list(self.locations))))  # create
        self.proxy_matrix_row_indices = []
        self.proxy_matrix_col_indices = []
        locEnumeration = list(enumerate(self.locations.values()))
        ids = []
        types = []
        for row in locEnumeration:
            i = row[0]
            x = row[1]
            self.proxy_matrix_row_indices.append(x.ID)
            if x.location_type != 'home':
                self.proxy_matrix_col_indices.append(x.ID)
                ids.append(x.ID)
                types.append(x.location_type)
            for col in locEnumeration:
                k = col[0]
                y = col[1]
                if y.location_type != 'home':
                    matrix[i, k] = np.sqrt((x.coordinates[0] - y.coordinates[0])
                                           ** 2 + (x.coordinates[1] - y.coordinates[1]) ** 2)

        self.proximity_matrix = matrix

        location_types_in_world = dict(zip(ids, types))
        ids_of_location_types = {}
        for t in list(set(list(location_types_in_world.values()))):
            l = [x for x in location_types_in_world if location_types_in_world[x] == t]
            ids_of_location_types[t] = l

        self.ids_of_location_types = ids_of_location_types
