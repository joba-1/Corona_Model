import numpy as np
import random
import pandas as pd
import ctypes
from random import choice as choosing_one


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
