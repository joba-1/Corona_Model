import pandas as pd

# read data
infectivity_df = pd.read_csv('datafiles/state_transition_probs/infectivity.csv')
recovery_df = pd.read_csv('datafiles/state_transition_probs/recovery.csv')
hospitalisation_df = pd.read_csv('datafiles/state_transition_probs/hospitalisation.csv')
icu_death_risk_df = pd.read_csv('datafiles/state_transition_probs/icu_to_death.csv')
general_death_risk_df = pd.read_csv('datafiles/state_transition_probs/death_risk.csv')
to_icu_df = pd.read_csv('datafiles/state_transition_probs/to_icu.csv')
icu_to_hospital_df = pd.read_csv('datafiles/state_transition_probs/icu_to_hospital.csv')
diagnosis_df = pd.read_csv('datafiles/state_transition_probs/diagnosis.csv')

# compute vars for run time
infectivity_df_max_time = infectivity_df['Time(h)'].max()
recovery_df_max_time = recovery_df['time/hours'].max()
hospitalisation_df_max_time = hospitalisation_df['Time'].max()
icu_death_risk_df_max_time = icu_death_risk_df['Hours in ICU'].max()
general_death_risk_df_max_time = general_death_risk_df['Hours infected'].max()
to_icu_df_max_time = to_icu_df['Time'].max()
icu_to_hospital_df_max_time = icu_to_hospital_df['Hours in ICU'].max()
diagnosis_df_max_time = diagnosis_df['Hours'].max()

# set indexes for run time
infectivity_df.set_index('Time(h)', inplace=True)
recovery_df.set_index('time/hours', inplace=True)
hospitalisation_df.set_index('Time', inplace=True)
icu_death_risk_df.set_index('Hours in ICU', inplace=True)
general_death_risk_df.set_index('Hours infected', inplace=True)
to_icu_df.set_index('Time', inplace=True)
icu_to_hospital_df.set_index('Hours in ICU', inplace=True)
diagnosis_df.set_index('Hours', inplace=True)


def _infectivity(infection_time):
    if infection_time == 0:
        return 0
    if infection_time > infectivity_df_max_time:
        return 0
    return float(infectivity_df.loc[infection_time, 'Probability_to_infect'])


def _recovery(infection_time):
    if infection_time == 0:
        return 0
    if infection_time > recovery_df_max_time:
        return float(recovery_df['recover probability'].max())
    return float(recovery_df.loc[infection_time, 'recover probability'])


def _hospitalisation(infection_time, age):
    if age > 99:
        age = 99
    if infection_time == 0:
        return 0
    if infection_time > hospitalisation_df_max_time:
        return 0
    return float(hospitalisation_df.loc[infection_time, str(age)])


def _icu_death_risk(icu_time, age):
    if age > 99:
        age = 99
    if icu_time == 0:
        return 0
    if icu_time > icu_death_risk_df_max_time:
        return 0
    return float(icu_death_risk_df.loc[icu_time, str(age)])


def _general_death_risk(infection_time, age):
    if age > 99:
        age = 99
    if infection_time == 0:
        return 0
    if infection_time > general_death_risk_df_max_time:
        return 0
    return float(general_death_risk_df.loc[infection_time, str(age)])


def _to_icu(hospital_time, age):
    if age > 99:
        age = 99
    if hospital_time == 0:
        return 0
    if hospital_time > to_icu_df_max_time:
        return 0
    return float(to_icu_df.loc[hospital_time, str(age)])


def _icu_to_hospital(icu_time, age):
    if age > 99:
        age = 99
    if icu_time == 0:
        return 0
    if icu_time > icu_to_hospital_df_max_time:
        return float(icu_to_hospital_df[str(age)].max())
    return float(icu_to_hospital_df.loc[icu_time, str(age)])


def _diagnosis(infection_time):
    if infection_time == 0:
        return 0
    if infection_time > diagnosis_df_max_time:
        return 0
    return float(diagnosis_df.loc[infection_time, 'probability'])
