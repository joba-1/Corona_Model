import virusPropagationModel as vPM
import pandas as pd
import numpy as np
import os


def get_r_eff_timecourse_from_human_timecourse(time_course_source, sliding_window_size,sliding_step_size=1):
    source_is_csv = type(time_course_source) is str and os.path.exists(time_course_source)
    source_is_sim_obj = isinstance(time_course_source, vPM.Simulation)
    if source_is_csv:
        humans_df = pd.read_csv(time_course_source, sep=';')
    elif source_is_sim_obj:
        stati_list = time_course_source.statuses_in_timecourse
        humans_df = time_course_source.simulation_timecourse.copy()
        for i in range(len(stati_list)):
            humans_df.loc[humans_df['status'] == i, 'status'] = stati_list[i]
        humans_df.set_index('time')
    else:
        raise ValueError('the time course source should be a either a csv of a human infection time course '
                         'or a simulation object')

    successful_spreading_cases_df = humans_df[humans_df['Infection_event'] == 1].drop(
        columns=['Infection_event', 'loc', 'Temporary_Flags', 'Cumulative_Flags'])
    infected_humans_df = successful_spreading_cases_df[successful_spreading_cases_df['status'] == 'S'].drop(
        columns=['status'])
    infected_humans_df.rename(columns={"h_ID": "infected_ID", "Interaction_partner": "infected_by"},inplace=True)
    infecting_humans_df = successful_spreading_cases_df[successful_spreading_cases_df['status'] == 'I'].drop(
        columns=['status'])
    infecting_humans_df.rename(columns={"Interaction_partner": "infected_ID", "h_ID": "infected_by"},inplace=True)
    successful_spreaders_df = pd.concat([infected_humans_df, infecting_humans_df], ignore_index=True)

    spreader_reproduction_numbers = successful_spreaders_df.groupby('infected_by').count().infected_ID.to_frame().rename(columns={"infected_ID": "reproduction_nr"})
    spreader_reproduction_numbers['infected_ID'] = spreader_reproduction_numbers.index
    spreader_reproduction_numbers.reset_index(drop=True, inplace=True)

    closed_spreader_cases_IDs = np.unique(humans_df[humans_df.status.isin(['R', 'D'])].h_ID.values) # makes sure we dont count people that never stopped being infectious (unclosed cases)
    closed_possible_spreaders = humans_df.loc[(humans_df.status == 'I') &
                                              (humans_df.h_ID.isin(closed_spreader_cases_IDs)),
                                              ['time','h_ID']].rename(columns={"h_ID": "infected_ID"})

    closed_spreaders_with_r = closed_possible_spreaders.merge(spreader_reproduction_numbers, on='infected_ID', how='left')
    closed_spreaders_with_r['reproduction_nr'] = closed_spreaders_with_r['reproduction_nr'].fillna(0.0).astype(int)

    times = np.arange(sliding_window_size, np.max(closed_spreaders_with_r.time) + 1, sliding_step_size)

    r_eff = np.zeros(len(times))
    stds_r_eff = np.zeros(len(times))

    for i,t in enumerate(times):
        time_window_reproduction_nrs = closed_spreaders_with_r.loc[(closed_spreaders_with_r['time'] >= t-sliding_window_size) & (closed_spreaders_with_r['time']<= t),['reproduction_nr']]
        r_eff[i] = time_window_reproduction_nrs.mean()
        stds_r_eff[i] = time_window_reproduction_nrs.std()

    return times, r_eff, stds_r_eff
