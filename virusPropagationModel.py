from human import *
from location import *
# from parameters import * (to be written)
from age_initialisation import RandomAge
import random
import pandas as pd


class ModeledPopulatedWorld(object):
    ## define initial variables
    def __init__(self, number_of_locs, number_of_people, initial_infections):
        self.number_of_locs = number_of_locs
        self.number_of_people = number_of_people
        self.initial_infections = initial_infections
        self.world = World(self.number_of_locs)
        self.locations = self.world.locations
        self.people = self.initialize_people(self.number_of_people)
        self.infect(self.initial_infections)

    # def init_world(self, number_of_locs):
    #	self.world = location.World(number_of_locs)

    # def initialize_locs(self, number_of_locs): # todo
    #	locs = set()
    #	for n in range(number_of_locs):
    #		locs.add(Location(n, (0,0), 'dummy_loc'))
    #	return locs

    def initialize_people(self, number_of_people):  # idee martin: skalenfeiheit
        people = set()
        for n in range(number_of_people):
            age = RandomAge()
            schedule = self.create_schedule(age, self.locations)
            people.add(Human(n, age, schedule, schedule['locs'][0]))
        return people

    def create_schedule(self, age, locations):
        if age > 3 and age < 70:  # schedule has to depend on age, this is only preliminary
            num_locs = 5
        else:
            num_locs = 3
        my_locs = random.sample(locations,
                                num_locs)  # draw random locations (preliminary) (random.sample() draws exclusively)
        my_times = random.sample(range(24), num_locs)
        my_times.sort()
        sched = {'times': my_times, 'locs': my_locs}
        return sched

    def infect(self, number):
        to_infect = random.sample(self.people, number)  # randomly choose who to infect
        for p in to_infect:
            p.status = 'I'


class Simulation(object):
    def __init__(self, modeled_populated_world, time_steps):
        self.modeled_populated_world = modeled_populated_world
        self.time = 0
        self.timecourse = []  # [{'h_ID': self.ID, 'loc': self.loc.ID, 'status': self.status, 'time': time}]
        self.time_steps = time_steps
        self.simulation_timecourse = self.run_simulation()

    def store_state(self, person):
        stat = person.get_status()
        stat['time'] = self.time  #
        self.timecourse.append(stat)

    def run_simulation(self):
        for t in range(self.time_steps):
            self.time += 1
            for p in self.modeled_populated_world.people:  #
                p.update_status(self.time)
            for p in self.modeled_populated_world.people:  # don't call if hospitalized
                p.move(self.time)
                self.store_state(p)
        return pd.DataFrame(self.timecourse)

    def get_status_trajectory(self, given_status='all'):
        possible_statuses = ['all'] + list(set([stat for stat in self.modeled_populated_world.people.status]))
        print(possible_statuses)
        assert given_status in possible_statuses, 'specified status does not exist in the population'
        if given_status == 'all':
            possible_statuses.remove('all')
            statuses = possible_statuses
        else:
            statuses = given_status
        for status in statuses:
            status_trajecory = [(t, len(self[(self['time'] == t) & (self['status'] == 'S')])) for t in
                            self['time'].unique()]

    def plot_timecourse(self):
        print("plotting timecourse")
