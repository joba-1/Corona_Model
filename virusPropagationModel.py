from human import *
from location import *
#from parameters import * (to be written)
## import random age draw function
from age_initialisation import random_age
## import required libraries
import numpy.random as npr ## numpy.random for generating random numbers
# from parameters import * (to be written)
from age_initialisation import RandomAge
import random
import pandas as pd
import matplotlib.pyplot as plt


class ModeledPopulatedWorld(object):
    def __init__(self, number_of_locs, number_of_people, initial_infections):
        self.number_of_locs = number_of_locs
        self.number_of_people = number_of_people
        self.initial_infections = initial_infections
        self.world = World(self.number_of_locs)
        self.locations = self.world.locations
        self.people = self.initialize_people(self.number_of_people)
        self.infect(self.initial_infections)

	def initialize_people(self, number_of_people): # idee martin: skalenfeiheit
		people = set()
		for n in range(number_of_people):
			age = random_age()
			schedule = self.create_schedule(age, self.locations)
			people.add(Human(n, age, schedule, schedule['locs'][0]))
		return people

    def create_schedule(self, age, locations):
        if 3 < age < 70:  # schedule has to depend on age, this is only preliminary
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
        self.statuses_in_timecourse = self.get_statuses_in_timecourse()

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

    def get_statuses_in_timecourse(self):
        return list(set(self.simulation_timecourse['status']))

    def get_status_trajecories(self, specific_statuses=None):
        """
        :param specific_statuses: List. Optional arg for getting only a subset  of statuses
        :return: DataFrame. The time courses for the specified statuses
        """
        if specific_statuses is None:
            statuses = self.get_statuses_in_timecourse()
        else:
            assert set(specific_statuses) <= set(self.statuses_in_timecourse), \
                'specified statuses ('+str(set(specific_statuses))+') dont match those in  in the population (' + \
                str(set(self.statuses_in_timecourse)) + ')'
            statuses = specific_statuses

        status_trajecories = {}
        for status in statuses:
            status_trajecories[status] = [(t, len(self.simulation_timecourse[(self.simulation_timecourse['time'] == t)
                                                                             & (self.simulation_timecourse[
                                                                                    'status'] == status)]))
                                          for t in self.simulation_timecourse['time'].unique()]
            status_trajecories[status] = pd.DataFrame(status_trajecories[status], columns=['time', status])
        return status_trajecories

    def plot_status_timecourse(self, specific_statuses=None, save_figure=False):
        """
        plots the timecourse for selected statuses
        :param save_figure:  Bool. Flag for saving the figure as an image
        :param specific_statuses:   List. Optional arg for getting only a
        subset  of statuses. if not speficied, will plot all available statuses
        :return:
        """
        labels = {
            'S': 'Susceptible',
            'R': 'Recovered',
            'I':  'Infected',
            'D':  'Dead'
        }

        trajectories = self.get_status_trajecories(specific_statuses)
        assert set(labels.keys()) >= set(trajectories.keys()), "label(s) missing for existing statuses in the time " \
                                                               "course "
        simulation_timepoints = trajectories[list(trajectories.keys())[0]]['time'].values

        for status in trajectories.keys():
            plt.plot(simulation_timepoints, trajectories[status][status].values, label=labels[status])

        plt.title('SecondPlot CoronaABM')
        plt.legend()
        plt.show()
        if save_figure:
            plt.savefig('output_plot.png')

# todo: plot location ID/type timecourse.

'''# testing
model = ModeledPopulatedWorld(100, 400, 5)
simulation1 = Simulation(model, 100)
simulation1.plot_status_timecourse()
'''