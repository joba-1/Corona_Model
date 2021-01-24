import numpy as np
import random
import pandas as pd
import ctypes
from random import choice as choosing_one


class Location(object):
    def __init__(self, ID, coordinates, location_type, neighbourhood, area,
                 location_factor=1):  # runs good with 50 people and 10 infected and 5 location, add Neighbouhood_ID
        self.ID = ID
        self.people_present = set()
        self.location_factor = location_factor
        self.coordinates = coordinates  # () tuples
        self.location_type = location_type  # add 'hospital'
        self.neighbourhood_ID = neighbourhood
        self.distances = {}
        self.area = area
        self.ids_of_location_types = {}  # loc_id : distance
        self.world_ref = None
        self.special_locations = {}

    def get_location_id(self):
        return self.ID

    def get_location_type(self):
        return self.location_type

    def enter(self, person):
        self.people_present.add(person)

    def leave(self, person):
        self.people_present.remove(person)

    def next_location_of_type(self, type):
        '''returns sorted list of IDs of the closest hospital in neighbourhood'''
        if self.closest_loc(type):
            return self.closest_loc(type)[0]
        else:
            return self.closest_loc_world(type)[0]

    def closest_loc(self, loc_type):
        ''' returns sorted list ID of the closest Location of type : loc_type, if type is identical the distance is 0'''
        try:
            ids_of_type_in_neighbourhood = self.ids_of_location_types[loc_type]
        except:
            # print('location type: {} is not in the neighbourhood'.format(loc_type))
            return None
        distances_loc = {loc_id: self.distance_loc(loc_id)
                         for loc_id in self.ids_of_location_types[loc_type]}
        min_dist_index = list(distances_loc.values()).index(min(distances_loc.values()))
        sorted_items = sorted((value, key) for (key, value) in distances_loc.items())
        sorted_ids = [i for (v, i) in sorted_items]
        return sorted_ids

    def closest_loc_world(self, loc_type, return_sorted_list=False):
        try:
            ids_of_type_in_world = ctypes.cast(
                self.world_ref, ctypes.py_object).value.ids_of_location_types[loc_type]
        except:
            return None
        if len(ids_of_type_in_world) > 1:
            row_ind = ctypes.cast(
                self.world_ref, ctypes.py_object).value.proxy_matrix_row_indices.index(self.ID)
            col_ind = [ctypes.cast(self.world_ref, ctypes.py_object).value.proxy_matrix_col_indices.index(
                l) for l in ids_of_type_in_world if l != self.ID]
            if len(col_ind) > 0:
                respective_other_matrix_entries = list(ctypes.cast(
                    self.world_ref, ctypes.py_object).value.proximity_matrix[row_ind, col_ind])
                if respective_other_matrix_entries:
                    if not return_sorted_list:
                        index_in_row_subset = int(respective_other_matrix_entries[respective_other_matrix_entries.index(
                            min(respective_other_matrix_entries))])
                        ID_of_closest = ctypes.cast(
                            self.world_ref, ctypes.py_object).value.proxy_matrix_col_indices[col_ind[index_in_row_subset]]
                        return([ID_of_closest])
                    else:
                        indices_in_row_subset = list(np.argsort(respective_other_matrix_entries))
                        IDs_sorted_by_dist = [ctypes.cast(
                            self.world_ref, ctypes.py_object).value.proxy_matrix_col_indices[col_ind[index_in_row_subset]] for i in indices_in_row_subset]
                        return(IDs_sorted_by_dist)
                else:
                    return([self])
        elif len(ids_of_type_in_world) == 1:
            return(ids_of_type_in_world)
        else:
            return([self])

    def get_other_loc_by_id(self, id):
        try:
            return([ctypes.cast(self.world_ref, ctypes.py_object).value.locations[id]])
        except:
            return []

    def distance_loc(self, location_ID):
        # print(location_ID)
        return self.distances[location_ID]

    def determine_interacting_pairs(self, mu=1, interaction_matrix=True):
        ## create dict of human ID's and interaction modifiers, currently present in location#
        h_dict = {p.ID: p.interaction_modifier for p in list(self.people_present)}
        n = len(h_dict)

        human_ids = list(h_dict.keys())
        interaction_modifier = list(h_dict.values())

        if interaction_matrix:
            # create vector of interaction modifier
            v = np.array([interaction_modifier])
            # set interaction probability threshold
            interaction_probability = mu / (n - 1)
            # Create triangle matrix from v  on top of diagonal (rest zeros)
            M = v.transpose().dot(v)
            C = np.triu(M) - np.eye(n) * v ** 2
            # generate array of random numbers with dimension n times n
            P = np.random.random((n, n))
            # build logical array, showing where drawn probabilities are smaller than mu
            I = P < C * interaction_probability
            # build list of interacting-ids (as tuples)
            cp1, cp2 = np.where(I)
            pairs = list(zip([human_ids[i]
                              for i in cp1], [human_ids[i] for i in cp2]))
        else:
            pairs = [
                (h_id, choosing_one(list(set(human_ids)-{h_id}))) for h_id in human_ids]
        return(pairs)

    def let_agents_interact(self, mu=1, interaction_matrix=True):
        if self.location_type != 'morgue':
            human_objects_present = {p.ID: p for p in list(self.people_present)}
            if len(list(human_objects_present.keys())) > 1:
                pairs = self.determine_interacting_pairs(
                    mu=mu*self.location_factor, interaction_matrix=interaction_matrix)
                for p in pairs:
                    human_objects_present[p[0]].contact_persons.append(str(p[1]))
                    human_objects_present[p[1]].contact_persons.append(str(p[0]))
                    human_objects_present[p[0]].interact_with(human_objects_present[p[1]])
                    human_objects_present[p[1]].interact_with(human_objects_present[p[0]])
