#!/usr/bin/python
"""
This class defines the a human agent to be used in a (Corona) Virus infection model.
It defines the agents properties and the transitions between different stati.
created April, 2nd, 2020 - 
(c) Judith Wodke, Stephan O. Adler, PLEASE ADD YOUR NAME IF CONTRIBUTING!
"""

## import required libraries
import numpy.random as npr ## numpy.random for generating random numbers
import logging as log ## logging for allowing to keep track of code development and putative errors
import sys ## sys 
from location import *

## define the human agent class
class Human(object):
	def __init__(self, ID, age, schedule, loc, status='S'):
		## initialize properties
		self.ID = ID
		self.status = status ## all humans are initialized as 'safe', except for a number of infected defined by the simulation parameters
		self.age = age ## if we get an age distribution, we should sample the age from that distribution
		self.schedule = schedule # dict of times and locations
		self.loc = loc # current location
		self.personal_risk = self.get_personal_risk(age) # todesrisiko
		self.infection_time = 0
		loc.enter(self)

##NOTE: we have to think about where to add additional information about age-dependent transition parameters, mobility profiles, etc.

	def update_status(self, time): # this is not yet according to Eddas model
		if self.status == 'R':
			pass
		elif self.status == 'S':
			risk = self.loc.infection_risk()
			self.GetInfected(risk, time)
		elif self.status == 'I':
			self.Die()
			if self.status == 'I':
				recover_prob = self.get_recover_prob(time)
				self.Recover(recover_prob)
	
	def get_status(self): # 	for storing simulation data 		
		return {'h_ID': self.ID, 'loc': self.loc.ID, 'status': self.status}

	def move(self, time): # agent moves relative to global time
	# {'times':[0,10,16], 'locs':[<location1>,<location2>,<location3>]}
		if time%24 in self.schedule['times']: # here i check for a 24h cycling schedule
			self.loc.leave(self) # leave old location
			new_loc = self.schedule['locs'][self.schedule['times'].index(time%24)]
			self.loc = new_loc
			new_loc.enter(self) # enter new location
	
	def get_recover_prob(self, time): # this needs improvement and is preliminary
		prob = (time - self.infection_time)/480. # probabitily increases hourly over 20 days (my preliminary random choice)
		# am besten mit kummulativer gauss-verteilung
		return prob

	def get_personal_risk(self, age): # maybe there is data for that...
		if age < 60:
			risk = 0.001
		elif age < 75:
			risk = 0.005
		else:
			risk = 0.01
		return risk


	## status transitions humans can undergo
	"""
	GetExposed
	
	def GetExposed(self):
		if self.__status == 'safe':
			tmpProb = npr.random_sample()
			if tmpProb < self.__exposureProbability:
				self.__status = 'exposed'
				log.debug('status has changed to ' + str(self.__status))
		else:
			log.debug('wrong status ' + str(self.__status) + ' to get exposed.')
	"""

	def GetInfected(self, risk, time):
		if risk > npr.random_sample():
			self.status = 'I'
			self.infection_time = time

	def Recover(self, recover_prob):
		if recover_prob > npr.random_sample():
			self.status = 'R'

	def GetHospitalized(self):
		self.status = 'H'
		# set location to next hospital

	def Die(self):
		if self.personal_risk > npr.random_sample():
			self.status = 'D'
