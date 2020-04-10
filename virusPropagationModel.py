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


	def initialize_people(self, number_of_people): # idee martin: skalenfeiheit
		print(len([h for h in self.locations.values() if h.location_type=='home']))
		print(len([h for h in self.locations.values() if (h.location_type=='home' and len(h.people_present)<6)]))
		free_homes=[h for h in self.locations.values() if (h.location_type=='home' and len(h.people_present)<6)]
		people = set()
		for n in range(number_of_people):
			age = RandomAge()
			home = random.sample(free_homes,1)[0]
			schedule = self.create_schedule(age, home)
			people.add(Human(n, age, schedule, home))
		return people

	def create_schedule(self, age, home):
		
		if age < 18:	## underage
			home_time = npr.randint(17,22)	## draw when to be back home from 17 to 22
			times = [8,15,home_time]	## school is from 8 to 15, from 15 on there is public time
			school_id = home.closest_loc('school')[0]	## go to closest school
			public_id = random.sample(home.closest_loc('public_place')[:2],1)[0]	## draw public place from 2 closest
			locs = [self.locations[school_id],self.locations[public_id],home]
		elif age < 70:		## working adult
			worktime = npr.randint(7,12)	## draw time between 7 and 12 to beginn work
			public_duration = npr.randint(1,3)	## draw duration of stay at public place
			times = [worktime, worktime+8, worktime+8+public_duration]
			work_id = random.sample(home.closest_loc('work')[:3],1)[0] ## draw workplace from the 3 closest
			public_id = random.sample(home.closest_loc('public_place')[:3],1)[0]	## draw public place from 3 closest
			locs = [self.locations[work_id],self.locations[public_id],home]
		else:	## senior, only goes to one public place each day
			public_time = npr.randint(7,17)
			public_duration = npr.randint(1,5)
			times = [public_time, public_time+public_duration]
			public_id = home.closest_loc('public_place')[0]
			locs = [self.locations[public_id],home]

		return {'times':times,'locs':locs}

		'''
		if age > 3 and age < 70:	# schedule has to depend on age, this is only preliminary
			num_locs = 5
		else:
			num_locs = 3
		my_locs = random.sample(list(self.locations.values()), num_locs) # draw random locations (preliminary) (random.sample() draws exclusively)
		my_times = random.sample(range(24), num_locs)
		my_times.sort()
		sched = {'times':my_times, 'locs':my_locs}
		return sched
		'''
		


	def infect(self, number):
		to_infect = random.sample(self.people, number) # randomly choose who to infect
		for p in to_infect:
			p.status = 'I'

	def store_state(self, person):
		stat = person.get_status()
		stat['time'] = self.time # 
		self.timecourse.append(stat)
		