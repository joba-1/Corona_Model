#!/usr/bin/python
"""
This class defines the a human agent to be used in a (Corona) Virus infection model.
It defines the agents properties and the transitions between different stati.
created April, 2nd, 2020 - 
(c) Judith Wodke, PLEASE ADD YOUR NAME IF CONTRIBUTING!
"""

## import required libraries
import numpy.random as npr ## numpy.random for generating random numbers
import logging as log ## logging for allowing to keep track of code development and putative errors
import sys ## sys 

## define the human agent class
class human(object):
	def __init__(self, status='safe', subgroup='none', mitig=1, k_s=1):
		## define lists of possible statii and status transitions
		self.statii_list = ['safe', 'exposed', 'infected', 'recovered', 'hospitalized', 'ICU', 'dead']
		self.transitions_list['GetExposed', 'BecomeInfected', 'RecoverFromVirus', 'GetHospitalized', 'AddIntensiveCare', 'SubIntensiveCare', 'Die']
		## list of upper age group limits: please add/change numbers to vary age groups
		self.ageGroups_upperThresholds_list = [10,20,30,40,50,60,70,80,90,100]

		## initialize properties
		self.__status = status ## all humans are initialized as 'safe', except for a number of infected defined by the simulation parameters
		self.__age = npr.randint(0,100) ## if we get an age distribution, we should sample the age from that distribution
## NOTE: not sure, but maybe the age distribution should also be a simulation parameter given for initialization of a human
		self.__populationSubgroup = subgroup ## to account for medical personel, public transport workers, etc.
		## extract respective ageGroup from ageGroups_upperThresholds_list
		self.__ageGroup = 0
		t_passed = 0
		for t_age in self.ageGroups_upperThresholds_list:
			if t_age > self.__age:
				self.__ageGroup = t_passed
			else:
				t_passed = t_age
		if t_passed == 100:
			self.__ageGroup = 100
		self.__exposureProbability = 1*mitig*k_s
##NOTE: we have to think about where to add additional information about age-dependent transition parameters, mobility profiles, etc.

	## getter/setter for human properties
##NOTE: Do we want to use getter/setter?	
	@property
	def status(self):
	    return self.__status
	@protID.setter
	def status(self, newStat):
		if not isinstance(newStat, str):
			raise TypeError('The status must be a string.')
		elif newStat not in self.statii_list:
			raise ValueError('The status must be listed in self.statii_list, ' + newStat + ' is not.')
	
		
	## status transitions humans can undergo
	"""
	GetExposed
	"""
	def GetExposed(self):
		if self.__status == 'safe':
			tmpProb = npr.random_sample()
			if tmpProb < self.__exposureProbability:
				self.__status = 'exposed'
				log.debug('status has changed to ' + str(self.__status))
		else:
			log.debug('wrong status ' + str(self.__status) + ' to get exposed.')
