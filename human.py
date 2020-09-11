# from numpy.random import choice as choosing  # numpy.random for generating random numbers
from random import choice as choosing_one
import numpy
import dataProcessing as dp
from random import random as randomval
import copy
from collections import OrderedDict as ordered_dict
from configure_simulation import location_coefficients as location_coefficient_dict


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

    get_death_prob()
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
        # all humans are initialized as 'S' (susceptible), except for a number of infected defined by the simulation parameters
        self.status = status
        self.preliminary_status = copy.copy(status)
        self.age = age  # if we get an age distribution, we should sample the age from that distribution
        self.schedule = schedule  # dict of times and locations
        self.original_schedule = {'type': copy.copy(schedule['type']), 'times': copy.copy(
            schedule['times']), 'locs': copy.copy(schedule['locs'])}
        self.specific_schedule = {'type': copy.copy(schedule['type']), 'times': copy.copy(
            schedule['times']), 'locs': copy.copy(schedule['locs'])}
        self.diagnosed_schedule = diagnosed_schedule
        self.type = self.original_schedule['type']
        self.loc = loc  # current location
        self.home = loc
        loc.enter(self)

        self.behaviour_as_infected = 1
        self.behaviour_as_susceptible = 1
        self.interaction_modifier = 1

        self.stati_times = {'infection_time': numpy.nan,
                            'diagnosis_time': numpy.nan,
                            'hospitalization_time': numpy.nan,
                            'recover_time': numpy.nan,
                            'immunity_loss_time': numpy.nan,
                            'death_time': numpy.nan,
                            'icu_time': numpy.nan,
                            'rehospitalization_time': numpy.nan}

        self.stati_durations = {'infection_duration': 0,
                                'diagnosis_duration': 0,
                                'hospitalization_duration': 0,
                                'recovery_duration': 0,
                                'icu_duration': 0}

        self.is_infected = False
        self.is_recovered = False
        self.diagnosed = False
        self.hospitalized = False
        self.icu = False

        self.was_recovered = False
        self.was_infected = False
        self.was_diagnosed = False
        self.was_hospitalized = False
        self.was_icued = False

        self.preliminary_is_recovered = False
        self.preliminary_is_infected = False
        self.preliminary_diagnosed = False
        self.preliminary_hospitalized = False
        self.preliminary_icu = False

        self.preliminary_was_recovered = False
        self.preliminary_was_infected = False
        self.preliminary_was_diagnosed = False
        self.preliminary_was_hospitalized = False
        self.preliminary_was_icued = False

        self.lost_immunity = False

        self.contact_persons = []
        self.infected_by = -1
        self.current_time = 0


# NOTE: we have to think about where to add additional information about age-dependent transition parameters, mobility profiles, etc.

    def update_state(self, time):
        """
        Updates agent-status and -flags.
        Arguments to provide are: time (int)
        """
        self.contact_persons = []  # ID of contact person#
        self.infected_by = -1
        self.current_time = time
        if self.is_infected:
            self.stati_durations['infection_duration'] += 1
            if self.diagnosed:
                self.stati_durations['diagnosis_duration'] += 1
            self.get_diagnosed(self.get_diagnosis_prob(), time)

            # What_to_do method #
            probabilities = [self.get_death_prob(), self.get_recover_prob()]
            if sum(probabilities) > 1:
                ## if the sum of death- and recovery probability is larger than 1 ##
                ## normalize probabilities to sum to 1 ##
                probabilities = [i/sum(probabilities) for i in probabilities]
                ## also print a message ##
                print('Death- or recover-probability for age ' + str(self.age) +
                      ' and infection-duration '+str(self.stati_durations['infection_duration']))
            what_happens = own_choose_function(probabilities)
            if what_happens == 'die':
                self.die(time)
            elif what_happens == 'recover':
                self.recover(time)
            else:
                if self.icu:
                    self.stati_durations['icu_duration'] += 1
                else:
                    if self.hospitalized:
                        self.stati_durations['hospitalization_duration'] += 1
                        self.get_ICUed(self.get_icu_prob(), time)
                    else:
                        if self.diagnosed:
                            self.get_hospitalized(self.get_hospitalization_prob(), time)
        elif self.is_recovered:
            self.stati_durations['recovery_duration'] += 1
            self.lose_immunity(0, time)

    # for storing simulation data (flags)
    def get_information_for_timecourse(self, time, keys_list='all'):
        """
        Returns ordered dictionary with time ('time') agent-ID ('h_ID') and information on stati/location/flags.
        All stati temporary and cumulative flags are encoded by one integer to save memory.
        Arguments to provide are: none
        """
        out = ordered_dict()
        out['time'] = time  # write down current time-step#
        out['h_ID'] = self.ID  # write down agent-ID#
        out['loc'] = self.loc.ID  # write down ID of current location#
        out['status'] = self.encode_stati()  # write down agent-status, in encoded fashion#
        # write down temporary agent-flags, in encoded fashion#
        out['Temporary_Flags'] = self.encode_temporary_flags()
        # write down cumulative agent-flags, in encoded fashion#
        out['Cumulative_Flags'] = self.encode_cumulative_flags()
        out['Interaction_partner'] = ','.join(self.contact_persons)
        out['Infection_event'] = int(self.infected_by)
        if keys_list == 'all':
            return(out)
        else:
            return(ordered_dict((i, out[i]) for i in keys_list))

    def encode_temporary_flags(self):
        """
        Encodes the four different temporary-flags into one specific integer.
        0: Agent is not infected.
        1: Agent is infected.
        2: Agent is infected and diagnosed.
        3: Agent is infected, diagnosed and hospitalized  (not ICU).
        4: Agent is infected, diagnosed and in ICU  (not hospital).
        """
        if self.is_infected:
            if self.diagnosed:
                if self.hospitalized:
                    return(numpy.uint8(3))
                elif self.icu:
                    return(numpy.uint8(4))
                else:
                    return(numpy.uint8(2))
            else:
                return(numpy.uint8(1))
        else:
            return(numpy.uint8(0))

    def encode_cumulative_flags(self):
        """
        Encodes the four different cumulative-flags into one specific integer.
        0: Agent has never been infected.
        1: Agent has been infected.
        2: Agent has been infected and diagnosed.
        3: Agent has been infected, diagnosed and hospitalized.
        4: Agent has been infected, diagnosed and in ICU.
        """
        if self.was_infected:
            if self.was_diagnosed:
                if self.was_hospitalized:
                    return(numpy.uint8(3))
                elif self.was_icued:
                    return(numpy.uint8(4))
                else:
                    return(numpy.uint8(2))
            else:
                return(numpy.uint8(1))
        else:
            return(numpy.uint8(0))

    def encode_stati(self):
        """
        Encodes the four different stati into one specific integer.
        0: 'S'
        1: 'I'
        2: 'R'
        3: 'D'
        """
        if self.status == 'S':
            return(numpy.uint8(0))
        elif self.status == 'I':
            return(numpy.uint8(1))
        elif self.status == 'R':
            return(numpy.uint8(2))
        elif self.status == 'D':
            return(numpy.uint8(3))

    def get_infection_info(self):
        """
        Returns dictionary with agent-ID ('h_ID') and information
        on the times and place of certain events
        Arguments to provide are: none
        """
        out = {'h_ID': self.ID,
               'infection_time': self.stati_times['infection_time'],
               'diagnosis_time': self.stati_times['diagnosis_time'],
               'hospitalization_time': self.stati_times['hospitalization_time'],
               'recover_time': self.stati_times['recover_time'],
               'death_time': self.stati_times['death_time'],
               'icu_time': self.stati_times['icu_time'],
               'rehospitalization_time': self.stati_times['rehospitalization_time']}
        return(out)

    def move(self, time):  # agent moves relative to global time
        """
        Moves agent to next location, according to its schedule.
        Arguments to provide are: time (int)
        """
        ## Firstly decide which schedule to follow ##
        if not self.status == 'D' and not self.hospitalized and not self.icu and not self.diagnosed:
            ## if alive and not diagnosed, hospitalized or ICUed##
            ## follow own regular schedule ##
            current_schedule = self.schedule
        else:
            ## if dead, diagnosed, hospitalized or ICUed##
            ## follow schedule, specific to condition##
            current_schedule = self.specific_schedule
        ## move according to relevant schedule ##
        if time % (24*7) in current_schedule['times']:  # here i check for a 24h cycling schedule
            self.loc.leave(self)  # leave old location
            new_loc = current_schedule['locs'][current_schedule['times'].index(
                time % (24*7))]  # find new location in  schedule#
            self.loc = new_loc  # set own location to new location#
            new_loc.enter(self)  # enter new location

    def stay_home_instead_of_going_to(self, location_type, excluded_human_types=[]):
        """
        Prohibit agent to visit a given type of location, and stay home instead.
        Arguments to provide are:
        location_type (str) - location type not to visit anymore
        excluded_human_types (list of strings) - list of agent-schedule types, which should be still permitted to visit.
        """
        if self.original_schedule['type'] not in excluded_human_types:
            ## check whether the agent does not belong to the excluded types ##
            for i in range(len(self.schedule['locs'])):
                ## go to each entry in the agents schedule ##
                if self.schedule['locs'][i].location_type == location_type:
                    ## if the location-type  of the schedule-entry is the specified type ##
                    ## replace this with the agent's home-location ##
                    self.schedule['locs'][i] = self.home

    def get_diagnosis_prob(self):  # !!! this needs improvement and is preliminary
        """
        Retreive probability to be diagnosed from data-module.
        Arguments to provide are: none
        """
        return (dp._diagnosis(self.stati_durations, self.age))  # TODO change in exel sheet - compare with gangelt data

    def get_hospitalization_prob(self):  # this needs improvement and is preliminary
        """
        Retreive probability to be hospitalized from data-module.
        Arguments to provide are: none
        """
        return dp._hospitalisation(self.stati_durations, self.age)

    def get_rehospitalization_prob(self):  # this needs improvement and is preliminary
        """
        Retreive probability to be re-hospitalized (from ICU) from data-module.
        Arguments to provide are: none
        """
        return dp._icu_to_hospital(self.stati_durations, self.age)

    def get_icu_prob(self):  # this needs improvement and is preliminary
        """
        Retreive probability to be admitted to intensive-care from data-module.
        Arguments to provide are: none
        """
        return dp._to_icu(self.stati_durations, self.age)

    def get_recover_prob(self):  # this needs improvement and is preliminary
        """
        Retreive probability to recover from data-module.
        Arguments to provide are: none
        """
        # probabitily increases hourly over 20 days (my preliminary random choice)
        # am besten mit kummulativer gauss-verteilung
        if self.diagnosed:
            if self.hospitalized:
                prob = dp._recovery_from_hospitalized(self.stati_durations, self.age)
            elif self.icu:
                prob = dp._recovery_from_icu(self.stati_durations, self.age)
            else:
                prob = dp._recovery_from_diagnosed(self.stati_durations, self.age)
        else:
            prob = dp._recovery_from_undiagnosed(self.stati_durations, self.age)
        return prob

    def get_death_prob(self):  # maybe there is data for that...
        """
        Calculates the personal (age-dependent) risk.
        Arguments to provide are: none
        """
        if self.diagnosed:
            if self.hospitalized:
                risk = dp._hospital_death_risk(self.stati_durations, self.age)
            elif self.icu:
                risk = dp._icu_death_risk(self.stati_durations, self.age)
            else:
                risk = dp._diagnosed_death_risk(self.stati_durations, self.age)
        else:
            risk = dp._undiagnosed_death_risk(self.stati_durations, self.age)
        return(risk)  # TODO change in exel sheet - compare with gangelt data

    def get_initially_infected(self):
        """
        Determines whether an agent gets infected, based on personal risk.
        Changes status-attribute to 'I', writes current time to
        infection_time-attribute and sets was_infected-attribute to True.
        Arguments to provide are: risk (float)
        """
        self.preliminary_status = 'I'
        self.preliminary_is_infected = True
        self.preliminary_was_infected = True
        self.set_stati_from_preliminary()
        self.stati_times['infection_time'] = 0
        self.was_infected = True
        self.is_infected = True

    def get_immunity_loss_prob(self):  # this needs improvement and is preliminary
        """
        """
        return dp._immunity_loss(self.stati_durations, self.age)

    def interact_with(self, contact_person):
        if contact_person.is_infected:
            if self.status == 'S':
                if not self.preliminary_is_infected:
                    infection_event = self.get_infected(contact_person)
                    if infection_event == 1:
                        self.infected_by = contact_person.ID

    def get_infected(self, contact_person):
        """
        Determines whether an agent gets infected, at the current location and time.
        Changes status-attribute to 'I', writes current location to 'place_of_infection',
        writes current time to infection_time-attribute and sets was_infected-attribute to True.
        If applicable writes name of agent infecting it to got_infected_by.
        Arguments to provide are: risk (float), time (int)
        """
        coeff = 1
        out = -1
        if self.loc.location_type in location_coefficient_dict.keys():
            coeff = location_coefficient_dict['self.loc.location_type']
        infection_probability = contact_person.get_infectivity()*self.behaviour_as_susceptible*coeff
        if infection_probability >= randomval():
            self.preliminary_status = 'I'  # set owns preliminary status to infected ##
            self.preliminary_was_infected = True  # set own was_infected argument to True##
            self.preliminary_is_infected = True  # set own is_infected argument to True##
            self.stati_times['infection_time'] = self.current_time
            out = 1
        return(out)

    def get_diagnosed(self, probability, time):
        """
        Determines whether an agent gets diagnosed, based on diagnosis-probability.
        Changes diagnosed-attribute to 'True', writes current time to
        diagnosis_time-attribute.
        Arguments to provide are: probability (float), time (int)
        """
        if not self.diagnosed:
            if probability >= randomval():
                self.preliminary_diagnosed = True
                self.stati_times['diagnosis_time'] = time
                self.specific_schedule = self.diagnosed_schedule
                self.preliminary_was_diagnosed = True

    def recover(self, time):
        """
        Determines whether an agent recovers,
        based on recover-probability.
        Changes status-attribute to 'R', records current time to recover_time-attribute.
        Sets icu-,hospitalized- and diagnosed-attribute to False.
        Arguments to provide are: probability (float), time (int)
        """
        self.stati_times['recover_time'] = time
        self.preliminary_status = 'R'
        self.preliminary_icu = False
        self.preliminary_hospitalized = False
        self.preliminary_diagnosed = False
        self.preliminary_is_infected = False
        self.preliminary_is_recovered = True
        self.preliminary_was_recovered = True

    def lose_immunity(self, probability, time):
        """
        """
        if probability >= randomval():
            self.stati_times['immunity_loss_time'] = time
            self.preliminary_status = 'S'
            self.preliminary_is_recovered = False
            self.lost_immunity = True

    def get_ICUed(self, probability, time):
        """
        Determines whether an agent gets ICUed, based on ICU-probability.
        Changes icu-attribute to 'True', writes current time to
        icu_time-attribute. Sets hospitalized-attribute to False.
        Arguments to provide are: probability (float), time (int)
        """
        if probability >= randomval():
            self.preliminary_icu = True
            self.preliminary_hospitalized = False
            self.stati_times['icu_time'] = time
            self.preliminary_was_icued = True

    def get_rehospitalized(self, probability, time):
        """
        Determines whether an agent gets out of ICU and back to the normal
        hospital-bed, based on rehospitalization-probability.
        Changes hospitalized-attribute to 'True', writes current time to
        rehospitalization_time-attribute. Sets icu-attribute to False.
        Arguments to provide are: probability (float), time (int)
        """
        if probability >= randomval():
            self.preliminary_hospitalized = True
            self.preliminary_icu = False
            self.stati_times['rehospitalization_time'] = time

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
            self.preliminary_hospitalized = True
            self.stati_times['hospitalization_time'] = time
            self.preliminary_was_hospitalized = True
            ## set locations in schedule to next hospital 24/7#
            if self.loc.special_locations['hospital']:
                self.specific_schedule['locs'] = [self.loc.special_locations['hospital'][0]] * \
                    len(list(self.specific_schedule['times']))

    def die(self, time):
        """
        Determines whether an agent dies,
        based on personal_risk-probability.
        Changes status-attribute to 'D', records current time to death_time-attribute.
        Sets icu-,hospitalized- and diagnosed-attribute to False.
        Arguments to provide are: probability (float), time (int)
        """
        self.preliminary_status = 'D'
        self.stati_times['death_time'] = time
        self.preliminary_icu = False
        self.preliminary_hospitalized = False
        self.preliminary_diagnosed = False
        self.preliminary_is_infected = False
        if self.loc.special_locations['morgue']:
            self.specific_schedule['locs'] = [
                self.loc.special_locations['morgue'][0]] * len(list(self.specific_schedule['times']))

    def get_infectivity(self):
        """
        Returns the infectivity of infected agent.
        Should theoretically be based on the duration of the infection.
        For now it is set to the default-value of 1; so nothing changes,
        with respect to the previous version.
        """
        # print(self.stati_durations)
        infectivity = dp._infectivity(self.stati_durations, self.age)
        return(infectivity*self.behaviour_as_infected)

    def set_stati_from_preliminary(self):
        """
        Set status and flags from preliminary.
        Arguments to provide are: none
        """
        self.status = self.preliminary_status
        self.diagnosed = self.preliminary_diagnosed
        self.hospitalized = self.preliminary_hospitalized
        self.icu = self.preliminary_icu
        self.was_infected = self.preliminary_was_infected
        self.is_infected = self.preliminary_is_infected
        self.was_diagnosed = self.preliminary_was_diagnosed
        self.was_hospitalized = self.preliminary_was_hospitalized
        self.was_icued = self.preliminary_was_icued
        self.is_recovered = self.preliminary_is_recovered
        self.was_recovered = self.preliminary_was_recovered

    def reset_schedule(self):
        """
        Resets the agents' schedule to the original one.
        Arguments to provide are: none
        """
        self.schedule = self.original_schedule


def own_choose_function(probabilities):
    """
    Takes list with two entries [p1,p2] and creates a three option urne from them.
    Then picks a random number between0 and 1 and checks in what section it falls.
    (|p1|p2| 1-p1-p2|).
    """
    val = randomval()
    if val <= probabilities[0]:
        return('die')
    elif val <= sum(probabilities):
        return('recover')
