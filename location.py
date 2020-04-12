import numpy as np


class World(object):
    def __init__(self, number_of_locs):
        self.number_of_locs = number_of_locs
        self.locations = self.initialize_locs()
        self.neighbourhoods = self.initialize_neighbourhoods()

    def initialize_locs(self):
        locations = []
        for n in range(self.number_of_locs):
            locations.append(Location(n, (n, 0), 'dummy_loc'))

        locations[3] = Location(3, (3, 0), 'hospital')
        locations[0] = Location(0, (0, 0), 'hospital')
        return locations

    def initialize_neighbourhoods(self):
        neighbourhoods = {1: Neighbourhood(self.locations)}
        return neighbourhoods

    def assign_neighbourhood(self, locations):
        for n in self.neighbourhoods:
            for loc in self.neighbourhoods[n].locations:
                loc.neighbourhood_ID = self.neighbourhoods[n].ID


class Neighbourhood(object):
    def __init__(self, locations):
        self.locations = locations
        self.proximity_matrix = self.calculate_proximity_matrix()
        self.ID = 1  # todo

    def calculate_proximity_matrix(self):  # create distances
        matrix = np.zeros((len(list(self.locations)), len(list(self.locations))))  # create

        for i, x in enumerate(self.locations):
            ids = []
            types = []
            for k, y in enumerate(self.locations):
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


# class neighbourhood(object):
#	def __init__(self,ID):
#		self.ID = ID
#		self.locations = []
# idea proximity map for location distances

class Location(object):
    def __init__(self, ID, coordinates, location_type, people_present=set(),
                 location_factor=0.001):  # runs good with 50 people and 10 infected and 5 location, add Neighbouhood_ID
        self.ID = ID
        self.people_present = people_present
        self.location_factor = location_factor
        self.coordinates = coordinates  # () tuples
        self.location_type = location_type  # add 'hospital'
        self.neighbourhood_ID = 1
        self.distances = {}
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
        '''returns ID of the closest hospital in neighbourhood'''
        return self.closest_loc('hospital')

    def closest_loc(self, loc_type):
        ''' returns ID of the closest Location of type : loc_type, if type is identical the distance is 0'''
        try:
            ids_of_type_in_neighbourhood = self.ids_of_location_types[loc_type]
        except:
            print('location type: {} is not in the neighbourhood'.format(loc_type))
            return None
        distances_loc = {loc_id: self.distance_loc(loc_id)
                         for loc_id in self.ids_of_location_types[loc_type]}
        min_dist_index = list(distances_loc.values()).index(min(distances_loc.values()))

        return list(distances_loc.keys())[min_dist_index]

    def distance_loc(self, location_ID):
        # print(location_ID)
        return self.distances[location_ID]
# maybe without sqrt
