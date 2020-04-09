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
from age_initialisation import random_age
## import required libraries
import numpy.random as npr ## numpy.random for generating random numbers
import random
import pandas as pd

class VirusPropagationModel(object):
	## define initial variables
	def __init__(self, number_of_locs, number_of_people, initial_infections):
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
		
	def simulate(self, timesteps):
		for t in range(timesteps):
			self.time+=1
			for p in self.people: # 
				p.update_status(self.time)
			for p in self.people: # don't call if hospitalized
				p.move(self.time)
				self.store_state(p)
		return pd.DataFrame(self.timecourse)


	#def init_world(self, number_of_locs):
	#	self.world = location.World(number_of_locs)

	#def initialize_locs(self, number_of_locs): # todo 
	#	locs = set()
	#	for n in range(number_of_locs):
	#		locs.add(Location(n, (0,0), 'dummy_loc'))
	#	return locs

	def initialize_people(self, number_of_people): # idee martin: skalenfeiheit
		people = set()
		for n in range(number_of_people):
			age = random_age()
			schedule = self.create_schedule(age, self.locations)
			people.add(Human(n, age, schedule, schedule['locs'][0]))
		return people

	def create_schedule(self, age, locations):
		if age > 3 and age < 70:	# schedule has to depend on age, this is only preliminary
			num_locs = 5
		else:
			num_locs = 3
		my_locs = random.sample(locations, num_locs) # draw random locations (preliminary) (random.sample() draws exclusively)
		my_times = random.sample(range(24), num_locs)
		my_times.sort()
		sched = {'times':my_times, 'locs':my_locs}
		return sched


	def infect(self, number):
		to_infect = random.sample(self.people, number) # randomly choose who to infect
		for p in to_infect:
			p.status = 'I'

	def store_state(self, person):
		stat = person.get_status()
		stat['time'] = self.time # 
		self.timecourse.append(stat)
		