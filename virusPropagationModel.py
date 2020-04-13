from human import *
from location import *
from age_initialisation import random_age
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class ModeledPopulatedWorld(object):
    """
    A Class which initializes a world with location and humans (a static snapshot of its origin).
    This class can be used as an object by the class Simulate to simulate this populated world's time course

    Attributes
    ----------
    number_of_locs : int
        The amount of location objects to initialize
    number_of_people : int
        The amount of human objects to initialize
    initial_infections : int
        The amount of human objects initially possibly infected (exact amount depends on a probability)
    world: object of class World
        the initialized world object assigned to this class object
    locations: list of location objects of the class Location
        the locations initialized in this world
    people: set of human objects of the human class

    Methods
    ----------
    initialize_people()
        initializes a set of people (human objects) with assigned ages and schedules
        :param number_of_people: int. The amount of people to initialize
        :return people: set. a set of human objects

    create_schedule()
        creates a schedule, depending on a given age and locations
        :param age: int. given age for a human from whom this schedule should be
        :param locations: list of location objects to which the human can go
        :return sched: dict. specifies times of transitions and assigned locations

    infect()
        infects people (list of humans) initially
        :param amount: int. amount of people to initially infect
    """

    def __init__(self, number_of_locs, number_of_people, initial_infections):
        self.number_of_locs = number_of_locs
        self.number_of_people = number_of_people
        self.initial_infections = initial_infections
        self.world = World(self.number_of_locs)
        self.locations = self.world.locations
        self.people = self.initialize_people(self.number_of_people)
        self.infect(self.initial_infections)

    def initialize_people(self, number_of_people):  # idee martin: skalenfeiheit
        """
        initializes a set of people (human objects) with assigned ages and schedules
        :param number_of_people: int. The amount of people to initialize
        :return people: set. a set of human objects
        """
        people = set()
        for n in range(number_of_people):
            age = random_age()
            schedule = self.create_schedule(age, self.locations)
            people.add(Human(n, age, schedule, schedule['locs'][0]))
        return people

    def create_schedule(self, age, locations):
        """
        creates a schedule, depending on a given age and locations
        :param age: int. given age for a human from whom this schedule should be
        :param locations: list of location objects to which the human can go
        :return sched: dict. specifies times of transitions and assigned locations
        """
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

    def infect(self, amount):
        """
        infects people (list of humans) initially
        :param amount: int. amount of people to initially infect
        """
        to_infect = random.sample(self.people, amount)  # randomly choose who to infect
        for p in to_infect:
            # p.status = 'I'
            p.get_infected(1.0, 0)


class Simulation(object):
    """
    A Class which contains a simulation based on a specific ModeledPopulatedWorld object.

    Attributes
    ----------
    modeled_populated_world : object of class ModeledPopulatedWorld
        the initialized populated world that is to be simulated over time
    time_steps: int
        the amount of time steps to simulate
    time : int
        the last point in time the time course of this simulation
    simulation_timecourse : pd.DataFrame
        contains a dataframe which includes all of the human state attributes
    statuses_in_timecourse: list
        list of the statuses
    people: set of human objects of the human class

    Methods
    ----------
    get_person_attributes_per_time()
        gets the location, status, and flags of a human object along with the current time
        :param person: object of the Human class
        :param only_status: bool. set True in case you dont want to return the flags too
        :return: dict. with all the attributes mentioned above

    run_simulation()
        simulates the trajectories of all the attributes of the population
        :return: DataFrame which contains the time course of the simulation

    get_statuses_in_timecourse()
        gets a list of the statuses in the time course
        :return: list. list of available statuses

    get_status_trajectories()
        gets the commutative amount of each status per point in time as a trajectory
        :param specific_statuses: List. Optional arg for getting only a subset  of statuses
        :return: DataFrame. The time courses for the specified statuses

    get_location_with_type_trajectory()
        uses the location ids in the simulation timecourse to reconstruct location types
        :return: DataFrame. Contains location ids, time, human ids and location types

    plot_status_timecourse()
        plots the time course for selected statuses
        :param save_figure:  Bool. Flag for saving the figure as an image
        :param specific_statuses:   List. Optional arg for getting only a
        subset  of statuses. if not specified, will plot all available statuses

    plot_flags_timecourse()
        plots the time course for the selected flags
        :param specific_flags: list. given flags to be included in the plot
        :param save_figure: bool. Flag for saving the figure as an image

    plot_location_type_occupancy_timecourse()
        plots the occupancy of the location types in the time course
        :param specific_types: list. List of specific types to plot (only)
        :param save_figure: bool. Whether to save the figure

    """

    def __init__(self, modeled_populated_world, time_steps):
        self.modeled_populated_world = modeled_populated_world
        self.time_steps = time_steps
        self.time = 0
        self.simulation_timecourse = self.run_simulation()
        self.statuses_in_timecourse = self.get_statuses_in_timecourse()

    def get_person_attributes_per_time(self, person, only_status=False):
        """
        gets the location, status, and flags of a human object along with the current time
        :param person: object of the Human class
        :param only_status: bool. set True in case you dont want to return the flags too
        :return: dict. with all the attributes mentioned above
        """
        if only_status:
            attr = person.get_status()
        else:
            attr = {**person.get_status(), **person.get_flags()}
        return {**attr, **{'time': self.time}}

    def run_simulation(self):
        """
        simulates the trajectories of all the attributes of the population
        :return: DataFrame which contains the time course of the simulation
        """
        population_size = len(self.modeled_populated_world.people)
        timecourse = np.empty(population_size*self.time_steps, dtype=object)
        for step in range(self.time_steps):
            person_counter = step*population_size
            self.time += 1
            for p in self.modeled_populated_world.people:  #
                p.update_state(self.time)
            for p in self.modeled_populated_world.people:  # don't call if hospitalized
                p.move(self.time)
                timecourse[person_counter] = self.get_person_attributes_per_time(p)
                person_counter += 1
        return pd.DataFrame(list(timecourse))

    def get_statuses_in_timecourse(self):
        """
        gets a list of the statuses in the time course
        :return: list. list of available statuses
        """
        return list(set(self.simulation_timecourse['status']))

    def get_status_trajectories(self, specific_statuses=None):
        """
        gets the commutative amount of each status per point in time as a trajectory
        :param specific_statuses: List. Optional arg for getting only a subset  of statuses
        :return: DataFrame. The time courses for the specified statuses
        """
        if specific_statuses is None:
            statuses = self.get_statuses_in_timecourse()
        else:
            assert set(specific_statuses) <= set(self.statuses_in_timecourse), \
                'specified statuses (' + str(set(specific_statuses)) + ') dont match those in  in the population (' + \
                str(set(self.statuses_in_timecourse)) + ')'
            statuses = specific_statuses
        status_trajectories = {}
        s_t = self.simulation_timecourse.copy()
        s_t.loc[:, 'ones'] = np.ones(s_t.shape[0])
        for status in statuses:
            df = s_t[s_t['status'] == status]
            gdf = df.groupby('time')
            stat_t = gdf.sum()['ones']
            df = pd.concat([pd.Series(np.arange(0, self.time_steps+1)), stat_t],
                           axis=1).loc[1:].fillna(0)
            df.columns = ['time', status]
            status_trajectories[status] = df
        return status_trajectories

    def get_location_with_type_trajectory(self):
        """
        uses the location ids in the simulation timecourse to reconstruct location types
        :return: DataFrame. Contains location ids, time, human ids and location types
        """
        loc_id_to_type_dict = {loc.get_location_id(): loc.get_location_type()
                               for loc in self.modeled_populated_world.locations}
        location_traj_df = self.simulation_timecourse[{'h_ID', 'loc', 'time'}].copy()
        loc_type_traj = np.empty(len(location_traj_df.index), dtype=object)
        for i in range(len(loc_type_traj)):
            loc_type_traj[i] = loc_id_to_type_dict[location_traj_df['loc'][i]]

        location_traj_df['loc_type'] = loc_type_traj
        return location_traj_df

    def plot_status_timecourse(self, specific_statuses=None, save_figure=False):
        """
        plots the time course for selected statuses
        :param save_figure:  Bool. Flag for saving the figure as an image
        :param specific_statuses:   List. Optional arg for getting only a
        subset  of statuses. if not specified, will plot all available statuses
        """
        labels = {
            'S': 'Susceptible',
            'R': 'Recovered',
            'I':  'Infected',
            'D':  'Dead'
        }
        trajectories = self.get_status_trajectories(specific_statuses)
        assert set(labels.keys()) >= set(trajectories.keys()), "label(s) missing for existing statuses in the time " \
                                                               "course "
        simulation_timepoints = trajectories[list(trajectories.keys())[0]]['time'].values

        for status in trajectories.keys():
            plt.plot(simulation_timepoints,
                     trajectories[status][status].values, label=labels[status])

        plt.title('status trajectories')
        plt.legend()
        plt.show()
        if save_figure:
            plt.savefig('status_plot.png')

    def plot_flags_timecourse(self, specific_flags=None, save_figure=False):
        """
        plots the time course for the selected flags
        :param specific_flags: list. given flags to be included in the plot
        :param save_figure: bool. Flag for saving the figure as an image
        """
        if specific_flags is None:
            cols = list(self.simulation_timecourse.columns)
            random_person = random.choice(list(self.modeled_populated_world.people))
            status_cols = random_person.get_status().keys()
            cols_of_interest = [ele for ele in cols if ele not in list(status_cols)]
        else:
            cols_of_interest = specific_flags + ['time']
        df = self.simulation_timecourse[set(cols_of_interest)].copy()
        gdf = df.groupby('time')
        flag_sums = gdf.sum()
        simulation_timepoints = list(gdf.groups.keys())
        for flag in flag_sums.columns:
            plt.plot(simulation_timepoints, flag_sums[flag], label=str(flag))
        plt.title('flags trajectories')
        plt.legend()
        plt.show()
        if save_figure:
            plt.savefig('flags_plot.png')

    def plot_location_type_occupancy_timecourse(self, specific_types=None, save_figure=False):
        """
        plots the occupancy of the location types in the time course
        :param specific_types: list. List of specific types to plot (only)
        :param save_figure: bool. Whether to save the figure
        """
        locations_df = self.get_location_with_type_trajectory().copy()
        available_loc_types = set(locations_df['loc_type'])
        if specific_types is not None:
            assert available_loc_types >= set(specific_types),\
                " specific types provided (" + str(specific_types) + ") " \
                "do not match those in the timecourse (" + str(available_loc_types) + " )"
            loc_types = specific_types
        else:
            loc_types = available_loc_types
        for loc_type in loc_types:
            df = locations_df[['time', 'loc_type']]
            df_of_location = df[df['loc_type'] == loc_type].rename(columns={'loc_type': loc_type})
            location_count = df_of_location.groupby('time').count()
            plt.plot(list(location_count.index.values), location_count[loc_type], label=loc_type)
        plt.title('location occupancy trajectories')
        plt.legend()
        plt.show()
        if save_figure:
            plt.savefig('loc_types_occupancy_plot.png')
