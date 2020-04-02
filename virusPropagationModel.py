#!/usr/bin/python
"""
This class defines the a human agent to be used in a (Corona) Virus infection model.
It defines the agents properties and the transitions between different statii.
Comments start with ## in order to distinguish them from outcommented code.
Created April, 2nd, 2020 - 
(c) Judith Wodke, PLEASE ADD YOUR NAME IF CONTRIBUTING!
"""

## import agent and parameter classes
from human import *
#from parameters import * (to be written)

## import required libraries
import numpy.random as npr ## numpy.random for generating random numbers
import logging as log ## logging for allowing to keep track of code development and putative errors
import sys ## sys 


class VirusPropagationModel(object):
	## define initial variables
	def __init__(self, listOfParameters):
		## initialize variables, lists, dictionaries depending on the input parameters
		self.ageGroups_list = []
		self.ageDependentRates_dict = {}
		self.populationSubgroups_list = []
		self.mitigationParams_list = []
		self.timeConstants_list = []
		self.__populationSize_int = 1000
		self.__timesteps_int = 100
		self.__infectedAtT0_int = 1
		self.__infected_int = self.__infectedAtT0_int ## number of infected people to be updated during the simulation

		## initialize containers for human agents to be used during simulation
		self.__healthyHumans_list = []
		self.__exposedHumans_list = []
		self.__infectedHumans_list = []
	

	## model functions
	"""
	InitializeModel initializes a number of human agents defined by population size and infected at t_0
	"""
	def InitializeModel(self):
		NoHealthy = self.__populationSize_int - self.__infectedAtT0_int ## calc number of healthy humans
		for num in range(self.__infectedAtT0_int):
			sick = human(status='infected') ## initialize an infected human
			self.__infectedHumans_list.append(sick) ## add the initialized human to the respective list
		for num in range(NoHealthy):
			fit = human() ## initialize a healthy human
			self.__healthyHumans_list.append(fit) ## add the initialized human to the respective list
		## print log info
		debug.log('Model initialized successfully, population size: ' + str(self.__populationSize_int) + \
			      ', infected humans at t=0: ' + str(len(self.__healthyHumans_list)))

	"""
	PropagateVirus defines how infected spread the virus to healthy humans depending on the given parameters
	such as infection probabilities, mitigation measurements
	"""
	def PropagateVirus(self, parameters_dict):

##NOTE: We need to talk about how we want functions to be structured