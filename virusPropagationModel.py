#!/usr/bin/python
"""
This class defines the a human agent to be used in a (Corona) Virus infection model.
It defines the agents properties and the transitions between different stati.
created April, 2nd, 2020 - 
(c) Judith Wodke, PLEASE ADD YOUR NAME IF CONTRIBUTING!
"""

## import agent class
from human import *

## import required libraries
import numpy.random as npr ## numpy.random for generating random numbers
import logging as log ## logging for allowing to keep track of code development and putative errors
import sys ## sys 


class VirusPropagationModel(object):
	## define initial variables
	def __init__(self):
		self.ageDependentRates_dict = {}
		self.ageGroups_list = []
		self.populationSubgroups_list = []
		self.mitigationParams_list = []
		self.timeConstants_list = []

		self.__healthy_list = []
		self.__exposed_list = []
		self.__infected_list = []

		self.__populationSize = 1000
		self.__timesteps = 100
		self.__infectedAtT0 = 1


	## model functions
	"""
	InitializeModel initializes a number of human agents defined by population size and infected at t_0
	"""
	def InitializeModel(self, noSteps=100):
		NoHealthy = self.__populationSize - self.__infectedAtT0
		for num in range(self.__infectedAtT0):
			sick = human(status='infected')
			self.__infected_list.append(sick)
		for num in range(NoHealthy):
			healthy = human()
			self.__healthy_list.append(healthy)