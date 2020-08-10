import pandas as pd
from configure_simulation import Simulation_Configuration

Configurator = Simulation_Configuration()

# read data
infectivity_df = pd.read_csv(Configurator.infectivity_df)
recovery_df = pd.read_csv(Configurator.recovery_df)
hospitalisation_df = pd.read_csv(Configurator.hospitalisation_df)
icu_death_risk_df = pd.read_csv(Configurator.icu_death_risk_df)
general_death_risk_df = pd.read_csv(Configurator.general_death_risk_df)
to_icu_df = pd.read_csv(Configurator.to_icu_df)
icu_to_hospital_df = pd.read_csv(Configurator.icu_to_hospital_df)
diagnosis_df = pd.read_csv(Configurator.diagnosis_df)

# compute vars for run time
infectivity_df_max_time = infectivity_df['Time-steps'].max()
recovery_df_max_time = recovery_df['Time-steps'].max()
hospitalisation_df_max_time = hospitalisation_df['Time-steps'].max()
icu_death_risk_df_max_time = icu_death_risk_df['Time-steps'].max()
general_death_risk_df_max_time = general_death_risk_df['Time-steps'].max()
to_icu_df_max_time = to_icu_df['Time-steps'].max()
icu_to_hospital_df_max_time = icu_to_hospital_df['Time-steps'].max()
diagnosis_df_max_time = diagnosis_df['Time-steps'].max()

# set indexes for run time
infectivity_df.set_index('Time-steps', inplace=True)
recovery_df.set_index('Time-steps', inplace=True)
hospitalisation_df.set_index('Time-steps', inplace=True)
icu_death_risk_df.set_index('Time-steps', inplace=True)
general_death_risk_df.set_index('Time-steps', inplace=True)
to_icu_df.set_index('Time-steps', inplace=True)
icu_to_hospital_df.set_index('Time-steps', inplace=True)
diagnosis_df.set_index('Time-steps', inplace=True)


def _infectivity(stati_durations):
    respective_duration = stati_durations[Configurator.infectivity_dependency]
    if respective_duration == 0:
        return 0
    if respective_duration > infectivity_df_max_time:
        return 0
    return float(infectivity_df.loc[respective_duration, 'Probability_to_infect'])


def _recovery(stati_durations):
    respective_duration = stati_durations[Configurator.recovery_dependency]
    if respective_duration == 0:
        return 0
    if respective_duration > recovery_df_max_time:
        return float(recovery_df['recover probability'].max())
    return float(recovery_df.loc[respective_duration, 'recover probability'])


def _hospitalisation(stati_durations, age):
    respective_duration = stati_durations[Configurator.hospitalisation_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > hospitalisation_df_max_time:
        return 0
    return float(hospitalisation_df.loc[respective_duration, str(age)])


def _icu_death_risk(stati_durations, age):
    respective_duration = stati_durations[Configurator.icu_death_risk_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > icu_death_risk_df_max_time:
        return 0
    return float(icu_death_risk_df.loc[respective_duration, str(age)])


def _general_death_risk(stati_durations, age):
    respective_duration = stati_durations[Configurator.general_death_risk_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > general_death_risk_df_max_time:
        return 0
    return float(general_death_risk_df.loc[respective_duration, str(age)])


def _to_icu(stati_durations, age):
    respective_duration = stati_durations[Configurator.to_icu_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > to_icu_df_max_time:
        return 0
    return float(to_icu_df.loc[respective_duration, str(age)])


def _icu_to_hospital(stati_durations, age):
    respective_duration = stati_durations[Configurator.icu_to_hospital_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > icu_to_hospital_df_max_time:
        return float(icu_to_hospital_df[str(age)].max())
    return float(icu_to_hospital_df.loc[respective_duration, str(age)])


def _diagnosis(stati_durations):
    respective_duration = stati_durations[Configurator.diagnosis_dependency]
    if respective_duration == 0:
        return 0
    if respective_duration > diagnosis_df_max_time:
        return 0
    return float(diagnosis_df.loc[respective_duration, 'probability'])
