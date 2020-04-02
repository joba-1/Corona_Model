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
		self.

		self.__populationSize = 1000
		self.__timesteps = 100
		self.__infectedAtT0 = 1

		for infectedHuman in range(self.__infectedAtT0):
			sick = 

	def InitializeModel(self, chrToUseList, pathToUseList, noSteps=10):
