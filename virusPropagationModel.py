from human import *
from location import *
from age_initialisation import random_age
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
        free_homes=[h for h in self.locations.values() if (h.location_type=='home' and len(h.people_present)<6)]
        people = set()
        for n in range(number_of_people):
            age = random_age()
            home = random.sample(free_homes,1)[0]
            schedule = self.create_schedule(age, home)
            people.add(Human(n, age, schedule, home))
        return people

    def create_schedule(self, age, home):
        
        if age < 18:    ## underage
            home_time = npr.randint(17,22)  ## draw when to be back home from 17 to 22
            times = [8,15,home_time]    ## school is from 8 to 15, from 15 on there is public time
            school_id = home.closest_loc('school')[0]   ## go to closest school
            public_id = random.sample(home.closest_loc('public_place')[:2],1)[0]    ## draw public place from 2 closest
            locs = [self.locations[school_id],self.locations[public_id],home]
        elif age < 70:      ## working adult
            worktime = npr.randint(7,12)    ## draw time between 7 and 12 to beginn work
            public_duration = npr.randint(1,3)  ## draw duration of stay at public place
            times = [worktime, worktime+8, worktime+8+public_duration]
            work_id = random.sample(home.closest_loc('work')[:3],1)[0] ## draw workplace from the 3 closest
            public_id = random.sample(home.closest_loc('public_place')[:3],1)[0]    ## draw public place from 3 closest
            locs = [self.locations[work_id],self.locations[public_id],home]
        else:   ## senior, only goes to one public place each day
            public_time = npr.randint(7,17)
            public_duration = npr.randint(1,5)
            times = [public_time, public_time+public_duration]
            public_id = home.closest_loc('public_place')[0]
            locs = [self.locations[public_id],home]

        return {'times':times,'locs':locs}

    def infect(self, amount):
        to_infect = random.sample(self.people, amount)  # randomly choose who to infect
        for p in to_infect:
            #p.status = 'I'
            p.get_infected(1.0, 0)


class Simulation(object):
    def __init__(self, modeled_populated_world, time_steps):
        self.modeled_populated_world = modeled_populated_world
        self.time = 0
        # [{'h_ID': self.ID, 'loc': self.loc.ID, 'status': self.status, 'time': time}]
        self.timecourse = []
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

    def get_status_trajectories(self, specific_statuses=None):
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

        status_trajectories = {}
        for status in statuses:
            status_trajectories[status] = [(t, len(self.simulation_timecourse[(self.simulation_timecourse['time'] == t)
                                                                              & (self.simulation_timecourse[
                                                                                 'status'] == status)]))
                                           for t in self.simulation_timecourse['time'].unique()]
            status_trajectories[status] = pd.DataFrame(
                status_trajectories[status], columns=['time', status])
        return status_trajectories

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

        trajectories = self.get_status_trajectories(specific_statuses)
        assert set(labels.keys()) >= set(trajectories.keys()), "label(s) missing for existing statuses in the time " \
                                                               "course "
        simulation_timepoints = trajectories[list(trajectories.keys())[0]]['time'].values

        for status in trajectories.keys():
            plt.plot(simulation_timepoints,
                     trajectories[status][status].values, label=labels[status])

        plt.title('SecondPlot CoronaABM')
        plt.legend()
        plt.show()
        if save_figure:
            plt.savefig('output_plot.png')

# todo: plot location ID/type cummulative timecourses for ticket #33
