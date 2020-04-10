#!/usr/bin/python
"""
This class defines the a human agent to be used in a (Corona) Virus infection model.
It defines the agents properties and the transitions between different stati.
created April, 2nd, 2020 -
(c) Judith Wodke, Stephan O. Adler, PLEASE ADD YOUR NAME IF CONTRIBUTING!
"""

# import required libraries
import numpy.random as npr  # numpy.random for generating random numbers
import logging as log  # logging for allowing to keep track of code development and putative errors
import sys  # sys
from location import *

# define the human agent class


class Human(object):
    """
    Class holding humans as agents of ABM.

    Attributes
    ----------
    ID : int
        Identification number of agent
    status : str
        Status of Agent (S,I,R or D)
    age : int
        Age of agent
    original_schedule : dict
        schedule of agent (defined by agent-type)
    schedule : dict
        effective schedule of agent (might be changed throughout simulation)
    loc : location.Location
        Location of agent
    personal_risk : float
        Succeptibility of agent
    infection_time : int
        Time at which agent was infected
    diagnosistime : int
        Time at which agent was diagnosed
    hospitalisation_time : int
        Time at which agent was hospitalised
    death_time : int
        Time at which agent died
    icu_time : int
        Time at which went to ICU
    rehospitalization_time : int
        Time at which agent went back to hospital from ICU

    diagnosed : bool
        Agent is diagnosed
    hospitalized : bool
        Agent is hospitalized
    icu : bool
        Agent is in ICU
    was_infected : bool
        Agent has ever been infected

    Methods
    ----------
    __init__()

    update_status()

    get_status()

    get_flags()

    move()

    get_recover_prob()

    get_personal_risk()

    getInfected()

    getReHospitalized()

    getHospitalized()

    die()
    """

    def __init__(self, ID, age, schedule, loc, status='S'):
        # initialize properties
        self.ID = ID
        self.status = status  # all humans are initialized as 'safe', except for a number of infected defined by the simulation parameters
        self.age = age  # if we get an age distribution, we should sample the age from that distribution
        self.schedule = schedule  # dict of times and locations
        self.loc = loc  # current location
        self.personal_risk = self.get_personal_risk(age)  # todesrisiko
        self.infection_time = 0
        self.diagnosis_time = 0
        self.hospitalisation_time = 0
        self.death_time = 0
        self.icu_time = 0
        self.rehospitalization_time = 0
        self.diagnosed = False
        self.hospitalized = False
        self.icu = False
        self.was_infected = False
        loc.enter(self)

# NOTE: we have to think about where to add additional information about age-dependent transition parameters, mobility profiles, etc.

    def update_status(self, time):  # this is not yet according to Eddas model
        if self.status == 'R':
            pass
        elif self.status == 'S':
            risk = self.loc.infection_risk()
            self.getInfected(risk, time)
        elif self.status == 'I':
            self.getDiagnosed(1, time)
            self.die(time)
            if self.status == 'I':
                recover_prob = self.get_recover_prob(time)
                self.recover(recover_prob)
            if self.status == 'I':
                if not self.hospitalized:
                    # hospitalization_prob_float = self.Get_hospitalization_risk(age_int)
                    self.getHospitalized(0.2, time)
                else:
                    if not self.icu:
                        self.getICUed(0.25, time)
                    else:
                        self.getReHospitalized(0.5, time)

    def get_status(self):  # for storing simulation data
        return {'h_ID': self.ID, 'loc': self.loc.ID, 'status': self.status}

    def get_flags(self):  # for storing simulation data (flags)
        return {'h_ID': self.ID, 'WasInfected': flag2Int(self.was_infected), 'Diagnosed': flag2Int(self.diagnosed), 'Hospitalized': flag2Int(self.hospitalized), 'ICUed': flag2Int(self.icu)}

    def move(self, time):  # agent moves relative to global time
        # {'times':[0,10,16], 'locs':[<location1>,<location2>,<location3>]}
        if time % 24 in self.schedule['times']:  # here i check for a 24h cycling schedule
            self.loc.leave(self)  # leave old location
            new_loc = self.schedule['locs'][self.schedule['times'].index(time % 24)]
            self.loc = new_loc
            new_loc.enter(self)  # enter new location

    def get_recover_prob(self, time):  # this needs improvement and is preliminary
        prob = (time - self.infection_time) / \
            480.  # probabitily increases hourly over 20 days (my preliminary random choice)
        # am besten mit kummulativer gauss-verteilung
        return prob

    def get_personal_risk(self, age):  # maybe there is data for that...
        if age < 60:
            risk = 0.001
        elif age < 75:
            risk = 0.005
        else:
            risk = 0.01
        return risk

    # status transitions humans can undergo
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

    def getInfected(self, risk, time):
        if risk > npr.random_sample():
            self.status = 'I'
            self.infection_time = time
            self.was_infected = True

    def getDiagnosed(self, probability, time):
        if probability > npr.random_sample():
            self.diagnosed = True
            self.diagnosis_time = time

    def recover(self, recover_prob):
        if recover_prob > npr.random_sample():
            self.status = 'R'
            self.icu = False
            self.hospitalized = False
            self.diagnosed = False
            self.schedule = self.original_schedule

    def getICUed(self, probability, time):
        if probability > npr.random_sample():
            self.icu = True
            self.hospitalized = False
            self.icu_time = time

    def getReHospitalized(self, probability, time):
        if probability > npr.random_sample():
            self.hospitalized = True
            self.icu = False
            self.rehospitalization_time = time

    def getHospitalized(self, probability, time):
        if probability > npr.random_sample():
            self.hospitalized = True
            self.hospitalization_time = time
            if not self.diagnosed:
                self.diagnosed = True
                self.diagnosis_time = time
            ## set locations in schedule to next hospital 24/7#
            #hospital = self.loc.next_hospital()
            #locDict = {i.ID: i for i in self.loc.neighbourhood.locations}
            #self.schedule['locs'] = [locDict[hospital]]*len(list(self.schedule['times']))

    def die(self, time):
        if self.personal_risk > npr.random_sample():
            self.status = 'D'
            self.death_time = time
            self.icu = False
            self.hospitalized = False
            self.diagnosed = False


def flag2Int(flag):
    if flag:
        return(1)
    else:
        return(0)
