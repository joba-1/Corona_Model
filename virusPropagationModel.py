from human import *
from location import *
from age_initialisation import random_age
from initialize_households import initialize_household
import random
import pandas as pd
import matplotlib.pyplot as plt


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

    # currently breaks when False
    def __init__(self, number_of_locs, initial_infections, world_from_file=False, agent_agent_infection=False):
        self.world_from_file = world_from_file
        self.agent_agent_infection = agent_agent_infection
        self.number_of_locs = number_of_locs
        self.initial_infections = initial_infections
        self.world = World(from_file=self.world_from_file, number_of_locs=self.number_of_locs)
        self.locations = self.world.locations
        #self.people = self.initialize_people(self.number_of_people)
        self.people = self.initialize_people(self.agent_agent_infection)
        self.initialize_infection(self.initial_infections)

    def initialize_people(self, agent_agent_infection):
        """
        initializes a set of people (human objects) with assigned ages and schedules
        :return people: set. a set of human objects
        """
        people = set()
        for home in [h for h in self.locations.values() if h.location_type == 'home']:
            home_type, home_size, ages = initialize_household()
            for age in ages:
                n = len(people)+1
                schedule = self.create_schedule(age, home, self.locations)
                people.add(Human(n, age, schedule, home, infection_interaction=agent_agent_infection))
        return people

    def create_schedule(self, age, home, locations):
        """
        creates a schedule, depending on a given age and locations
        :param age: int. given age for a human from whom this schedule should be
        :param locations: list of location objects to which the human can go
        :return sched: dict. specifies times of transitions and assigned locations
        """
        workplaces = [l.ID for l in self.locations.values() if l.location_type == 'work']
        public_places = [l.ID for l in self.locations.values() if l.location_type == 'public_place']
        schools = [l.ID for l in self.locations.values() if l.location_type == 'school']

        if age < 18:  # underage
            home_time = npr.randint(17, 22)  # draw when to be back home from 17 to 22
            times = [8, 15, home_time]  # school is from 8 to 15, from 15 on there is public time

            if home.closest_loc('school'):
                school_id = home.closest_loc('school')[0]  # go to closest school
            else:
                school_id = random.sample(schools, 1)[0]

            if home.closest_loc('public_place'):
                public_id = random.sample(home.closest_loc('public_place')[:2], 1)[
                    0]  # draw public place from 2 closest
            else:
                public_id = random.sample(public_places, 1)[0]

            locs = [self.locations[school_id], self.locations[public_id], home]

        elif age < 70:  # working adult
            worktime = npr.randint(7, 12)  # draw time between 7 and 12 to beginn work
            public_duration = npr.randint(1, 3)  # draw duration of stay at public place
            times = [worktime, worktime+8, worktime+8+public_duration]

            if home.closest_loc('work'):
                work_id = random.sample(home.closest_loc('work')[:3], 1)[
                    0]  # draw workplace from the 3 closest
            else:
                work_id = random.sample(workplaces, 1)[0]

            if home.closest_loc('public_place'):
                public_id = random.sample(home.closest_loc('public_place')[:3], 1)[
                    0]  # draw public place from 3 closest
            else:
                public_id = random.sample(public_places, 1)[0]

            locs = [self.locations[work_id], self.locations[public_id], home]

        else:  # senior, only goes to one public place each day
            public_time = npr.randint(7, 17)
            public_duration = npr.randint(1, 5)
            times = [public_time, public_time+public_duration]

            if home.closest_loc('public_place'):
                public_id = home.closest_loc('public_place')[0]  # draw public place from 3 closest
            else:
                public_id = random.sample(public_places, 1)[0]

            locs = [self.locations[public_id], home]

        return {'times': times, 'locs': locs}

    def initialize_infection(self, amount):
        """
        infects people (list of humans) initially
        :param amount: int. amount of people to initially infect
        """
        to_infect = random.sample(self.people, amount)  # randomly choose who to infect
        for p in to_infect:
            p.get_initially_infected()


class Simulation(object):
    """
    A Class which contains a simulated time course of a given ModeledPopulatedWorld object

    Attributes
    ----------
    modeled_populated_world : ModeledPopulatedWorld object
        the initialized populated world used as basis for the simulation
    time_steps : int
        The amount of time steps to simulate (hours)
    time: int
        the current in-silico time in the simulation in its current state
    statuses_in_timecourse: list
        a list of all the statuses available in the time course (e.g. I, for "infected")

    Methods
    ----------
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
                p.set_status_from_preliminary()
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
        loc_id_to_type_dict = {loc.get_location_id(): loc.get_location_type() for loc in
                               self.modeled_populated_world.locations.values()}
        location_traj_df = self.simulation_timecourse[{'h_ID', 'loc', 'time'}].copy()
        loc_type_traj = np.empty(len(location_traj_df.index), dtype=object)
        for i in range(len(loc_type_traj)):
            loc_type_traj[i] = loc_id_to_type_dict[location_traj_df['loc'][i]]

        location_traj_df['loc_type'] = loc_type_traj
        return location_traj_df

    def get_durations(self):
        """
        Returns a pandas DataFrame with the durations of certain states of the agents.
        Durations included so far (columns in the data-frame):
        From infection to death ('infection_to_death'),
        from infection to recovery ('infection_to_recovery'),
        from infection to hospital ('infection_to_hospital') and
        from hospital to ICU (hospital_to_icu).
        """
        df = pd.DataFrame()
        for p in self.modeled_populated_world.people:
            duration_dict = p.get_infection_info()
            if not pd.isna(duration_dict['infection_time']):
                if not pd.isna(duration_dict['recovery_time']):
                    df.loc[p.ID, 'infection_to_recovery'] = duration_dict['recovery_time'] - \
                        duration_dict['infection_time']
                elif not pd.isna(duration_dict['death_time']):
                    df.loc[p.ID, 'infection_to_death'] = duration_dict['death_time'] - \
                        duration_dict['infection_time']
                if not pd.isna(duration_dict['hospitalized_time']):
                    df.loc[p.ID, 'infection_to_hospital'] = duration_dict['hospitalized_time'] - \
                        duration_dict['infection_time']
                    if not pd.isna(duration_dict['hospital_to_ICU_time']):
                        df.loc[p.ID, 'hospital_to_icu'] = duration_dict['hospital_to_ICU_time'] - \
                            duration_dict['hospitalized_time']
        return(df)

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
            plt.savefig('outputs/status_plot.png')

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
            plt.savefig('outputs/flags_plot.png')

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
            zero_occupancy_array = df['time'].copy().unique()
            df_of_location = df[df['loc_type'] == loc_type].rename(columns={'loc_type': loc_type})
            time_grouped_location_count = df_of_location.groupby('time').count()
            zero_occupancy_df = pd.DataFrame({'time': zero_occupancy_array, loc_type: np.zeros(
                len(zero_occupancy_array))}).set_index('time')
            merged_df = time_grouped_location_count.merge(zero_occupancy_df, left_index=True, right_index=True,
                                                          suffixes=('', '_zeros'), how='right').fillna(0)
            plt.plot(list(merged_df.index.values), merged_df[loc_type], label=loc_type)
        plt.title('location occupancy trajectories')
        plt.legend()
        plt.show()
        if save_figure:
            plt.savefig('outputs/loc_types_occupancy_plot.png')

    def export_time_courses_as_csvs(self, identifier=""):
        self.simulation_timecourse.to_csv('outputs/'+identifier+'-humans_time_course.csv')
        statuses_trajectories = self.get_status_trajectories().values()
        dfs = [df.set_index('time') for df in statuses_trajectories]
        concat_trajectory_df = pd.concat(dfs, axis=1)
        concat_trajectory_df.to_csv('outputs/'+identifier+'-commutative_status_time_course.csv')
        locations_traj = self.get_location_with_type_trajectory()
        locations_traj.to_csv('outputs/' + identifier + '-locations_time_course.csv')
