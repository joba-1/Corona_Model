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
	def __init__(self, ID_int, age_int, schedule_dict, loc_loc, status_str='S'):
		## initialize properties
		self.ID_int = ID_int
		self.status_str = status_str ## all humans are initialized as 'safe', except for a number of infected defined by the simulation parameters
		self.age_int = age_int ## if we get an age distribution, we should sample the age from that distribution
		self.schedule_dict = schedule_dict # dict of times and locations
		self.loc_loc = loc_loc # current location
		self.personal_risk_float = self.Get_personal_risk(age_int) # todesrisiko
		self.infection_time_int = 0
		loc_loc.Enter(self)

##NOTE: we have to think about where to add additional information about age-dependent transition parameters, mobility profiles, etc.

	def Update_status(self, time_int): # this is not yet according to Eddas model
		if self.status_str == 'R':
			pass
		elif self.status_str == 'S':
			risk_float = self.loc_loc.Infection_risk()
			self.GetInfected(risk_float, time_int)
		elif self.status_str == 'I':
			self.Die()
			if self.status_str == 'I':
				recover_prob_float = self.Get_recover_prob(time_int)
				self.Recover(recover_prob_float)
	
	def Get_status(self): # 	for storing simulation data 		
		return {'h_ID': self.ID_int, 'loc': self.loc_loc.ID_int, 'status': self.status_str}

	def Move(self, time_int): # agent moves relative to global time
	# {'times':[0,10,16], 'locs':[<location1>,<location2>,<location3>]}
		if time_int%24 in self.schedule_dict['times']: # here i check for a 24h cycling schedule
			self.loc_loc.Leave(self) # leave old location
			new_loc_loc = self.schedule_dict['locs'][self.schedule_dict['times'].index(time_int%24)]
			self.loc_loc = new_loc_loc
			new_loc_loc.Enter(self) # enter new location
	
	def Get_recover_prob(self, time_int): # this needs improvement and is preliminary
		prob_float = (time_int - self.infection_time_int)/480. # probabitily increases hourly over 20 days (my preliminary random choice)
		# am besten mit kummulativer gauss-verteilung
		return prob_float

	def Get_personal_risk(self, age_int): # maybe there is data for that...
		if age_int < 60:
			risk_float = 0.001
		elif age_int < 75:
			risk_float = 0.005
		else:
			risk_float = 0.01
		return risk_float


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

	def GetInfected(self, risk_float, time_int):
		if risk_float > npr.random_sample():
			self.status_str = 'I'
			self.infection_time = time_int

	def Recover(self, recover_prob_float):
		if recover_prob_float > npr.random_sample():
			self.status_str = 'R'

	def GetHospitalized(self):
		self.status_str = 'H'
		# set location to next hospital

	def Die(self):
		if self.personal_risk_float > npr.random_sample():
			self.status_str = 'D'
