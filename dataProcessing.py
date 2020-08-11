import pandas as pd
from configure_simulation import Simulation_Configuration

Configurator = Simulation_Configuration()

# read data
infectivity_df = pd.read_csv(Configurator.infectivity_df)
hospitalisation_df = pd.read_csv(Configurator.hospitalisation_df)
to_icu_df = pd.read_csv(Configurator.to_icu_df)
icu_to_hospital_df = pd.read_csv(Configurator.icu_to_hospital_df)
diagnosis_df = pd.read_csv(Configurator.diagnosis_df)

recovery_from_undiagnosed_df = pd.read_csv(Configurator.recovery_from_undiagnosed_df)
recovery_from_diagnosed_df = pd.read_csv(Configurator.recovery_from_diagnosed_df)
recovery_from_hospitalized_df = pd.read_csv(Configurator.recovery_from_hospitalized_df)
death_from_undiagnosed_df = pd.read_csv(Configurator.death_from_undiagnosed_df)
death_from_diagnosed_df = pd.read_csv(Configurator.death_from_diagnosed_df)
death_from_hospitalized_df = pd.read_csv(Configurator.death_from_hospitalized_df)
death_from_icu_df = pd.read_csv(Configurator.death_from_icu_df)

# compute vars for run time
infectivity_df_max_time = infectivity_df['Time-steps'].max()
hospitalisation_df_max_time = hospitalisation_df['Time-steps'].max()
to_icu_df_max_time = to_icu_df['Time-steps'].max()
icu_to_hospital_df_max_time = icu_to_hospital_df['Time-steps'].max()
diagnosis_df_max_time = diagnosis_df['Time-steps'].max()
recovery_from_undiagnosed_df_max_time = recovery_from_undiagnosed_df['Time-steps'].max()
recovery_from_diagnosed_df_max_time = recovery_from_diagnosed_df['Time-steps'].max()
recovery_from_hospitalized_df_max_time = recovery_from_hospitalized_df['Time-steps'].max()
death_from_undiagnosed_df_max_time = death_from_undiagnosed_df['Time-steps'].max()
death_from_diagnosed_df_max_time = death_from_diagnosed_df['Time-steps'].max()
death_from_hospitalized_df_max_time = death_from_hospitalized_df['Time-steps'].max()
death_from_icu_df_max_time = death_from_icu_df['Time-steps'].max()

# set indexes for run time
infectivity_df.set_index('Time-steps', inplace=True)
hospitalisation_df.set_index('Time-steps', inplace=True)
to_icu_df.set_index('Time-steps', inplace=True)
icu_to_hospital_df.set_index('Time-steps', inplace=True)
diagnosis_df.set_index('Time-steps', inplace=True)
recovery_from_undiagnosed_df.set_index('Time-steps', inplace=True)
recovery_from_diagnosed_df.set_index('Time-steps', inplace=True)
recovery_from_hospitalized_df.set_index('Time-steps', inplace=True)
death_from_undiagnosed_df.set_index('Time-steps', inplace=True)
death_from_diagnosed_df.set_index('Time-steps', inplace=True)
death_from_hospitalized_df.set_index('Time-steps', inplace=True)
death_from_icu_df.set_index('Time-steps', inplace=True)


def _infectivity(stati_durations):
    respective_duration = stati_durations[Configurator.infectivity_dependency]
    if respective_duration == 0:
        return 0
    if respective_duration > infectivity_df_max_time:
        return 0
    return float(infectivity_df.loc[respective_duration, 'Probability_to_infect'])


def _recovery_from_undiagnosed(stati_durations):
    respective_duration = stati_durations[Configurator.recovery_from_undiagnosed_dependency]
    if respective_duration == 0:
        return 0
    if respective_duration > recovery_from_undiagnosed_df_max_time:
        return float(recovery_from_undiagnosed['recover probability'].max())
    return float(recovery_from_undiagnosed_df.loc[respective_duration, 'recover probability'])


def _recovery_from_diagnosed(stati_durations):
    respective_duration = stati_durations[Configurator.recovery_from_diagnosed_dependency]
    if respective_duration == 0:
        return 0
    if respective_duration > recovery_from_diagnosed_df_max_time:
        return float(recovery_from_diagnosed['recover probability'].max())
    return float(recovery_from_diagnosed_df.loc[respective_duration, 'recover probability'])


def _recovery_from_hospitalized(stati_durations):
    respective_duration = stati_durations[Configurator.recovery_from_hospitalized_dependency]
    if respective_duration == 0:
        return 0
    if respective_duration > recovery_from_hospitalized_df_max_time:
        return float(recovery_from_hospitalized['recover probability'].max())
    return float(recovery_from_hospitalized_df.loc[respective_duration, 'recover probability'])


def _hospitalisation(stati_durations, age):
    respective_duration = stati_durations[Configurator.hospitalisation_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > hospitalisation_df_max_time:
        return 0
    return float(hospitalisation_df.loc[respective_duration, str(age)])


def _undiagnosed_death_risk(stati_durations, age):
    respective_duration = stati_durations[Configurator.death_from_undiagnosed_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > death_from_undiagnosed_df_max_time:
        return 0
    return float(death_from_undiagnosed_df.loc[respective_duration, str(age)])


def _diagnosed_death_risk(stati_durations, age):
    respective_duration = stati_durations[Configurator.death_from_diagnosed_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > death_from_diagnosed_df_max_time:
        return 0
    return float(death_from_diagnosed_df.loc[respective_duration, str(age)])


def _hospital_death_risk(stati_durations, age):
    respective_duration = stati_durations[Configurator.death_from_hospitalized_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > death_from_hospitalized_df_max_time:
        return 0
    return float(death_from_hospitalized_df.loc[respective_duration, str(age)])


def _icu_death_risk(stati_durations, age):
    respective_duration = stati_durations[Configurator.death_from_icu_dependency]
    if age > 99:
        age = 99
    if respective_duration == 0:
        return 0
    if respective_duration > death_from_icu_df_max_time:
        return 0
    return float(death_from_icu_df.loc[respective_duration, str(age)])


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
