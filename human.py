from numpy.random import choice as choosing  # numpy.random for generating random numbers
# import logging as log  # logging for allowing to keep track of code development and putative errors
# import sys  # sys
#from location import *
#import copy
import numpy
import dataProcessing as dp
from random import random as randomval

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
        schedule of agent (defined by at initialization)
    schedule : dict
        effective schedule of agent (might be changed throughout simulation)
    diagnosed_schedule : dict
        schedule to follow while diagnosed==True
    loc : location.Location
        Location of agent
    personal_risk : float
        Succeptibility of agent
    infection_time : int
        Time at which agent was infected
    diagnosistime : int
        Time at which agent was diagnosed
    hospitalization_time : int
        Time at which agent was hospitalised
    recover_time : int
        Time at which agent recovered
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
    infection_duration : int
        The duration of the agent's infection.
    behaviour_as_infected : float
        Factor by which the infected can decrease infectivity by behaviour.
    behaviour_as_susceptible = float
        Factor by which the susceptible can avoid infection by behaviour.

    Methods
    ----------
    __init__()
        Creates human-object with initial status 'S'.
        Arguments to provide are: ID (int), age (int), schedule (dict), loc (location.Location)

    update_state()
        Updates agent-status and -flags.
        Arguments to provide are: time (int)

    get_status()
        Returns dictionary with agent-ID ('h_ID'), current location ('loc') and status ('status')
        Arguments to provide are: none

    get_flags()
        Returns dictionary with agent-ID ('h_ID') and information on flags
        Arguments to provide are: none

    move()
        Moves agent to next location, according to its schedule.
        Arguments to provide are: time (int)

    get_diagnosis_prob()
        Calculates probability to be diagnosed.
        For now it returns a default value.
        Function has to be defined!
        Arguments to provide are: none

    get_hospitalization_prob()
        Calculates probability to be hospitalized.
        For now it returns a default value.
        Function has to be defined!
        Arguments to provide are: none

    get_rehospitalization_prob()
        Calculates probability to be rehospitalized.
        For now it returns a default value.
        Function has to be defined!
        Arguments to provide are: none

    get_icu_prob()
        Calculates probability to be ICUed.
        For now it returns a default value.
        Function has to be defined!
        Arguments to provide are: none

    get_recover_prob()
        Calculates probability to recover.
        Arguments to provide are: time (int)

    get_personal_risk()
        Calculates the personal (age-dependent) risk.
        Arguments to provide are: none

    get_infected()
        Determines whether an agent gets infected, at the current location and time.
        Changes status-attribute to 'I', writes current location to 'place_of_infection',
        writes current time to infection_time-attribute and sets was_infected-attribute to True.
        If applicable writes name of agent infecting it to got_infected_by.
        Arguments to provide are: risk (float), time (int)

    get_diagnosed()
        Determines whether an agent gets diagnosed, based on diagnosis-probability.
        Changes diagnosed-attribute to 'True', writes current time to
        diagnosis_time-attribute.
        Arguments to provide are: probability (float), time (int)

    get_rehospitalized()
        Determines whether an agent gets out of ICU and back to the normal
        hospital-bed, based on rehospitalization-probability.
        Changes hospitalized-attribute to 'True', writes current time to
        rehospitalization_time-attribute. Sets icu-attribute to False.
        Arguments to provide are: probability (float), time (int)

    get_hospitalized()
        Determines whether an agent gets to the hospital,
        based on hospitalization-probability.
        Changes hospitalized-attribute to 'True', writes current time to
        hospitalization_time-attribute
        and sets diagnosed-attribute to True (if it wasn't).
        CHANGE OF SCHEDULE MUST BE IMPLEMENTED HERE!!!
        Arguments to provide are: probability (float), time (int)

    get_ICUed()
        Determines whether an agent gets ICUed, based on ICU-probability.
        Changes icu-attribute to 'True', writes current time to
        icu_time-attribute. Sets hospitalized-attribute to False.
        Arguments to provide are: probability (float), time (int)

    die()
        Determines whether an agent dies,
        based on personal_risk-probability.
        Changes status-attribute to 'D', records current time to death_time-attribute.
        Sets icu-,hospitalized- and diagnosed-attribute to False.
        Arguments to provide are: probability (float), time (int)

    recover()
        Determines whether an agent recovers,
        based on recover-probability.
        Changes status-attribute to 'R', records current time to recover_time-attribute.
        Sets icu-,hospitalized- and diagnosed-attribute to False.
        Sets schedule-attribute to original_schedule.
        Arguments to provide are: probability (float), time (int)

    get_infectivity()
        Returns the infectivity of infected agent.
        Should theoretically be based on the duration of the infection and
        the personal behaviour.
        For now it is set to the default-value of 1; so nothing changes,
        with respect to the previous version.

    get_infection_info()
        Returns dictionary with agent-ID ('h_ID') and information
        on the times and place of certain events
    """

    def __init__(self, ID, age, schedule, diagnosed_schedule, loc, status='S', enable_infection_interaction=False):
        """
        Creates human-object with initial status 'S'.
        Arguments to provide are: ID (int), age (int), schedule (dict), loc (location.Location)
        """
        # initialize properties
        self.infection_interaction_enabled = enable_infection_interaction
        self.ID = ID
        self.status = status  # all humans are initialized as 'safe', except for a number of infected defined by the simulation parameters
        self.age = age  # if we get an age distribution, we should sample the age from that distribution
        self.schedule = schedule  # dict of times and locations
        self.original_schedule = schedule
        self.diagnosed_schedule = diagnosed_schedule
        self.loc = loc  # current location
        self.place_of_infection = numpy.nan
        self.infection_time = numpy.nan
        self.diagnosis_time = numpy.nan
        self.hospitalization_time = numpy.nan
        self.recover_time = numpy.nan
        self.death_time = numpy.nan
        self.icu_time = numpy.nan
        self.rehospitalization_time = numpy.nan
        self.diagnosed = False
        self.hospitalized = False
        self.icu = False
        self.was_infected = False
        self.infection_duration = 0
        self.hospitalization_duration = 0
        self.icu_duration = 0
        self.behaviour_as_infected = 1
        self.behaviour_as_susceptible = 1
        loc.enter(self)
        self.personal_risk = self.get_personal_risk()  # todesrisiko
        self.preliminary_status = 'S'
        self.got_infected_by = numpy.nan
        self.infected_in_contact_with = set()
        self.is_infected = False
# NOTE: we have to think about where to add additional information about age-dependent transition parameters, mobility profiles, etc.

    def update_state(self, time):  # this is not yet according to Eddas model
        """
        Updates agent-status and -flags.
        Arguments to provide are: time (int)
        """
        if self.status == 'R':
            pass
        elif self.status == 'S':
            self.get_infected(time)
        elif self.is_infected:
            self.infection_duration += 1
            self.get_diagnosed(self.get_diagnosis_prob(), time)
            recoverProb = self.get_recover_prob()
            what_happens = choosing(['die', 'recover', 'stay_infected'], p=[
                self.personal_risk, recoverProb, 1-recoverProb-self.personal_risk])
            if what_happens == 'die':
                self.die(1.0, time)
            elif what_happens == 'recover':
                self.recover(1.0, time)
            else:
                if self.icu:
                    self.icu_duration += 1
                    self.get_rehospitalized(self.get_rehospitalization_prob(), time)
                else:
                    if self.hospitalized:
                        self.hospitalization_duration += 1
                        self.get_ICUed(self.get_icu_prob(), time)
                    else:
                        self.get_hospitalized(self.get_hospitalization_prob(), time)

    def get_status(self):  # for storing simulation data
        """
        Returns dictionary with agent-ID ('h_ID'), current location ('loc') and status ('status')
        Arguments to provide are: none
        """
        return {'h_ID': self.ID, 'loc': self.loc.ID, 'status': self.status}

    def get_flags(self):  # for storing simulation data (flags)
        """
        Returns dictionary with agent-ID ('h_ID') and information on flags
        Arguments to provide are: none
        """
        return {'h_ID': self.ID, 'WasInfected': int(self.was_infected), 'Diagnosed': int(self.diagnosed), 'Hospitalized': int(self.hospitalized), 'ICUed': int(self.icu)}

    def get_infection_info(self):  # for storing simulation data (flags)
        """
        Returns dictionary with agent-ID ('h_ID') and information
        on the times and place of certain events
        Arguments to provide are: none
        """
        return {'h_ID': self.ID,
                'infected_in_contact_with': ' , '.join(self.infected_in_contact_with),
                'infected_by': str(self.got_infected_by),
                'place_of_infection': str(self.place_of_infection),
                'infection_time': self.infection_time,
                'recovery_time':  self.recover_time,
                'death_time':     self.death_time,
                'diagnosis_time': self.diagnosis_time,
                'hospitalized_time':    self.hospitalization_time,
                'hospital_to_ICU_time': self.icu_time,
                'ICU_to_hospital_time': self.rehospitalization_time}

    def move(self, time):  # agent moves relative to global time
        """
        Moves agent to next location, according to its schedule.
        Arguments to provide are: time (int)
        """
        # {'times':[0,10,16], 'locs':[<location1>,<location2>,<location3>]}
        if time % (24*7) in self.schedule['times']:  # here i check for a 24h cycling schedule
            self.loc.leave(self)  # leave old location
            new_loc = self.schedule['locs'][self.schedule['times'].index(time % (24*7))]
            self.loc = new_loc
            new_loc.enter(self)  # enter new location

    def get_diagnosis_prob(self):  # this needs improvement and is preliminary
        """
        Calculates probability to be diagnosed.
        For now it returns a default value.
        Function has to be defined!
        Arguments to provide are: none
        """
        return dp._diagnosis(self.infection_duration)

    def get_hospitalization_prob(self):  # this needs improvement and is preliminary
        """
        Calculates probability to be hospitalized.
        For now it returns a default value.
        Function has to be defined!
        Arguments to provide are: none
        """
        return dp._hospitalisation(self.infection_duration, self.age)

    def get_rehospitalization_prob(self):  # this needs improvement and is preliminary
        """
        Calculates probability to be rehospitalized.
        For now it returns a default value.
        Function has to be defined!
        Arguments to provide are: none
        """
        return dp._hospital_to_icu(self.icu_duration, self.age)

    def get_icu_prob(self):  # this needs improvement and is preliminary
        """
        Calculates probability to be ICUed.
        For now it returns a default value.
        Function has to be defined!
        Arguments to provide are: none
        """
        return dp._to_icu(self.hospitalization_duration, self.age)

    def get_recover_prob(self):  # this needs improvement and is preliminary
        """
        Calculates probability to recover.
        Arguments to provide are: none
        """
        # probabitily increases hourly over 20 days (my preliminary random choice)
        # am besten mit kummulativer gauss-verteilung
        if self.icu:
            return(0.0)
        else:
            prob = dp._recovery(self.infection_duration)
            return prob

    def get_personal_risk(self):  # maybe there is data for that...
        """
        Calculates the personal (age-dependent) risk.
        Arguments to provide are: none
        """
        if self.age < 60:
            risk = 0.001
        elif self.age < 75:
            risk = 0.005
        else:
            risk = 0.01
        if self.icu:
            risk = dp._icu_death_risk(self.icu_time, self.age)
        return(risk*self.behaviour_as_susceptible)

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

    def get_initially_infected(self):
        """
        Determines whether an agent gets infected, based on personal risk.
        Changes status-attribute to 'I', writes current time to
        infection_time-attribute and sets was_infected-attribute to True.
        Arguments to provide are: risk (float)
        """
        self.preliminary_status = 'I'
        self.set_status_from_preliminary()
        self.infection_time = 0
        self.was_infected = True
        self.place_of_infection = self.loc.ID
        self.is_infected = True

    def get_infected(self, time):
        """
        Determines whether an agent gets infected, at the current location and time.
        Changes status-attribute to 'I', writes current location to 'place_of_infection',
        writes current time to infection_time-attribute and sets was_infected-attribute to True.
        If applicable writes name of agent infecting it to got_infected_by.
        Arguments to provide are: risk (float), time (int)
        """
        if self.infection_interaction_enabled:
            infectious_person = self.loc.infection_interaction()
            if infectious_person is not None:
                self.infected_in_contact_with.add(str(infectious_person.ID))
                if infectious_person.get_infectivity()*self.behaviour_as_susceptible >= randomval():
                    self.preliminary_status = 'I'
                    self.infection_time = time
                    self.was_infected = True
                    self.got_infected_by = infectious_person.ID
                    self.place_of_infection = self.loc.ID
                    self.is_infected = True
        else:
            if self.loc.infection_risk()*self.behaviour_as_susceptible >= randomval():
                self.preliminary_status = 'I'
                self.infection_time = time
                self.place_of_infection = self.loc.ID
                self.was_infected = True
                self.is_infected = True

    def get_diagnosed(self, probability, time):
        """
        Determines whether an agent gets diagnosed, based on diagnosis-probability.
        Changes diagnosed-attribute to 'True', writes current time to
        diagnosis_time-attribute.
        Arguments to provide are: probability (float), time (int)
        """
        if not self.diagnosed:
            if probability >= randomval():
                self.diagnosed = True
                self.diagnosis_time = time
                self.schedule = self.diagnosed_schedule

    def recover(self, recover_prob, time):
        """
        Determines whether an agent recovers,
        based on recover-probability.
        Changes status-attribute to 'R', records current time to recover_time-attribute.
        Sets icu-,hospitalized- and diagnosed-attribute to False.
        Sets schedule-attribute to original_schedule.
        Arguments to provide are: probability (float), time (int)
        """
        if recover_prob >= randomval():
            self.recover_time = time
            self.preliminary_status = 'R'
            self.icu = False
            self.hospitalized = False
            self.diagnosed = False
            self.schedule = self.original_schedule
            self.is_infected = False

    def get_ICUed(self, probability, time):
        """
        Determines whether an agent gets ICUed, based on ICU-probability.
        Changes icu-attribute to 'True', writes current time to
        icu_time-attribute. Sets hospitalized-attribute to False.
        Arguments to provide are: probability (float), time (int)
        """
        if probability >= randomval():
            self.icu = True
            self.hospitalized = False
            self.icu_time = time

    def get_rehospitalized(self, probability, time):
        """
        Determines whether an agent gets out of ICU and back to the normal
        hospital-bed, based on rehospitalization-probability.
        Changes hospitalized-attribute to 'True', writes current time to
        rehospitalization_time-attribute. Sets icu-attribute to False.
        Arguments to provide are: probability (float), time (int)
        """
        if probability >= randomval():
            self.hospitalized = True
            self.icu = False
            self.rehospitalization_time = time

    def get_hospitalized(self, probability, time):
        """
        Determines whether an agent gets to the hospital,
        based on hospitalization-probability.
        Changes hospitalized-attribute to 'True', writes current time to
        hospitalization_time-attribute
        and sets diagnosed-attribute to True (if it wasn't).
        CHANGE OF SCHEDULE MUST BE IMPLEMENTED HERE!!!
        Arguments to provide are: probability (float), time (int)
        """
        if probability >= randomval():
            self.hospitalized = True
            self.hospitalization_time = time
            self.get_diagnosed(1.0, time)
            ## set locations in schedule to next hospital 24/7#
            if self.loc.special_locations['hospital']:
                self.schedule['locs'] = [self.loc.special_locations['hospital'][0]] * \
                    len(list(self.schedule['times']))

    def die(self, risk, time):
        """
        Determines whether an agent dies,
        based on personal_risk-probability.
        Changes status-attribute to 'D', records current time to death_time-attribute.
        Sets icu-,hospitalized- and diagnosed-attribute to False.
        Arguments to provide are: probability (float), time (int)
        """
        if risk >= randomval():
            self.preliminary_status = 'D'
            self.death_time = time
            self.icu = False
            self.hospitalized = False
            self.diagnosed = False
            self.is_infected = False
            if self.loc.special_locations['cemetery']:
                self.schedule['locs'] = [self.loc.special_locations['cemetery'][0]] * \
                    len(list(self.schedule['times']))

    def get_infectivity(self):
        """
        Returns the infectivity of infected agent.
        Should theoretically be based on the duration of the infection.
        For now it is set to the default-value of 1; so nothing changes,
        with respect to the previous version.
        """
        infectivity = dp._infectivity(self.infection_duration)  
        return(infectivity*self.behaviour_as_infected)

    def set_status_from_preliminary(self):
        """
        Set status from preliminary status
        Arguments to provide are: none
        """
        self.status = self.preliminary_status
