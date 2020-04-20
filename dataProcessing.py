import pandas as pd
import numpy as np

infectivity_df = pd.read_csv('datafiles/state_transition_probs/infectivity.csv')
recovery_df = pd.read_csv('datafiles/state_transition_probs/recovery.csv')
hospitalisation_df = pd.read_csv('datafiles/state_transition_probs/hospitalisation.csv')
icu_death_risk_df = pd.read_csv('datafiles/state_transition_probs/death_risk.csv')
to_icu_df = pd.read_csv('datafiles/state_transition_probs/to_icu.csv')
hospital_to_icu_df = pd.read_csv('datafiles/state_transition_probs/icu_to_hospital.csv')
diagnosis_df = pd.read_csv('datafiles/state_transition_probs/diagnosis.csv')

def _infectivity(infection_time):
    if infection_time == 0:
        return 0
    return infectivity_df.loc[infectivity_df['Time(h)'] == infection_time, 'Probability_to_infect']

def _recovery(infection_time):
    if infection_time == 0:
        return 0
    return recovery_df.loc[recovery_df['time/hours'] == infection_time, 'recover probability']

def _hospitalisation(infection_time, age):
    if infection_time == 0:
        return 0
    return hospitalisation_df.loc[hospitalisation_df['Time'] == infection_time, str(age)]

def _icu_death_risk(icu_time, age):
    if icu_time == 0:
        return 0
    return icu_death_risk_df.loc[icu_death_risk_df['Hours in ICU'] == icu_time, str(age)]

def _to_icu(hospital_time, age):
    if hospital_time == 0:
        return 0
    return to_icu_df.loc[to_icu_df['Time'] == hospital_time, str(age)]

def _hospital_to_icu(icu_time, age):
    if icu_time == 0:
        return 0
    return hospital_to_icu_df.loc[hospital_to_icu_df['Hours in ICU'] == icu_time, str(age)]

def _diagnosis(infection_time):
    if infection_time == 0:
        return 0
    return diagnosis_df.loc[diagnosis_df['Hours'] == infection_time, 'probability']