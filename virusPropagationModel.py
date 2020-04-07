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

## import required libraries
import numpy.random as npr ## numpy.random for generating random numbers
import random

class VirusPropagationModel(object):
	## define initial variables
	def __init__(self, number_of_locs, number_of_people, initial_infections):
		## initialize variables, lists, dictionaries depending on the input parameters
		self.locations = self.initialize_locs(number_of_locs)
		self.people = self.initialize_people(number_of_people)
		self.dead_people = set()
		self.time = 0
		self.timecourse = [] # [{'0':{'status':'S','loc_ID':1}, '1':{'status':'S','loc_ID':1}}]
		self.infect(initial_infections)

	def simulate(self, timesteps):
		for t in range(timesteps):
			new_deads = [v for v in self.people if v.status=='D'] # get list of newly dead people
			for p in new_deads:
				self.dead_people.add(p) # add them to set of dead people
				self.people.remove(p) # remove them from set of alive people
			self.time+=1
			for p in self.people:
				p.update_status(self.time)
			for p in self.people: # don't call if hospitalized
				p.move(self.time)
			self.store_state()

	def initialize_locs(self, number_of_locs):
		locs = set()
		for n in range(number_of_locs):
			locs.add(Location(n, (0,0), 'dummy_loc'))
		return locs

	def initialize_people(self, number_of_people): # idee martin: skalenfeiheit
		people = set()
		for n in range(number_of_people):
			age = npr.normal(30,20)
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

	def store_state(self):
		pass