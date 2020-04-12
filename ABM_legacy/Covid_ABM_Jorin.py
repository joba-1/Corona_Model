# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 09:32:59 2020

@author: Jorin
"""
import warnings
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class population:
    """Class defining a population of a city. The actual initialization is done
    by the simulation class. """
    
    def __init__(self, S_array,I_array, R_array, age_array, gender_array, 
                 location_array, activity_array, mask_array):
        self.S = S_array  # Susceptible
        self.I = I_array  # Infected
        self.R = R_array  # Recovered
        self.age = age_array  # Age
        self.gender = gender_array  # Gender
        self.location = location_array  # Location, such as City1, City2
        self.activity = activity_array  # Activity, such as work, home etc..
        self.mask = mask_array  # bool if person has mask
    
    def __add__(self, other):
        """Adding function for populations. Adds other population to self population."""
        self.S = np.hstack((self.S, other.S))
        self.I = np.hstack((self.I, other.I))
        self.R = np.hstack((self.R, other.R))
        self.age = np.hstack((self.age, other.age))
        self.gender = np.hstack((self.gender, other.gender))
        self.location = np.hstack((self.location, other.location))
        self.activity = np.hstack((self.activity, other.activity))
        self.mask = np.hstack((self.mask, other.mask))
        

class simulation:
    """Class to run simulation and save results."""
    
    def __init__(self, info_pd):
        self.info_df = info_pd  # pandas dataframe with cities as rows
        self.pop = None # place to store entire population
        self.initialize_humans()  # initialized human population based on info_df
        # Result storing units
        self.time_list = [] 
        self.S_list = []
        self.I_list = []
        self.R_list = []
        self.city_tracker = {}
        
        
    def initialize_humans(self):
        """Initializes population(s). """
        for i in self.info_df.index:
            row = self.info_df.loc[i]  # gets all information on city in row i
            pop_dict = {'S_array': np.array([True]*row.n),  # initially all people are susceptible
                        'I_array': np.array([False]*row.n),  
                        'R_array': np.array([False]*row.n),
                        'age_array': np.random.choice(row.age_list, size=row.n),  # TODO: this has to be done better
                        'gender_array': np.random.choice(['f', 'm'], size=row.n,  # Q: Gender specific age distribution?
                                                   p=[row.female_ratio,
                                                         1-row.female_ratio]),
                        'location_array': np.array([row.city_name]*row.n), 
                        'activity_array': np.random.choice(['work', 'home'], size=row.n, # Also this should depent on age 
                                                   p=[row.employment_rate,
                                                         1-row.employment_rate]),
                        'mask_array': np.random.choice([True, False], size=row.n,  # Array defining if person has mask or not
                                                       p=[row.mask_prop,
                                                          1 - row.mask_prop])}
            current_pop = population(**pop_dict)
            if self.pop is None:
                self.pop = current_pop  # first populaiton is set to simulations population
            else:
                _ = self.pop + current_pop  # other populations are added to this. FIXME: This is really dirty making use of mutability
    
    def init_infect(self, n_infect=1):
        """Randomly infect n_infect person(s)"""
        infect_people = np.random.randint(0, len(self.pop.S), n_infect)
        self.pop.S[infect_people] = False
        self.pop.I[infect_people] = True
        
        
    def get_infection_density(self):
        """Return number of infected people to number of people who are alive per location/city."""
        infection_densities = np.array([])
        for city in self.info_df['city_name'].values:
            indeces = np.where(self.pop.location == city)
            mask_and_in_town = np.where((self.pop.mask == True) % (self.pop.location == city))  # FIXME: This sometimes raises a division by zero warning, which it shouldn't check why
            living_pop = self.pop.S[indeces].sum() + self.pop.I[indeces].sum() + self.pop.R[indeces].sum() 
            infected_pop = self.pop.I[indeces].sum()
            infected_people_with_mask = self.pop.I[mask_and_in_town].sum()
            if infected_pop != 0:
                ratio_infected_people_with_mask = 1 - 0.9 * (infected_people_with_mask / infected_pop) # infected people wearing masks reduce infection density
            else:
                ratio_infected_people_with_mask = 1
            infection_density = np.ones(len(self.pop.S[indeces])) * infected_pop / living_pop *  ratio_infected_people_with_mask#np.array([infected_pop / living_pop] * len(self.pop.S[indeces]))
            infection_densities = np.hstack((infection_densities, infection_density))
        return infection_densities
        
    def define_infection_propabality(self):
        """Defines infection probability for each person. Depending on age, city, etc."""  # etc has to be added
        inf_dens = self.get_infection_density()
        probability = inf_dens * self.pop.age / (self.pop.age.max()) 
        probability[self.pop.mask] = probability[self.pop.mask] * 0.9  # wearing a mask slighty reduces infection probability
        probability[self.pop.I] = 0  # Infected can't be infected
        probability[self.pop.R] = 0  # Recovred can't be infected
        return probability
    
    def define_recover_probability(self):
        """Defines recovery probability for each person. Depending on age, etc."""  # etc has to be added
        probability = 0.1 * (self.pop.age.max() - self.pop.age) / self.pop.age.max()
        probability[self.pop.S] = 0  # Susceptibel can't recover
        probability[self.pop.R] = 0  # Recovered people can't recover
        return probability
    
    def infect(self):
        """Infects people based on there infection probability."""
        infection_prop = self.define_infection_propabality()
        uniform_draw = np.random.uniform(size=infection_prop.size)
        infect_array = infection_prop > uniform_draw  # positions where infection takes place
        self.pop.S[infect_array] = False
        self.pop.I[infect_array] = True
        
        
    def recover(self):
        """Recovers people based on recovery probabilities."""
        recover_prop = self.define_recover_probability()
        uniform_draw = np.random.uniform(size=recover_prop.size)
        recover_array = recover_prop > uniform_draw  # positions where recovery takes place
        self.pop.I[recover_array] = False
        self.pop.R[recover_array] = True
        
            
    def simulate_time_step(self):
        """Simulation of one time step."""
        self.infect()
        self.recover()
        
    
    def simulate_time_course(self, t_array):
        """Simulates time course."""
        # Setup of location/city tracker dict
        for i in self.info_df.index:
            row = self.info_df.loc[i]
            self.city_tracker[row.city_name] = {}
            self.city_tracker[row.city_name]['S_list'] = []
            self.city_tracker[row.city_name]['I_list'] = []
            self.city_tracker[row.city_name]['R_list'] = []
        
        for t in t_array: 
            # save timepoints before simulation step TODO: write save_timepoint function
            self.time_list.append(t)
            self.S_list.append(self.pop.S.sum())
            self.I_list.append(self.pop.I.sum())
            self.R_list.append(self.pop.R.sum())
            for i in self.info_df.index:
                row = self.info_df.loc[i]
                S_in_city = self.pop.S[self.pop.location == row.city_name]
                I_in_city = self.pop.I[self.pop.location == row.city_name]
                R_in_city = self.pop.R[self.pop.location == row.city_name]
                self.city_tracker[row.city_name]['S_list'].append(S_in_city.sum())
                self.city_tracker[row.city_name]['I_list'].append(I_in_city.sum())
                self.city_tracker[row.city_name]['R_list'].append(R_in_city.sum())
            self.simulate_time_step()  # Simulates time step
        
        # save last timepoint        
        self.time_list.append(t)
        self.S_list.append(self.pop.S.sum())
        self.I_list.append(self.pop.I.sum())
        self.R_list.append(self.pop.R.sum())
        for i in self.info_df.index:
            row = self.info_df.loc[i]
            S_in_city = self.pop.S[self.pop.location == row.city_name]
            I_in_city = self.pop.I[self.pop.location == row.city_name]
            R_in_city = self.pop.R[self.pop.location == row.city_name]
            self.city_tracker[row.city_name]['S_list'].append(S_in_city.sum())
            self.city_tracker[row.city_name]['I_list'].append(I_in_city.sum())
            self.city_tracker[row.city_name]['R_list'].append(R_in_city.sum())
        

       
if __name__=='__main__':
    warnings.filterwarnings('default')
    # minimal example of cities df
    # Maybe better have a dict with a df for each city, which holds specific data for each person.
    cities_pd = pd.DataFrame([['Town', 10, 0.1, 10,  abs(np.random.normal(30, 20, size=100)), int(1e4), 0, 0.51, 0.9],
                              ['City', 500, 1, 1000, abs(np.random.normal(70, 20, size=100)), int(1.2e4), 0.1, 0.55, 0.8],
                              ['Metropole', 500, 1, 1000, abs(np.random.normal(50, 20, size=100)), int(1.5e4), 0.8, 0.55, 0.8]],
                                columns=['city_name', 'size', 
                              'density', 'population', 'age_list', 'n', 'mask_prop', 'female_ratio', 'employment_rate'])
    a = time.time()
    sim = simulation(cities_pd)
    sim.init_infect(10)  # Randomly infects 5 people 
    sim.simulate_time_course(np.arange(0, 100))  # simulates given time
    b = time.time()
    sim_time = b - a
    print(f'Simulation Time: {round(sim_time, 4)} seconds.')    
    
    # Quick and dirty visualization 
    fig, ax = plt.subplots()
    ax.plot(sim.time_list, sim.S_list, label='S', color='b')
    ax.plot(sim.time_list, sim.I_list, label='I', color='r')
    ax.plot(sim.time_list, sim.R_list, label='R', color='g')
    for i, city in enumerate(sim.city_tracker.keys()):
            ax.plot(sim.time_list, sim.city_tracker[city]['S_list'], label=f'S_{city}', color='b', alpha=0.7 - 0.2 * i)
            ax.plot(sim.time_list, sim.city_tracker[city]['I_list'], label=f'I_{city}', color='r', alpha=0.7 - 0.2 * i)
            ax.plot(sim.time_list, sim.city_tracker[city]['R_list'], label=f'R_{city}', color='g', alpha=0.7 - 0.2 * i)
    ax.legend()
    #fig.savefig('./test.pdf', format='pdf')
    plt.show()
    
    
    
    