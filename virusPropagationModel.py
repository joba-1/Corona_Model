from human import *
from location import *
from initialize_households import initialize_household
from VPM_save_and_load import *
import VPM_plotting as vpm_plt
import VPM_network_analysis as vpm_neta
from parse_schedule import parse_schedule
import random
import pandas as pd
import numpy as np
import copy
import numpy.random as npr
import glob
from scipy import sparse
from collections import OrderedDict as ordered_dict


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
        the population of this world

    Methods
    ----------
    save()
    wrapper for saveandloadobjects.save
        :param saving_object: object(modeledPopulatedWorld or Simulation) to be saved
        :param filename: string, file to which it should be saved - date and time will be added
        :param date_suffix: bool, whether to add date and time to filename

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

    def __init__(self, number_of_locs, initial_infections=1, world_from_file=False, agent_agent_infection=False,
                 geofile_name='datafiles/Buildings_Gangelt_MA_3.csv', input_schedules='schedules_standard', automatic_initial_infections=True):
        self.world_from_file = world_from_file
        self.agent_agent_infection = agent_agent_infection
        self.number_of_locs = number_of_locs
        self.initial_infections = initial_infections
        self.geofile_name = geofile_name
        self.world = World(from_file=self.world_from_file, number_of_locs=self.number_of_locs,
                           geofile_name=self.geofile_name)
        self.locations = self.world.locations
        self.input_schedules = input_schedules
        self.people = self.initialize_people(self.agent_agent_infection)
        self.number_of_people = len(self.people)
        if automatic_initial_infections:
            self.initialize_infection(amount=self.initial_infections)
        self.location_types = self.get_location_types()

    # folder='saved_objects/'):
    def save(self, filename, obj_type_suffix=True, date_suffix=True, **kwargs):
        """
        wrapper for VPM_save_and_load.save_simulation_object
        :param obj_type_suffix: flag for saving the type of the object in the name of the file
        :param filename: string, file to which it should be saved - date and time will be added
        :param date_suffix: bool, whether to add date and time to filename
        """
        if obj_type_suffix:
            save_simulation_object(self, filename + '_worldObj', date_suffix, **kwargs)
        else:
            save_simulation_object(self, filename, date_suffix, **kwargs)

    def initialize_people(self, agent_agent_infection):
        """
        initializes a set of people (human objects) with assigned ages and schedules
        :return people: set. a set of human objects
        """
        people = set()
        for home in [h for h in self.locations.values() if h.location_type == 'home']:
            home_type, home_size, ages = initialize_household()
            for age in ages:
                n = len(people) + 1
                schedule, diagnosed_schedule = self.create_schedule(age, home)
                if age > 99:
                    age = 99
                elif age < 0:
                    age = 0
                people.add(Human(n, age, schedule, diagnosed_schedule, home,
                                 enable_infection_interaction=agent_agent_infection))
        return people

    def create_schedule(self, age, home):
        """
        creates a schedule, depending on a given age and locations
        :param age: int. given age for a human from whom this schedule should be
        :param locations: list of location objects to which the human can go
        :return sched: dict. specifies times of transitions and assigned locations
        """

        ## standard schedule ##

        schedules = parse_schedule(self.input_schedules)
        for bound in schedules['upper_bounds']:
            if age <= bound:
                schedule = copy.deepcopy(npr.choice(
                    schedules[bound][0], p=schedules[bound][1]))
                break
        my_locations = {}
        for loc in schedule['locs']:
            if not loc in my_locations:
                if loc == 'home':
                    my_locations['home'] = home.ID
                    continue
                elif loc[-1].isdigit():
                    l_type = loc[:-2]
                else:
                    l_type = loc
                closest = home.closest_loc(l_type)
                if closest:
                    possible_loc_ids = [l for l in closest[:10] if not l in my_locations.values()]
                    if not possible_loc_ids:
                        possible_loc_ids = [l for l in closest[:10]]
                else:
                    possible_loc_ids = [l.ID for l in self.locations.values(
                    ) if not l.ID in my_locations.values() and l.location_type == l_type]
                    if not possible_loc_ids:
                        possible_loc_ids = [
                            l.ID for l in self.locations.values() if l.location_type == l_type]

                probs = [len(possible_loc_ids) - i for i in range(len(possible_loc_ids))]
                norm_probs = [float(v) / sum(probs) for v in probs]
                loc_id = npr.choice(possible_loc_ids, p=norm_probs)
                my_locations[loc] = loc_id

        for i, loc in enumerate(schedule['locs']):
            schedule['locs'][i] = self.locations[my_locations[loc]]

        ## diagnosed schedule ##

        diagnosed_schedule = copy.deepcopy(npr.choice(
            schedules['diagnosed'][0], p=schedules['diagnosed'][1]))

        if isinstance(diagnosed_schedule, str):
            diag_type = diagnosed_schedule
            diagnosed_schedule = copy.deepcopy(schedule)
            diagnosed_schedule['type'] = diag_type
        else:
            for loc in diagnosed_schedule['locs']:
                if not loc in my_locations:
                    if loc[-1].isdigit():
                        l_type = loc[:-2]
                    else:
                        l_type = loc
                    closest = home.closest_loc(l_type)
                    if closest:
                        possible_loc_ids = [l for l in closest[:10]
                                            if not l in my_locations.values()]
                        if not possible_loc_ids:
                            possible_loc_ids = [l for l in closest[:10]]
                    else:
                        possible_loc_ids = [l.ID for l in self.locations.values(
                        ) if not l.ID in my_locations.values() and l.location_type == l_type]
                        if not possible_loc_ids:
                            possible_loc_ids = [
                                l.ID for l in self.locations.values() if l.location_type == l_type]

                    probs = [len(possible_loc_ids) - i for i in range(len(possible_loc_ids))]
                    norm_probs = [float(v) / sum(probs) for v in probs]
                    loc_id = npr.choice(possible_loc_ids, p=norm_probs)
                    my_locations[loc] = loc_id

            for i, loc in enumerate(diagnosed_schedule['locs']):
                diagnosed_schedule['locs'][i] = self.locations[my_locations[loc]]

        return schedule, diagnosed_schedule

    def initialize_infection(self, amount=1, specific_people_ids=None):
        """
        infects people (list of humans) initially
        :param amount: int. amount of people to initially infect
        """
        if specific_people_ids is None:
            to_infect = random.sample(self.people, amount)  # randomly choose who to infect
        else:
            to_infect = [p for p in list(self.people) if p.ID in specific_people_ids]
        for p in to_infect:
            p.set_initially_infected()

    def get_location_types(self):
        location_types = list(self.world.loc_class_dic.keys())
        location_types.remove('excluded_buildings')
        location_types.append('home')
        return location_types

    # dict
    def get_distribution_of_location_types(self):
        """
        gets the counts of each type of location initialized in this world
        :param loc_types: the location types to count
        :return: dict. depicts per location type the sum (count) of this type in this world
        """
        # if loc_types is None:
        #    loc_types = ['home', 'work', 'public', 'school', 'hospital', 'cemetery']
        location_counts = {}
        for loc_type in self.location_types:
            location_counts[loc_type] = sum(
                [1 for x in self.locations.values() if x.location_type == loc_type])
        return location_counts

    # DF
    def get_distribution_of_ages_and_infected(self, age_groups_step=10):
        """
        gets the distribution of the statuses for specified age groups
        :param age_groups_step: int. the step between the ages grouped for the distribution
        :return: DataFrame. The distribution of statuses by age group
        """
        agent_ages = pd.DataFrame([{'age': p.age, 'status': p.status} for p in self.people])
        oldest_person = agent_ages['age'].max()
        max_age = round(oldest_person, -1)
        if max_age < oldest_person:
            max_age += 10
        group_by_age = pd.crosstab(agent_ages.age, agent_ages.status)
        status_by_age_range = group_by_age.groupby(pd.cut(group_by_age.index,
                                                          np.arange(
                                                              0, max_age + age_groups_step, age_groups_step),
                                                          right=False)).sum()
        status_by_age_range.index.name = 'age groups'
        return status_by_age_range

    def get_remaining_possible_initial_infections(self, ini_I_list):
        """
        Compares list of agent IDs to initally infect with IDs of initially recovered agents.
        Rewrites a list of possible agents.
        :return: list of agent IDs
        """
        recovered_people = [p.ID for p in self.people if p.status == 'R']
        print('amount of initially recovered agents:',len(recovered_people))
        inif_I_list_new = []

        for i in ini_I_list:
            x = i
            while x in recovered_people or x in inif_I_list_new:
                x += 1
                if x < self.number_of_people:
                    pass
                else:
                    raise Exception("Not enough, humans to infect")
            if x not in inif_I_list_new:
                inif_I_list_new.append(x)
        if not all(inif_I_list_new == ini_I_list):
            print('list of initial infected changed from ',
                  ini_I_list, ' to ', inif_I_list_new)
        return inif_I_list_new

    def plot_distribution_of_location_types(self):
        """
        plots the distribution of the location types that were initialized in this world
        :param modeled_pop_world_obj: obj of ModeledPopulatedWorld Class
        """
        vpm_plt.plot_distribution_of_location_types(self)

    def plot_locations_and_schedules(self, **kwargs):
        """
        plots the distribution of the location and schedule types that were initialized
        in this world
        :param modeled_pop_world_obj: obj of ModeledPopulatedWorld Class
        """
        vpm_plt.plot_locations_and_schedules(self, **kwargs)

    def plot_initial_distribution_of_ages_and_infected(self, age_groups_step=10, **kwargs):
        """
        plots a histogram of the ages of the population and how many of those are infected
        :param age_groups_step: int. Determines the amount of ages in an age group (like 10: 0-10, 10-20 ...)
        """
        vpm_plt.plot_initial_distribution_of_ages_and_infected(self, age_groups_step, **kwargs)


class Simulation(object):
    """
    A Class which contains a simulated time course of a given ModeledPopulatedWorld object

    Attributes
    ----------
    simulation_object : ModeledPopulatedWorld or Simulation object
        the object used as basis for the simulation, which depicts a populated world at some time point
    time_steps : int
        The amount of time steps to simulate (hours)
    people: set of human objects of the human class
        the population of this world
    locations: list of location objects of the class Location
        the locations in this world
    time: int
        the current in-silico time of this objects. Gets updated during when the simulation runs at initiation
    simulation_timecourse: DataFrame:
        contains the information regarding the humans and where they are since t=0
    statuses_in_timecourse: list
        a list of all the statuses available in the time course (e.g. I, for "infected")

    Methods
    ----------
    save()
    wrapper for saveandloadobjects.save
        :param saving_object: object(modeledPopulatedWorld or Simulation) to be saved
        :param filename: string, file to which it should be saved - date and time will be added
        :param date_suffix: bool, whether to add date and time to filename

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

    get_durations()
        Returns a pandas DataFrame with the durations of certain states of the agents.
        Durations included so far (columns in the data-frame):
        From infection to death ('infection_to_death'),
        from infection to recovery ('infection_to_recovery'),
        from infection to hospital ('infection_to_hospital') and
        from hospital to ICU (hospital_to_icu).

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

    export_time_courses_as_csvs()
        export the human simulation time course, human commutative status time course, and locations time course
        :param identifier: a given identifying name for the file which will be included in the name of the exported file

    """

    def __init__(self, object_to_simulate, time_steps, run_immediately=True, copy_sim_object=True, random_seed=None):

        self.random_seed = random_seed
        if self.random_seed is not None:
            random.seed(self.random_seed)
            npr.seed(self.random_seed)

        assert type(object_to_simulate) == ModeledPopulatedWorld or type(object_to_simulate) == Simulation, \
            "\'object_to_simulate\' can only be of class \'ModeledPopulatedWorld\' or \'Simulation\' "

        self.location_types = object_to_simulate.location_types
        if isinstance(object_to_simulate, ModeledPopulatedWorld):
            self.time_steps = time_steps
            self.people = copy.deepcopy(object_to_simulate.people)
            #self.locations = copy.deepcopy(object_to_simulate.locations)
            self.number_of_people = len(self.people)

            self.locations = {}
            for p in self.people:
                self.locations.update({p.loc.ID: p.loc})
                self.locations.update({l.ID: l for l in list(p.schedule['locs'])})
                self.locations.update({l.ID: l for l in list(p.diagnosed_schedule['locs'])})
                for l in p.schedule['locs']:
                    for sl in l.special_locations.keys():
                        self.locations.update(
                            {l.special_locations[sl][0].ID: l.special_locations[sl][0]})
                for l in p.diagnosed_schedule['locs']:
                    for sl in l.special_locations.keys():
                        self.locations.update(
                            {l.special_locations[sl][0].ID: l.special_locations[sl][0]})
                self.locations[p.loc.ID].enter(p)

            self.simulation_timecourse = pd.DataFrame()
            self.time = 0
        elif isinstance(object_to_simulate, Simulation):
            self.time_steps = time_steps
            if copy_sim_object:
                self.people = copy.deepcopy(object_to_simulate.people)
                #self.locations = copy.deepcopy(object_to_simulate.locations)
                #self.locations = {p.loc.ID: p.loc for p in self.people}
                self.locations = {}
                for p in self.people:
                    self.locations.update({p.loc.ID: p.loc})
                    self.locations.update({l.ID: l for l in list(p.schedule['locs'])})
                    self.locations.update({l.ID: l for l in list(p.diagnosed_schedule['locs'])})
                    for l in p.schedule['locs']:
                        for sl in l.special_locations.keys():
                            self.locations.update(
                                {l.special_locations[sl][0].ID: l.special_locations[sl][0]})
                    for l in p.diagnosed_schedule['locs']:
                        for sl in l.special_locations.keys():
                            self.locations.update(
                                {l.special_locations[sl][0].ID: l.special_locations[sl][0]})
                    self.locations[p.loc.ID].enter(p)
            else:
                self.people = object_to_simulate.people
                self.locations = object_to_simulate.locations
            self.simulation_timecourse = object_to_simulate.simulation_timecourse
            self.time = object_to_simulate.time

        self.statuses_in_timecourse = ['S', 'I', 'R', 'D']
        self.interaction_frequency = 1
        self.interaction_matrix = True

        if run_immediately:
            self.simulate()

    def set_seed(self, random_seed_value):
        self.random_seed = random_seed_value
        random.seed(self.random_seed)
        npr.seed(self.random_seed)

    def save(self, filename, obj_type_suffix=True, date_suffix=True, **kwargs):
        """
        wrapper for VPM_save_and_load.save_simulation_object
        :param obj_type_suffix: flag for saving the type of the object in the name of the file
        :param filename: string, file to which it should be saved - date and time will be added
        :param date_suffix: bool, whether to add date and time to filename
        """
        if obj_type_suffix:
            save_simulation_object(self, filename + '_simulationObj', date_suffix, **kwargs)
        else:
            save_simulation_object(self, filename, date_suffix, **kwargs)

    def simulate(self, timecourse_keys='all'):
        self.simulation_timecourse = pd.concat([self.simulation_timecourse, self.run_simulation(
            timecourse_keys=timecourse_keys)], ignore_index=True)
        #self.statuses_in_timecourse = self.get_statuses_in_timecourse()

    def run_simulation(self, timecourse_keys='all'):
        """
        simulates the trajectories of all the attributes of the population
        :return: DataFrame which contains the time course of the simulation
        """
        #population_size = len(self.people)
        # print(population_size)
        timecourse = []
        if self.time == 0:
            for p in self.people:  # makes sure he initial conditions are t=0 of the time course
                timecourse.append(tuple(p.get_information_for_timecourse(
                    self.time, keys_list=timecourse_keys).values()))
            first_simulated_step = 1
        else:
            first_simulated_step = 0
        for step in range(first_simulated_step, self.time_steps):
            self.time += 1
            for p in self.people:
                p.update_state(self.time)
            for l in self.locations.values():
                l.let_agents_interact(mu=self.interaction_frequency,
                                      interaction_matrix=self.interaction_matrix)
            for p in self.people:  # don't call if hospitalized
                timecourse.append(tuple(p.get_information_for_timecourse(
                    self.time, keys_list=timecourse_keys).values()))
                p.set_stati_from_preliminary()
                p.move(self.time)
        return pd.DataFrame(timecourse, columns=list(p.get_information_for_timecourse(self.time, keys_list=timecourse_keys).keys()))

    def change_agent_attributes(self, input):
        """
        Applies the change of the values of certain specified agent-attributes.
        The input is a dictionary with the IDs of agents, one wants to change an attribute for.
        It is possible to have one or many entries with specific agent-ID(s); or use the key 'all',
        to specifiy that the changes should be applied to all agents.
        The corresponding value to this keys is another dictionary,
        which hast the names of the attributes to change as keys().
        In this attribute-specific dictionary one finds two keys 'value' and 'type'.
        'type' can take on the values 'replacement' or 'multiplicative_factor';
        where 'replacement' specifies to replace the old attribue-value and
        'multiplicative_factor' specifies the multiplication of the old attribute-value with a given factor.
        PLEASE NOTE: The value of the 'multiplicative_factor'-key MUST be numeric!
                    Furthermore the target attribute must then be also numeric.
        The value to replace or multiply with is then found by the key 'value'.
        Examples:
            1:
            {all:{attr1:{'value':val1,'type':'replacement'},
                  attr2:{'value':val2,'type':'multiplicative_factor'}}}
            2:
            {id1:{attr1:{'value':val1,'type':'replacement'},
                  attr2:{'value':val2,'type':'multiplicative_factor'}},
             id2:{attr1:{'value':val1,'type':'replacement'},
                  attr2:{'value':val2,'type':'multiplicative_factor'}}}

        """
        if len(list(input.keys())) == 1:
            if list(input.keys())[0] == 'all':
                input_all = input['all']
                for p in self.people:
                    for attribute in input_all.keys():
                        if input_all[attribute]['type'] == 'replacement':
                            setattr(p, attribute, input_all[attribute]['value'])
                        elif input_all[attribute]['type'] == 'multiplicative_factor':
                            setattr(p, attribute, getattr(p, attribute) *
                                    input_all[attribute]['multiplicative_factor'])
            else:
                id = list(input.keys())[0]
                respective_person = [p for p in self.people if str(p.ID) == id]
                if len(respective_person) > 0:
                    for attribute in input[id].keys():
                        if input[id][attribute]['type'] == 'replacement':
                            setattr(respective_person, attribute, input[id][attribute]['value'])
                        elif input[id][attribute]['type'] == 'multiplicative_factor':
                            setattr(respective_person, attribute, getattr(respective_person,
                                                                          attribute) * input[id][attribute][
                                'multiplicative_factor'])
                else:
                    print('Error: No agent with ID "{}"'.format(id))
        else:
            for id in list(input.keys()):
                respective_person = [p for p in self.people if str(p.ID) == id]
                if len(respective_person) > 0:
                    for attribute in input[id].keys():
                        if input[id][attribute]['type'] == 'replacement':
                            setattr(respective_person, attribute, input[id][attribute]['value'])
                        elif input[id][attribute]['type'] == 'multiplicative_factor':
                            setattr(respective_person, attribute, getattr(respective_person,
                                                                          attribute) * input[id][attribute][
                                'multiplicative_factor'])
                else:
                    print('Error: No agent with ID "{}"'.format(id))

    # def get_statuses_in_timecourse(self):
        """
        gets a list of the statuses in the time course
        :return: list. list of available statuses
        """
    #    stati_list = ['S', 'I', 'R', 'D']
    #    stati = self.simulation_timecourse.copy()
    #    for i in range(len(stati_list)):
    #        stati.loc[self.simulation_timecourse['status'] == i, 'status'] = stati_list[i]
    #    return ['S', 'I', 'R', 'D']#list(set(stati['status']))

    # DF
    def get_status_trajectories(self, specific_statuses=None, specific_people=None):
        """
        gets the commutative amount of each status per point in time as a trajectory
        :param specific_statuses: List. Optional arg for getting only a subset  of statuses
        :return: DataFrame. The time courses for the specified statuses
        """
        if specific_statuses is None:
            statuses = self.statuses_in_timecourse  # self.get_statuses_in_timecourse()
        else:
            assert set(specific_statuses) <= set(self.statuses_in_timecourse), \
                'specified statuses (' + str(set(specific_statuses)) + ') dont match those in  in the population (' + \
                str(set(self.statuses_in_timecourse)) + ')'
            statuses = specific_statuses

        status_trajectories = {}

        stati_list = self.statuses_in_timecourse
        timecourse_df = self.simulation_timecourse.copy()
        for i in range(len(stati_list)):
            timecourse_df.loc[self.simulation_timecourse['status'] == i, 'status'] = stati_list[i]

        if specific_people is None:
            status_tc = timecourse_df[['time', 'status']]
        else:
            traject = timecourse_df
            list_of_peple_IDs_of_type = [
                p.ID for p in self.people if p.type == specific_people]  # Specify doctors here##
            humans_in_traject = list(traject['h_ID'])
            rows_to_remove = set(traject.index)
            for i in list_of_peple_IDs_of_type:
                rows_to_remove -= set([j for j, k in enumerate(humans_in_traject) if k == i])
            status_tc = traject.drop(list(rows_to_remove))[['time', 'status']]

        t_c_times = status_tc['time'].copy().unique()  # copy?
        for status in statuses:
            df = status_tc[status_tc['status'] == status].copy().rename(
                columns={'status': status})  # copy?
            time_grouped_status_count = df.groupby('time').count()
            zero_occupancy_df = pd.DataFrame({'time': t_c_times, status: np.zeros(
                len(t_c_times))}).set_index('time')
            merged_df = time_grouped_status_count.merge(zero_occupancy_df, on='time',
                                                        suffixes=('', '_zeros'),
                                                        how='right').fillna(0).sort_index().reset_index()
            status_trajectories[status] = merged_df[['time', status]]

        return status_trajectories

    # DF
    def get_location_with_type_trajectory(self):
        """
        uses the location ids in the simulation timecourse to reconstruct location types
        :return: DataFrame. Contains location ids, time, human ids and location types
        """
        loc_id_to_type_dict = {loc.get_location_id(): loc.get_location_type() for loc in
                               self.locations.values()}
        location_traj_df = self.simulation_timecourse[{'h_ID', 'loc', 'time'}].copy()
        loc_type_traj = np.empty(len(location_traj_df.index), dtype=object)
        for i in range(len(loc_type_traj)):
            loc_type_traj[i] = loc_id_to_type_dict[location_traj_df['loc'][i]]

        location_traj_df['loc_type'] = loc_type_traj
        return location_traj_df

    # DF
    def get_location_and_status(self):
        """
        processes simulation output to generate DataFrame
        with location and sums of people for each status
        :return: pandas dataframe

        :example:
        status   loc     time    D        I       R       S   x_coordinate  y_coordinate
        0          0      1      0.0     0.0     0.0     1.0      4              0
        1          0      2      0.0     0.0     0.0     1.0      4              0
        2          0      3      0.0     0.0     0.0     1.0      4              0

        """
        stati_list = self.statuses_in_timecourse
        df = self.simulation_timecourse.copy()
        for i in range(len(stati_list)):
            df.loc[self.simulation_timecourse['status'] == i, 'status'] = stati_list[i]

        df.drop(columns=['Temporary_Flags', 'Cumulative_Flags'], inplace=True)

        d = pd.pivot_table(df, values='h_ID', index=['loc', 'time'],
                           columns=['status'], aggfunc='count')
        table = d.reset_index().fillna(0)

        for stat in ['D', 'I', 'R', 'S']:
            if stat not in table.columns:
                table[stat] = [0] * len(table)

        table['x_coordinate'] = [self.locations[loc_id].coordinates[0] for loc_id in table['loc']]
        table['y_coordinate'] = [self.locations[loc_id].coordinates[1] for loc_id in table['loc']]
        table['location_type'] = [self.locations[loc_id].location_type for loc_id in table['loc']]
        return table

    # DF
    def get_durations(self):
        """
         Returns a pandas DataFrame with the durations of certain states of the agents.
         :return: pandas DataFrame
         """
        df = pd.DataFrame([p.get_infection_info() for p in self.people if not pd.isna(p.stati_times['infection_time'])], columns=[
            'infection_time', 'diagnosis_time', 'recover_time', 'death_time', 'hospitalization_time', 'icu_time'])
        out = pd.DataFrame()
        #out['infection_to_death'] = df['death_time'] - df['infection_time']
        #out['infection_to_hospital'] = df['hospitalization_time'] - df['infection_time']
        out['hospital_to_recovery'] = df['recover_time'] - df['hospitalization_time']
        out['hospital_to_death'] = df['death_time'] - df['hospitalization_time']
        out['hospital_to_icu'] = df['icu_time'] - df['hospitalization_time']
        out['icu_to_death'] = df['death_time'] - df['icu_time']
        out['icu_to_recovery'] = df['recover_time'] - df['icu_time']
        out['infection_to_diagnosis'] = df['diagnosis_time'] - df['infection_time']
        out['infection_to_recovery'] = df['recover_time'] - df['infection_time']
        out['infection_to_death'] = df['death_time'] - df['infection_time']
        out['infection_to_hospital'] = df['hospitalization_time'] - df['infection_time']
        out['diagnosis_to_hospital'] = df['hospitalization_time'] - df['diagnosis_time']
        out['diagnosis_to_recovery'] = df['recover_time'] - df['diagnosis_time']
        out['diagnosis_to_death'] = df['death_time'] - df['diagnosis_time']
        return out

    # DF ## changed. should be used in other functions ?
    def get_infection_event_information(self):
        """
        Returns a pandas DataFrame with information on all infection-events:
        ID of agent, who got infected ('h_ID'),
        ID of location, where agent got infected ('infection_loc_ID'),
        Time, at which agent got infected ('time'),
        ID of infected agent, who infected  ('infected_by_ID'),
        """
        # df = pd.DataFrame([p.get_infection_info() for p in self.people if not pd.isna(p.infection_time)], columns=[
        #    'h_ID', 'place_of_infection', 'infection_time', 'infected_by', 'infected_in_contact_with'])
        # df.sort_values('infection_time').reset_index(drop=True)
        df = self.simulation_timecourse
        df_I = df[df['Infection_event'] > 1].copy()
        cols_to_drop = [x for x in ['Temporary_Flags', 'Cumulative_Flags',
                                    'Interaction_partner', 'status'] if x in list(df_I.columns)]
        df_I.drop(columns=cols_to_drop, inplace=True)
        df_I.set_index('time', inplace=True)
        df_I.columns = ['h_ID', 'infection_loc_ID', 'infected_by_ID']
        return df_I

    # DF
    def get_distribution_of_statuses_per_age(self, group_ages=True, age_groups_step=10):
        """
        gets the distribution of the statuses over time, possibly for specified age groups
        :param group_ages: bool. whether to sum the ages by groups
        :param age_groups_step: int. the step between the ages grouped for the distribution
        returns the entire time course if None
        :return: DataFrame. The distribution of statuses by age group
        :example:
        status    D  I  R  S
        age time
        0   0     0  8  0  9
            1     0  8  0  9
            2     0  8  0  9
            3     0  8  0  9
            4     0  8  0  9
              .. .. .. ..
        100 95    0  0  0  2
            96    0  0  0  2
            97    0  0  0  2
            98    0  0  0  2
            99    0  0  0  2
        :comment: use pt.loc[:,t] to get the values for a specific point in time
        """
        assert type(group_ages) is bool
        agent_ages = pd.DataFrame([{'h_ID': p.ID, 'age': p.age} for p in self.people])
        stati_list = self.statuses_in_timecourse
        df = self.simulation_timecourse.copy()
        for i in range(len(stati_list)):
            df.loc[self.simulation_timecourse['status'] == i, 'status'] = stati_list[i]

        merged_df = df.merge(agent_ages, on='h_ID')
        merged_df.drop(columns=['loc', 'Temporary_Flags', 'Cumulative_Flags'], inplace=True)
        pt = merged_df.pivot_table(values='h_ID', index=['age', 'time'], columns=[
            'status'], aggfunc='count', fill_value=0)
        if group_ages is True:
            ages_in_s_t = np.array(np.unique(np.array(pt.index.get_level_values('age'))))
            oldest_person = np.max(ages_in_s_t)
            max_age = round(oldest_person, -1)
            if max_age < oldest_person:
                max_age += 10
            age_bins = pd.cut(pt.index.get_level_values('age'),
                              np.arange(0, max_age + age_groups_step, age_groups_step),
                              right=False)
            pt = pt.groupby([age_bins, 'time']).sum()
        return pt

    # dict
    def get_infections_per_location_type(self, relative_to_building_number=True):
        """
        :return: dict. The number of infection-events at different locations.
        :param relative_to_building_number: bool. whether to normalize the number of infection-events by number of respective locations
        :example:
                {'home': 5, 'school': 6, ... 'public': 4}
        """
        #infection_events = self.get_infection_event_information()
        #infection_locations = list(infection_events['place_of_infection'])
        loc_infection_dict_0 = dict(zip(self.location_types, [0.0]*len(self.location_types)))
        # we could use get_infection_event_information() here
        infection_events = self.simulation_timecourse[self.simulation_timecourse['Infection_event'] > 0]
        infection_locations = list(infection_events['loc'].values)
        location_types = {l.ID: l.location_type for l in self.locations.values()
                          if l.ID in infection_locations}
        unique_locs = list(set(list(location_types.values())))
        loc_infection_dict = dict(zip(unique_locs, [0]*len(unique_locs)))
        total_buildings_of_type = {}
        for i in unique_locs:
            total_buildings_of_type[i] = len(
                [1 for j in self.locations.keys() if self.locations[j].location_type == i])
        for i_loc in infection_locations:
            respective_type = location_types[i_loc]
            if relative_to_building_number:
                loc_infection_dict[respective_type] += 1 / \
                    total_buildings_of_type[respective_type]
            else:
                loc_infection_dict[respective_type] += 1
        loc_infection_dict_0.update(loc_infection_dict)

        return loc_infection_dict_0

    # DF

    def get_flag_sums_over_time(self, specific_flags=None):
        """
        :return: DataFrame. The number of true flags over time
        :example:
            WasHospitalized  Hospitalized  WasInfected  ICUed  IsInfected  WasDiagnosed  WasICUed  Diagnosed
        time
        0           0             0            1      0           1             0         0          0
        1           0             0            1      0           1             0         0          0
        """
        Temporary_list = [[0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 0, 1]]
        Cumulative_list = [[0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1]]

        parsed_df = pd.DataFrame(index=self.simulation_timecourse.index, columns=[
            'IsInfected', 'Diagnosed', 'Hospitalized', 'ICUed', 'WasInfected', 'WasDiagnosed', 'WasHospitalized', 'WasICUed', 'time'])
        parsed_df['time'] = self.simulation_timecourse['time']

        for i in range(5):
            parsed_df.loc[self.simulation_timecourse['Temporary_Flags'] == i, [
                'IsInfected', 'Diagnosed', 'Hospitalized', 'ICUed']] = Temporary_list[i]
            parsed_df.loc[self.simulation_timecourse['Cumulative_Flags'] == i, [
                'WasInfected', 'WasDiagnosed', 'WasHospitalized', 'WasICUed']] = Cumulative_list[i]

        if specific_flags is None:
            cols_of_interest = ['IsInfected', 'Diagnosed', 'Hospitalized', 'ICUed',
                                'WasInfected', 'WasDiagnosed', 'WasHospitalized', 'WasICUed', 'time']
        else:
            cols_of_interest = specific_flags + ['time']
        sub_df = parsed_df.loc[:, cols_of_interest]
        gdf = sub_df.groupby('time')
        flag_sums = gdf.sum()
        simulation_timepoints = list(gdf.groups.keys())
        return(flag_sums)
    # DF

    def get_location_info(self):
        locations = list(self.locations.values())
        Location_Types = {str(l.ID): l.location_type for l in locations}
        Location_Areas = {str(l.ID): l.area for l in locations}
        Location_Neighbourhood = {str(l.ID): l.neighbourhood_ID for l in locations}
        Location_Info = pd.DataFrame()
        Location_Info['ID'] = [int(i) for i in list(Location_Types.keys())]
        Location_Info['Type'] = list(Location_Types.values())
        Location_Info['Area'] = list(Location_Areas.values())
        Location_Info['Neighbourhood'] = list(Location_Neighbourhood.values())
        return(Location_Info)

    def get_agent_info(self):
        people = list(self.people)
        Agents_Ages = {str(p.ID): p.age for p in people}
        Agents_Homes = {str(p.ID): p.home.ID for p in people}
        Agents_Types = {str(p.ID): p.type for p in people}
        Agent_Info = pd.DataFrame()
        Agent_Info['ID'] = [int(i) for i in list(Agents_Ages.keys())]
        Agent_Info['Age'] = list(Agents_Ages.values())
        Agent_Info['Home'] = list(Agents_Homes.values())
        Agent_Info['Type'] = list(Agents_Types.values())
        return(Agent_Info)

    def get_number_of_infected_households(self, time_span=[0, None], total=False):
        if time_span[1] is None:
            max_ts = self.simulation_timecourse['time'].max()
        else:
            max_ts = time_span[1]
        Agent_Info = self.get_agent_info()
        time_course = self.simulation_timecourse[(self.simulation_timecourse['time'] <= max_ts) & (
            self.simulation_timecourse['time'] >= time_span[0])]
        infected_tc = time_course[time_course['status'] == 1].copy()
        infected_tc['Household'] = [Agent_Info.loc[Agent_Info['ID'] == i, 'Home'].values[0]
                                    for i in list(infected_tc['h_ID'])]
        if total:
            return(len(list(infected_tc['Household'].unique())))
        else:
            timesteps = list(range(time_span[0], max_ts+1))
            out = pd.DataFrame()
            out['time'] = timesteps
            out['households'] = [
                len(list(infected_tc.loc[infected_tc['time'] == t, 'Household'].unique())) for t in timesteps]
            return(out)

    def get_contact_distributions(self, timesteps_per_aggregate=24, human_type='all', min_t=0, max_t=None):
        tc = self.simulation_timecourse
        if max_t is None:
            t_max = tc['time'].max()
        else:
            t_max = max_t

        if human_type == 'all':
            timecourse = tc.loc[(tc['time'] <= t_max) & (tc['time'] >= min_t)].copy()
        else:
            Agent_Info = self.get_agent_info()
            for a in list(Agent_Info.loc[Agent_Info['Type'] == human_type].index):
                tc.loc[tc['h_ID'] == Agent_Info.loc[a, 'ID'],
                       'human_type'] = Agent_Info.loc[a, 'Type']
            timecourse = tc.loc[(tc['time'] <= t_max) & (tc['time'] >= min_t)
                                & (tc['human_type'] == human_type)].copy()

        timecourse['aggregate'] = [int(i/timesteps_per_aggregate) for i in timecourse['time']]
        n_aggregates = timecourse['aggregate'].max()

        interactions_per_time = []
        interactions = []
        interactions_per_agent = {}
        for t in timecourse['time'].unique():
            df_t = timecourse.loc[timecourse['time'] == t, ['time', 'h_ID', 'Interaction_partner']]
            ts_l = []
            for i in df_t.index:
                IP = df_t.loc[i, 'Interaction_partner']
                if df_t.loc[i, 'h_ID'] not in interactions_per_agent.keys():
                    interactions_per_agent[df_t.loc[i, 'h_ID']] = []
                if pd.isna(IP):
                    interactions.append(0)
                    ts_l.append(0)
                    interactions_per_agent[df_t.loc[i, 'h_ID']].append(0)
                else:
                    interactions.append(int(str(IP).count(',')+1))
                    ts_l.append(int(str(IP).count(',')+1))
                    interactions_per_agent[df_t.loc[i, 'h_ID']].append(int(str(IP).count(',')+1))
            interactions_per_time.append(numpy.mean(ts_l))

        mean_interactions_of_agents = {x: numpy.mean(
            interactions_per_agent[x]) for x in interactions_per_agent.keys()}

        out = {}
        for d in range(n_aggregates):
            df_d = timecourse.loc[timecourse['aggregate'] ==
                                  d, ['time', 'h_ID', 'Interaction_partner']]
            h_list = list(df_d['h_ID'].unique())
            partners = [list(set([p for x in list(df_d.loc[(df_d['h_ID'] == h), 'Interaction_partner'])
                                  for p in str(x).split(' , ') if p != 'nan'])) for h in h_list]
            out[d] = dict(zip(h_list, partners))

        n_unique_contacts = []
        agent_unique_contacts = {}
        for d in out.keys():
            for a in out[d].keys():
                n_unique_contacts.append(len(out[d][a]))
                if a not in agent_unique_contacts.keys():
                    agent_unique_contacts[a] = []
                agent_unique_contacts[a].append(len(out[d][a]))

        mean_unique_interactions_per_day = {i: numpy.mean(
            agent_unique_contacts[i]) for i in agent_unique_contacts.keys()}

        agent_dict = {}
        for d in range(n_aggregates):
            for a in out[d].keys():
                if a not in agent_dict.keys():
                    agent_dict[a] = {}
                if d == 0:
                    entry = out[d][a]
                else:
                    last_entry = agent_dict[a][d-1]
                    entry = list(set(last_entry+out[d][a]))
                agent_dict[a][d] = entry

        Day_DF = pd.DataFrame()
        if len(list(agent_dict.keys())) > 0:
            for d in list(agent_dict[list(agent_dict.keys())[0]].keys()):
                Day_DF[d] = [len(agent_dict[a][d]) for a in agent_dict.keys()]

        return({'Mean_interactions_per_agent': mean_interactions_of_agents, 'Mean_interactions_per_timestep': interactions_per_time, 'Mean_unique_interactions_per_agent': mean_unique_interactions_per_day, 'Cumulative_unique_contacts_per_agent': Day_DF})

    def contact_tracing(self, tracing_window=336, time_span=[0, None], timesteps_per_aggregate=24, loc_time_overlap_tracing=True, trace_secondary_infections=True, trace_all_following_infections=False):
        if time_span[1] is None:
            max_ts = self.simulation_timecourse['time'].max()
        else:
            max_ts = time_span[1]
        time_course = self.simulation_timecourse[(self.simulation_timecourse['time'] <= max_ts) & (
            self.simulation_timecourse['time'] >= time_span[0])]
        diag_df = time_course.loc[time_course['Temporary_Flags'] == 2]
        diagnosed_individuals = list(diag_df['h_ID'].unique())
        t_diagnosis = {i: diag_df.loc[diag_df['h_ID'] == i, 'time'].min()
                       for i in diagnosed_individuals}
        t_tracing_period_start = {i: t_diagnosis[i]-tracing_window for i in diagnosed_individuals}

        if loc_time_overlap_tracing:
            n_contacts, n_same_loc_time = zip(
                *[trace_contacts_with_loctime(i, time_course, t_diagnosis, t_tracing_period_start) for i in diagnosed_individuals])
        else:
            #n_contacts = [trace_contacts(i, time_course, t_diagnosis,t_tracing_period_start) for i in diagnosed_individuals]
            n_same_loc_time = [numpy.nan]*len(diagnosed_individuals)
            traced_contacts_time_dict = {}
            for di in diagnosed_individuals:
                if t_diagnosis[di] in traced_contacts_time_dict.keys():
                    traced_contacts_time_dict[t_diagnosis[di]] += trace_contacts(
                        di, time_course, t_diagnosis, t_tracing_period_start)
                else:
                    traced_contacts_time_dict[t_diagnosis[di]] = trace_contacts(
                        di, time_course, t_diagnosis, t_tracing_period_start)

            day_contact_dict = {}
            for td in traced_contacts_time_dict.keys():
                respective_time_aggregate = int(td/timesteps_per_aggregate)
                if respective_time_aggregate in day_contact_dict.keys():
                    day_contact_dict[respective_time_aggregate] += traced_contacts_time_dict[td]
                else:
                    day_contact_dict[respective_time_aggregate] = traced_contacts_time_dict[td]

            unique_contacts_per_day = {
                i: len(list(set(day_contact_dict[i]))) for i in day_contact_dict.keys()}

        n_traced_infections = [time_course.loc[(time_course['Infection_event'] == i) & (time_course['time'] >= t_tracing_period_start[i]) & (
            time_course['time'] <= t_diagnosis[i])].shape[0] for i in diagnosed_individuals]

        # Secondary infections people infected by traced infectees, after tracing-time
        if trace_secondary_infections:
            traced_secondary_infectees = []
            for i in diagnosed_individuals:
                traced_primary_infectees = list(time_course.loc[(time_course['Infection_event'] == i) & (
                    time_course['time'] >= t_tracing_period_start[i]) & (time_course['time'] <= t_diagnosis[i]), 'h_ID'])
                n_secondary_infectees = 0
                for j in traced_primary_infectees:
                    n_secondary_infectees += time_course.loc[(time_course['Infection_event'] == j) & (
                        time_course['time'] >= t_diagnosis[i])].shape[0]
                traced_secondary_infectees.append(n_secondary_infectees)
        else:
            traced_secondary_infectees = [numpy.nan]*len(diagnosed_individuals)

        if trace_all_following_infections:
            # finds all infections, along the infection chains originating from diagnosees, which would be prevend by cutting the infection chain
            only_infection_TC = time_course.loc[time_course['Infection_event'] > 0]
            original_infection_number = int(only_infection_TC.shape[0])
            last_infection_number = original_infection_number
            traced_downstream_infectees = []
            for i in diagnosed_individuals:
                traced_infectees = list(time_course.loc[(time_course['Infection_event'] == i) & (
                    time_course['time'] >= t_tracing_period_start[i]) & (time_course['time'] <= t_diagnosis[i]), 'h_ID'])
                while len(traced_infectees) > 0:
                    new_primary = []
                    for j in traced_infectees:
                        only_infection_TC = only_infection_TC.loc[(only_infection_TC['h_ID'] != j) | (
                            only_infection_TC['time'] <= t_diagnosis[i])]
                        traced_infectees_secondary = list(
                            only_infection_TC.loc[only_infection_TC['Infection_event'] == j, 'h_ID'])
                        new_primary += traced_infectees_secondary
                    traced_infectees = new_primary
                traced_downstream_infectees.append(
                    last_infection_number-int(only_infection_TC.shape[0]))
                last_infection_number = int(only_infection_TC.shape[0])

            only_infection_TC = time_course.loc[time_course['Infection_event'] > 0]
            original_infection_number = int(only_infection_TC.shape[0])
            last_infection_number = original_infection_number
            traced_downstream_infectees_unpreventable = []
            for i in diagnosed_individuals:
                traced_infectees = list(time_course.loc[(time_course['Infection_event'] == i) & (
                    time_course['time'] <= t_diagnosis[i]), 'h_ID'])
                while len(traced_infectees) > 0:
                    new_primary = []
                    for j in traced_infectees:
                        only_infection_TC = only_infection_TC.loc[only_infection_TC['h_ID'] != j]
                        traced_infectees_secondary = list(
                            only_infection_TC.loc[only_infection_TC['Infection_event'] == j, 'h_ID'])
                        new_primary += traced_infectees_secondary
                    traced_infectees = new_primary
                traced_downstream_infectees_unpreventable.append(
                    last_infection_number-int(only_infection_TC.shape[0]))
                last_infection_number = int(only_infection_TC.shape[0])
        else:
            traced_downstream_infectees = [numpy.nan]*len(diagnosed_individuals)
            traced_downstream_infectees_unpreventable = [numpy.nan]*len(diagnosed_individuals)

        out = pd.DataFrame()
        out['time'] = [t_diagnosis[i] for i in diagnosed_individuals]
        out['diagnosed_individuals'] = [1]*out.shape[0]
        out['traced_infections'] = n_traced_infections
        out['traced_secondary_infections'] = traced_secondary_infectees
        out['traced_all_downstream_infections'] = traced_downstream_infectees_unpreventable
        out['traced_preventable_downstream_infections'] = traced_downstream_infectees
        #out['traced_contacts'] = n_contacts
        out['loc_time_overlap'] = n_same_loc_time
        out['aggregated_time'] = [int(i/timesteps_per_aggregate) for i in out['time']]
        out2 = out.groupby(['aggregated_time']).sum()
        out2['traced_contacts'] = [unique_contacts_per_day[i] for i in out2.index]
        return(out2.drop(columns=['time']))

    def get_age_group_specific_interaction_patterns(self, lowest_timestep=0, highest_timestep=None, timesteps_per_aggregate=24, age_groups=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]):
        if highest_timestep is None:
            max_ts = self.simulation_timecourse['time'].max()
        else:
            max_ts = highest_timestep
        n_time_aggregates = (max_ts-lowest_timestep)/timesteps_per_aggregate
        Agent_Info = self.get_agent_info()
        Interaction_matrix = build_interaction_matrix(
            self, lowest_timestep=lowest_timestep, highest_timestep=highest_timestep, timesteps_per_aggregate=timesteps_per_aggregate)
        Interaction_HeatmapDF = build_agegroup_aggregated_interaction_matrix(
            Interaction_matrix, Agent_Info, n_time_aggregates=n_time_aggregates, age_groups=age_groups)
        return(Interaction_HeatmapDF)

    def get_age_group_specific_infection_patterns(self, lowest_timestep=0, highest_timestep=None, timesteps_per_aggregate=24, age_groups=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]):
        if highest_timestep is None:
            max_ts = self.simulation_timecourse['time'].max()
        else:
            max_ts = highest_timestep
        n_time_aggregates = (max_ts-lowest_timestep)/timesteps_per_aggregate
        Agent_Info = self.get_agent_info()
        Infection_matrix = build_infection_matrix(
            self, lowest_timestep=lowest_timestep, highest_timestep=highest_timestep, timesteps_per_aggregate=timesteps_per_aggregate)
        Infection_HeatmapDF = build_agegroup_aggregated_infection_matrix(
            Infection_matrix, Agent_Info, n_time_aggregates=n_time_aggregates, age_groups=age_groups)
        return(Infection_HeatmapDF)

    def get_infections_per_location_type_over_time(self):
        """
        export data frame of cummulative infection events per location
        :return pandas.DataFrame
        """
        infection_events = self.simulation_timecourse[self.simulation_timecourse['Infection_event'] != -1].copy(
        )
        infection_events.drop(columns=['status', 'h_ID', 'Temporary_Flags', 'Cumulative_Flags',
                                       'Interaction_partner'], axis=1, inplace=True)
        infection_locations = list(infection_events['loc'].values)
        location_types = {l.ID: l.location_type for l in self.locations.values()
                          if l.ID in infection_locations}

        infection_events.reset_index()
        infection_events.loc[:, 'loc_type'] = [location_types[x]
                                               for x in list(infection_events['loc'].values)]
        df = infection_events.groupby(by=['time', 'loc_type']).count().reset_index()
        df.drop('loc', axis=1, inplace=True)
        df.columns = ['time', 'loc_type', 'number_of_infection_events']

        return(df)

    def get_interaction_timecourse(self, diagnosed_contact=False):
        """
        : return pivot table
        """
        df = self.simulation_timecourse

        if not diagnosed_contact:
            df_p = df
        else:
            # timecourse dataframe only for diagnosed (acitve partner)
            df_diag = df[(df['Temporary_Flags'].isin([2, 3, 4]))]
            human_diagnosed = df_diag['h_ID'].unique()
            df_diag_contact = df[(df['h_ID'].isin(human_diagnosed))]  # all tracable contacts
            df_p = df_diag_contact
        # count events
        df_pivot = pd.pivot_table(df_p, values='h_ID', index=['time'], columns=[
                                  'Infection_event'], aggfunc='count')
        return df_pivot

    def get_r_eff_timecourse(self, sliding_window_size, sliding_step_size=1):
        return vpm_neta.get_r_eff_timecourse_from_human_timecourse(self, sliding_window_size, sliding_step_size=1)

    def export_time_courses_as_csvs(self, identifier="output"):
        """
        export the human simulation time course, human commutative status time course, and locations time course
        :param identifier: a given identifying name for the file which will be included in the name of the exported file
        """
        stati_list = self.statuses_in_timecourse
        df = self.simulation_timecourse.copy()
        for i in range(len(stati_list)):
            df.loc[self.simulation_timecourse['status'] == i, 'status'] = stati_list[i]

        df.set_index('time').to_csv(
            'outputs/' + identifier + '-humans_time_course.csv')
        statuses_trajectories = self.get_status_trajectories().values()
        dfs = [df.set_index('time') for df in statuses_trajectories]
        concat_trajectory_df = pd.concat(dfs, axis=1)
        concat_trajectory_df.to_csv('outputs/' + identifier + '-commutative_status_time_course.csv')
        locations_traj = self.get_location_with_type_trajectory()
        locations_traj.set_index('time').to_csv(
            'outputs/' + identifier + '-locations_time_course.csv')

    def export_r_eff_time_course_as_csv(self, sliding_window_size, sliding_step_size=1, saved_csv_identifier='unnamed_output'):
        vpm_neta.export_r_eff_timecourse_as_csv(
            self, sliding_window_size, sliding_step_size=1, saved_csv_identifier=saved_csv_identifier)

    def plot_infections_per_location_type(self, relative_to_building_number=True, save_figure=False):
        ax, loc_dict_inf = vpm_plt.plot_infections_per_location_type(
            self, save_figure=save_figure, relative_to_building_number=relative_to_building_number)
        return ax, loc_dict_inf

    def plot_status_timecourse(self, specific_statuses=None, specific_people=None, save_figure=False):
        """
        plots the time course for selected statuses
        :param simulation_object: obj of Simulation Class
        :param save_figure:  Bool. Flag for saving the figure as an image
        :param specific_statuses:   List. Optional arg for getting only a
        subset  of statuses. if not specified, will plot all available statuses
        """
        vpm_plt.plot_status_timecourse(self, specific_statuses, specific_people, save_figure)

    def plot_flags_timecourse(self, specific_flags=None, save_figure=False):
        """
        plots the time course for the selected flags
        :param specific_flags: list. given flags to be included in the plot
        :param save_figure: bool. Flag for saving the figure as an image
        """
        vpm_plt.plot_flags_timecourse(self, specific_flags, save_figure)

    def plot_location_type_occupancy_timecourse(self, specific_types=None, save_figure=False):
        """
        plots the occupancy of the location types in the time course
        :param specific_types: list. List of specific types to plot (only)
        :param save_figure: bool. Whether to save the figure
        """
        vpm_plt.plot_location_type_occupancy_timecourse(self, specific_types, save_figure)

    def plot_status_at_location(self, save_figure=False):
        """
        plots the occupancy of each status type at the different location types from the time course

        """
        vpm_plt.plot_status_at_location(self, save_figure=save_figure)

    def map_status_at_loc(self, save_figure=False, time_steps=2):
        """
        map the occupancy of each status type at the different location types from the time course

        """
        vpm_plt.map_status_at_loc(self, save_figure=save_figure, time_steps=time_steps)

    def plot_distributions_of_durations(self, save_figure=False):
        """
        plots the distributions of the total duration of the infection,
        the time from infection to hospitalization,
        the times from hospitalization to death or recovery
        and the time from hospitalisation to ICU.
        :param save_figure:  Bool. Flag for saving the figure as an image
        """
        vpm_plt.plot_distributions_of_durations(self, save_figure)

    def plot_infections_per_location_type_over_time(self, save_figure=False):
        vpm_plt.plot_infections_per_location_type_over_time(self, save_figure)

    def plot_age_groups_status_timecourse(self, age_groups_step=10, save_figure=False):
        vpm_plt.plot_age_groups_status_timecourse(
            self, age_groups_step=age_groups_step, save_figure=save_figure)

    def plot_interaction_timecourse(self, save_figure=False, log=False, diagnosed_contact=False):
        vpm_plt.plot_interaction_timecourse(
            self, save_figure=save_figure, log=log, diagnosed_contact=diagnosed_contact)

    def plot_interaction_patterns(self, lowest_timestep=0, highest_timestep=None, timesteps_per_aggregate=24, age_groups=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95], save_figure=False):
        vpm_plt.plot_interaction_patterns(self, lowest_timestep=lowest_timestep, highest_timestep=highest_timestep,
                                          timesteps_per_aggregate=timesteps_per_aggregate, age_groups=age_groups, save_figure=save_figure)

    def plot_infection_patterns(self, lowest_timestep=0, highest_timestep=None, timesteps_per_aggregate=24, age_groups=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95], save_figure=False):
        vpm_plt.plot_infection_patterns(self, lowest_timestep=lowest_timestep, highest_timestep=highest_timestep,
                                        timesteps_per_aggregate=timesteps_per_aggregate, age_groups=age_groups, save_figure=save_figure)


def build_infection_matrix(simulation, lowest_timestep=0, highest_timestep=None, timesteps_per_aggregate=24):
    if highest_timestep is None:
        max_ts = simulation.simulation_timecourse['time'].max()
    else:
        max_ts = highest_timestep
    Timecourse = simulation.simulation_timecourse[(simulation.simulation_timecourse['time'] >= lowest_timestep) & (
        simulation.simulation_timecourse['time'] <= max_ts)]

    Infections = Timecourse.loc[Timecourse['Infection_event'] >= 0, :]
    Days = [int(i/timesteps_per_aggregate) for i in Infections['time']]
    Infections['aggregated_time'] = Days
    individuals = list(Timecourse['h_ID'].unique())
    # out={}
    infection_matrix = numpy.zeros((len(individuals), len(individuals)))
    for d in list(Infections['aggregated_time'].unique()):
        DayFrame = Infections.loc[Infections['aggregated_time'] == d, ]
        did_infect_array = numpy.zeros((len(individuals), len(individuals)))
        for i in list(DayFrame.index):
            if DayFrame.loc[i, 'h_ID'] in individuals:
                if DayFrame.loc[i, 'Infection_event'] in individuals:
                    did_infect_array[individuals.index(DayFrame.loc[i, 'h_ID']), individuals.index(
                        DayFrame.loc[i, 'Infection_event'])] = 1
        infection_matrix += did_infect_array
    # cols=spreaders rows=receivers
    return(pd.DataFrame(infection_matrix, index=individuals, columns=individuals))


def build_agegroup_aggregated_infection_matrix(Infection_matrix, Agent_Info, n_time_aggregates=5, age_groups=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]):
    Agent_Info['AgeGroup'] = [-1]*Agent_Info.shape[0]
    for i in age_groups:
        age_index = age_groups.index(i)
        if age_groups.index(i) < len(age_groups)-1:
            lower_bound = i
            upper_bound = age_groups[age_index+1]
            agent_ids = Agent_Info.loc[(Agent_Info['Age'] >= lower_bound)
                                       & (Agent_Info['Age'] < upper_bound), 'ID']
            Agent_Info.loc[Agent_Info['ID'].isin(agent_ids), 'AgeGroup'] = int(i)
        else:
            lower_bound = i
            agent_ids = Agent_Info.loc[Agent_Info['Age'] >= lower_bound, 'ID']
            Agent_Info.loc[Agent_Info['ID'].isin(agent_ids), 'AgeGroup'] = int(i)

    Infection_matrix['AgeGroup_object'] = [-1]*Infection_matrix.shape[0]
    for i in list(Infection_matrix.index):
        agePerson = Agent_Info.loc[Agent_Info['ID'] == i, 'AgeGroup'].values[0]
        Infection_matrix.loc[i, 'AgeGroup_object'] = agePerson
    CMgroup = Infection_matrix.groupby(['AgeGroup_object']).sum()
    CMgroup.loc['AgeGroup_subject', :] = [-1]*CMgroup.shape[1]

    for i in list(CMgroup.columns):
        agePerson = Agent_Info.loc[Agent_Info['ID'] == int(i), 'AgeGroup'].values[0]
        CMgroup.loc['AgeGroup_subject', i] = agePerson
    Out = CMgroup.transpose().groupby(['AgeGroup_subject']).sum()
    perday = Out/n_time_aggregates
    perday.index = age_groups
    perday.columns = age_groups
    return(perday)

def build_interaction_matrix(simulation, lowest_timestep=0, highest_timestep=None, timesteps_per_aggregate=24):
    if highest_timestep is None:
        max_ts = simulation.simulation_timecourse['time'].max()
    else:
        max_ts = highest_timestep
    Timecourse = simulation.simulation_timecourse[(simulation.simulation_timecourse['time'] >= lowest_timestep) & (
        simulation.simulation_timecourse['time'] <= max_ts)]
    # Infections=Timecourse.loc[Timecourse['Infection_event']>=0,:]
    Interactions = Timecourse.loc[Timecourse['Interaction_partner'] != '', :].copy()
    Days = [int(i/timesteps_per_aggregate) for i in Interactions['time']]
    Interactions.loc[:,'aggregated_time'] = Days
    individuals = [int(i) for i in list(Timecourse['h_ID'].unique())]
    individual_dict = dict(zip(individuals, list(range(len(individuals)))))
    # out={}
    interaction_matrix = sparse.csr_matrix(numpy.zeros((len(individuals), len(individuals))))
    for d in list(Interactions['aggregated_time'].unique()):
        DayFrame = Interactions[Interactions['aggregated_time'] == d]
        #person_indices,contact_indices=zip(*[(individual_dict[int(DayFrame.loc[i,'h_ID'])],individual_dict[int(k)]) for j in [DayFrame.loc[i,'Interaction_partner'].split(',') for i in DayFrame.index] for k in j])
        contact_indices = [individual_dict[int(j)] for i in list(
            DayFrame['Interaction_partner']) for j in i.split(',')]
        #contact_indices=[individuals.index(int(j)) for i in list(DayFrame.index) for j in DayFrame.loc[i,'Interaction_partner'].split(',')]
        person_indices = [individual_dict[int(i)] for i in list(DayFrame['h_ID'])]
        person_indices = []
        for i in DayFrame.index:
            appendix_list = [individual_dict[int(DayFrame.loc[i, 'h_ID'])]] * \
                len(DayFrame.loc[i, 'Interaction_partner'].split(','))
            person_indices += appendix_list
        # person_indices=[for j in [[individual_dict[int(DayFrame.loc[i,'h_ID'])]]*len(DayFrame.loc[i,'Interaction_partner'].split(',')) for i in DayFrame.index] for k in j]
        #person_indices=[individuals.index(DayFrame.loc[i,'h_ID']) for i in list(DayFrame.index)]
        interaction_matrix[contact_indices, person_indices] += 1
    # cols=subject rows=object
    return(pd.DataFrame(interaction_matrix.toarray(), index=individuals, columns=individuals))

def build_agegroup_aggregated_interaction_matrix(Interaction_matrix, Agent_Info, n_time_aggregates=5, age_groups=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]):
    Agent_Info['AgeGroup'] = [-1]*Agent_Info.shape[0]
    for i in age_groups:
        age_index = age_groups.index(i)
        if age_groups.index(i) < len(age_groups)-1:
            lower_bound = i
            upper_bound = age_groups[age_index+1]
            agent_ids = Agent_Info.loc[(Agent_Info['Age'] >= lower_bound)
                                       & (Agent_Info['Age'] < upper_bound), 'ID']
            Agent_Info.loc[Agent_Info['ID'].isin(agent_ids), 'AgeGroup'] = int(i)
        else:
            lower_bound = i
            agent_ids = Agent_Info.loc[Agent_Info['Age'] >= lower_bound, 'ID']
            Agent_Info.loc[Agent_Info['ID'].isin(agent_ids), 'AgeGroup'] = int(i)

    Interaction_matrix['AgeGroup_subject'] = [-1]*Interaction_matrix.shape[0]
    for i in list(Interaction_matrix.index):
        agePerson = Agent_Info.loc[Agent_Info['ID'] == i, 'AgeGroup'].values[0]
        Interaction_matrix.loc[i, 'AgeGroup_subject'] = agePerson
    CMgroup = Interaction_matrix.groupby(['AgeGroup_subject']).mean()

    CMgroup.loc['AgeGroup_object', :] = [-1]*CMgroup.shape[1]
    for i in list(CMgroup.columns):
        agePerson = Agent_Info.loc[Agent_Info['ID'] == int(i), 'AgeGroup'].values[0]
        CMgroup.loc['AgeGroup_object', i] = agePerson
    Out = CMgroup.transpose().groupby(['AgeGroup_object']).sum()
    perday = Out/n_time_aggregates
    perday.index = age_groups
    perday.columns = age_groups
    return(perday)

def plot_r_eff(self, sliding_window_size, sliding_step_size=1, save_fig=False):
    vpm_neta.plot_r_eff_from_csvs_or_sim_object(
        self, from_sim_obj_sliding_window_size=sliding_window_size,
        from_sim_obj_sliding_step_size=sliding_step_size, save_fig=save_fig)

def trace_contacts_with_loctime(person, time_course, t_diagnosis, t_tracing_period_start):
    t_diag = t_diagnosis[person]
    resp_Timesteps = time_course.loc[(time_course['h_ID'] == person) & (
        time_course['time'] <= t_diagnosis[person]) & (time_course['time'] >= t_tracing_period_start[person])]
    contacts = list(
        resp_Timesteps.loc[resp_Timesteps['Interaction_partner'] != '', 'Interaction_partner'])
    #contact_number = list(set(','.join(contacts).split(',')))
    time_places = list(zip(list(resp_Timesteps['time']), list(resp_Timesteps['loc'])))
    # time_place_overlap_ids = [j for i in time_places for j in list(
    #    set(time_course.loc[(time_course['time'] == i[0]) & (time_course['loc'] == i[1]), 'h_ID']))]
    time_place_overlap_ids = []
    for i in time_places:
        time_place_overlap_ids += list(
            set(time_course.loc[(time_course['time'] == i[0]) & (time_course['loc'] == i[1]), 'h_ID']))
    number_time_loc_overlap = len(list(set(time_place_overlap_ids)))
    return((list(set(','.join(contacts).split(','))), number_time_loc_overlap))

def trace_contacts(person, time_course, t_diagnosis, t_tracing_period_start):
    t_diag = t_diagnosis[person]
    resp_Timesteps = time_course.loc[(time_course['h_ID'] == person) & (
        time_course['time'] <= t_diagnosis[person]) & (time_course['time'] >= t_tracing_period_start[person])]
    contacts = list(
        resp_Timesteps.loc[resp_Timesteps['Interaction_partner'] != '', 'Interaction_partner'])
    return(list(set(','.join(contacts).split(','))))
    #contact_number = len(list(set(','.join(contacts).split(','))))
    # return(contact_number)
