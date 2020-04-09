#!/usr/bin/python
"""
This class defines the a human agent to be used in a (Corona) Virus infection model.
It defines the agents properties and the transitions between different statii.
Comments start with ## in order to distinguish them from outcommented code.
Created April, 2nd, 2020 - 
(c) Judith Wodke, Stephan O. Adler, PLEASE ADD YOUR NAME IF CONTRIBUTING!
"""

## import agent and parameter classes
from human import *
from location import *
#from parameters import * (to be written)
## import random age draw function
from age_initialisation import RandomAge
## import required libraries
import numpy.random as npr ## numpy.random for generating random numbers
import random
import pandas as pd

class VirusPropagationModel(object):
	## define initial variables
	def __init__(self, number_of_locs_int, number_of_people_int, initial_infections_int):
		## initialize variables, lists, dictionaries depending on the input parameters
		
		self.time = 0
		self.timecourse = [] # [{'h_ID': self.ID, 'loc': self.loc.ID, 'status': self.status, 'time': time}]
		self.world = World(number_of_locs)
		self.locations = self.world.locations
		#self.locations = self.initialize_locs(number_of_locs)
		self.people = self.initialize_people(number_of_people)
		self.infect(initial_infections)



	def reset_model(self): # todo set model to origin 
		pass	
		
	def Simulate(self, timesteps_int):
		for t in range(timesteps_int):
			self.time_int+=1
			for p in self.people_set: # 
				p.Update_status(self.time_int)
			for p in self.people_set: # don't call if hospitalized
				p.Move(self.time_int)
				self.Store_state(p)
		return pd.DataFrame(self.timecourse_list)


	#def init_world(self, number_of_locs):
	#	self.world = location.World(number_of_locs)

	#def initialize_locs(self, number_of_locs): # todo 
	#	locs = set()
	#	for n in range(number_of_locs):
	#		locs.add(Location(n, (0,0), 'dummy_loc'))
	#	return locs

	def Initialize_people(self, number_of_people_int): # idee martin: skalenfeiheit
		people_set = set()
		for n in range(number_of_people_int):
			age_int = RandomAge()
			schedule_dict = self.Create_schedule(age_int, self.locations_set)
			people_set.add(Human(n, age_int, schedule_dict, schedule_dict['locs'][0]))
		return people_set

	def Create_schedule(self, age_int, locations_set):
		if age_int > 3 and age_int < 70:	# schedule has to depend on age, this is only preliminary
			num_locs_int = 5
		else:
			num_locs_int = 3
		my_locs_list = random.sample(locations_set, num_locs_int) # draw random locations (preliminary) (random.sample() draws exclusively)
		my_times_list = random.sample(range(24), num_locs_int)
		my_times_list.sort()
		sched_dict = {'times':my_times_list, 'locs':my_locs_list}
		return sched_dict

	def Infect(self, number_int):
		to_infect_list = random.sample(self.people_set, number_int) # randomly choose who to infect
		for p in to_infect_list:
			p.status_str = 'I'

	def Store_state(self, person_hu):
		stat_dict = person_hu.Get_status()
		stat_dict['time'] = self.time_int # 
		self.timecourse_list.append(stat_dict)
		