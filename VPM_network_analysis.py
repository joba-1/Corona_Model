import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import time
import glob
import warnings

def helper_return_wsize_wstep_from_file_path(file_path):
    assert 'WSIZE' in file_path and 'WSTEP' in file_path, 'window size and step have to be given in the file name'
    relevant_string = file_path.split('(WSIZE')[1]
    wsize, relevant_str_for_step = relevant_string.split('_WSTEP')
    wstep = relevant_str_for_step.split(')')[0]
    return wsize, wstep

def get_r_eff_timecourse_from_human_timecourse(time_course_source, sliding_window_size,sliding_step_size=1):
    source_is_csv = type(time_course_source) is str and os.path.exists(time_course_source)
    source_is_sim_obj = 'Simulation' in str(type(time_course_source))
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
    closed_possible_spreaders = humans_df.loc[(humans_df.status == 'I') &  # we only count the actively infected as spreaders
                                              (humans_df.h_ID.isin(closed_spreader_cases_IDs)),
                                              ['time','h_ID']].rename(columns={"h_ID": "infected_ID"})

    closed_spreaders_with_r = closed_possible_spreaders.merge(spreader_reproduction_numbers, on='infected_ID', how='left')
    closed_spreaders_with_r['reproduction_nr'] = closed_spreaders_with_r['reproduction_nr'].fillna(0.0).astype(int)

    assert sliding_window_size<=np.max(closed_spreaders_with_r.time), "the sliding window size it more then the time of the last infection in the time course  ! "
    times = np.arange(sliding_window_size, np.max(closed_spreaders_with_r.time) + 1, sliding_step_size)

    r_effs = np.zeros(len(times))
    stds_r_eff = np.zeros(len(times))

    for i,t in enumerate(times):
        time_window_reproduction_nrs = closed_spreaders_with_r.loc[(closed_spreaders_with_r['time'] >= t-sliding_window_size) & (closed_spreaders_with_r['time']<= t),['reproduction_nr']]
        r_effs[i] = time_window_reproduction_nrs.mean()
        stds_r_eff[i] = time_window_reproduction_nrs.std()

    return times, r_effs, stds_r_eff


def export_r_eff_timecourse_as_csv(time_course_source, sliding_window_size,sliding_step_size=1,saved_csv_identifier='unnamed'):
    times, r_effs, stds_r_eff = get_r_eff_timecourse_from_human_timecourse(time_course_source, sliding_window_size, sliding_step_size=sliding_step_size)
    output_df = pd.DataFrame({'time':times,'r_eff':r_effs,'stds_r_eff':stds_r_eff})
    output_df.to_csv('outputs/' + saved_csv_identifier + '-r_eff_timecourse(WSIZE{}_WSTEP{}).csv'.format(sliding_window_size, sliding_step_size))


def plot_r_eff_from_csvs_or_sim_object(timecourse_source, from_sim_obj_sliding_window_size=None, from_sim_obj_sliding_step_size=1,timecourses_source_is_list_of_csvs=False,label_list_for_csvs=None,plot_std=True,save_fig=True):
    if 'Simulation' in str(type(timecourse_source)):  # when the source is a sim. obj.
        assert from_sim_obj_sliding_window_size is not None, "the desired sliding window size has to be specified under from_sim_obj_sliding_window_size"
        times, r_effs, stds_r_eff = get_r_eff_timecourse_from_human_timecourse(timecourse_source, from_sim_obj_sliding_window_size,
                                                                               sliding_step_size=1)
        r_eff_timecourse_dfs = [pd.DataFrame({'time': times, 'r_eff': r_effs, 'stds_r_eff': stds_r_eff})]
        ylabels = ['r_eff']
        sliding_window_size = from_sim_obj_sliding_window_size
        sliding_step_size = from_sim_obj_sliding_step_size
        different_windows = False
    elif type(timecourse_source) == list:  # when the source is a list paths or identifiers of pre-calcualated r_eff timecourse csv files
        assert type(timecourse_source[0]) == str, "the csvs have to be given as names or paths (strings)"
        r_eff_timecourse_dfs=[]
        ylabels = []
        wsizes,wsteps = [],[]
        for i,csv in enumerate(timecourse_source):
            if os.path.exists(csv):
                r_eff_timecourse_dfs.append(pd.read_csv(csv))
                path_to_folder, file = os.path.split(csv)
                file_name = str(file.split('-r_eff')[0])
                ylabels.append(file_name.replace("_"," "))
                window_info = helper_return_wsize_wstep_from_file_path(file)
                wsizes.append(window_info[0])
                wsteps.append(window_info[1])
            elif glob.glob('outputs/'+csv+'*r_eff_timecourse*'):
                path_in_list = glob.glob('outputs/' + csv + '*r_eff_timecourse*')
                assert len(path_in_list) == 1, 'more than one csv for for a given source name'
                r_eff_timecourse_dfs.append(pd.read_csv(path_in_list[0]))
                ylabels.append(csv.replace("_"," "))
                window_info = helper_return_wsize_wstep_from_file_path(path_in_list[0])
                wsizes.append(window_info[0])
                wsteps.append(window_info[1])
            else:
                raise ValueError('input path list ({}) was not provided in the expected format or does not exist'.format(csv))

        if len(set(wsizes)) != 1 or len(set(wsteps)) != 1:
            warnings.warn('Not all window sizes and step sizes in these trajectories match! Window sizes and steps will be added to the labels')
            different_windows = True
            for i in range(len(ylabels)):
                ylabels[i] = ylabels[i] + ' ({}, {})'.format(wsizes[i], wsteps[i])
        else:
            different_windows = False
            sliding_window_size, sliding_step_size = wsizes[0], wsteps[0]
        if label_list_for_csvs is not None:
            assert len(label_list_for_csvs) == len(timecourse_source), 'nr of labels and nr of trajectories does not match'
            ylabels.clear()
            ylabels = label_list_for_csvs
    else:
        raise ValueError('The given timecourse_source is not a csv list or a simulation object')

    cmap = cm.get_cmap("Set2")
    plt.figure(figsize=(10, 10))

    if not different_windows:
        for i, tc_df in enumerate(r_eff_timecourse_dfs):
            plt.plot(tc_df['time'], tc_df['r_eff'], label=ylabels[i], color=cmap(i),linewidth=3)
            if plot_std:
                std = tc_df['stds_r_eff']
                plt.fill_between(tc_df['time'],tc_df['r_eff']-std,tc_df['r_eff']+std,color=cmap(i),alpha=0.2)
            plt.xlabel("Time [h]")
            plt.ylabel("Effective reproduction number $R_\mathrm{{eff}}$")
        plt.legend(ylabels, loc='best', frameon=False,title='Sliding window size = {} day(s), step size = {} h'.format(str(round(float(sliding_window_size) / 24, 1)),str(sliding_step_size)))
    else:
        for i, tc_df in enumerate(r_eff_timecourse_dfs):
            plt.plot(tc_df['time'], tc_df['r_eff'],label=ylabels[i],color=cmap(i),linewidth=3)
            if plot_std:
                std = tc_df['stds_r_eff']
                plt.fill_between(tc_df['time'],tc_df['r_eff']-std,tc_df['r_eff']+std,color=cmap(i),alpha=0.2)
            plt.xlabel("Time [h]")
            plt.ylabel("Effective reproduction number $R_\mathrm{{eff}}$")
        plt.legend(ylabels, loc='best', frameon=False,title='Based on varying window sizes and steps (WSIZE[h],WSTEP[h])')

    plt.axhline(y=1., color='gray', linestyle='--')

    plt.show()

    if save_fig:
        timestr = '_' + time.strftime("%d-%m-%Y_%H-%M-%S")
        plt.savefig('outputs/r_eff_timecourse'+timestr+'.png', dpi=200)