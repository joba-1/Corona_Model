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


def export_r_eff_timecourse_as_csv(time_course_source, sliding_window_size, sliding_step_size=1, saved_csv_identifier='unnamed'):
    times, r_effs, stds_r_eff = get_r_eff_timecourse_from_human_timecourse(
        time_course_source, sliding_window_size, sliding_step_size=sliding_step_size)
    output_df = pd.DataFrame({'time': times, 'r_eff': r_effs, 'stds_r_eff': stds_r_eff})
    output_df.to_csv('outputs/simulation_results/' + saved_csv_identifier +
                     '-r_eff_timecourse(WSIZE{}_WSTEP{}).csv'.format(sliding_window_size, sliding_step_size))


def plot_r_eff_from_sim_object(sim_obj, sliding_window_size=None, sliding_step_size=1, plot_std=True, save_fig=False):
    assert sliding_window_size is not None, "the desired sliding window size has to be specified under from_sim_obj_sliding_window_size"
    times, r_effs, stds_r_eff = get_r_eff_timecourse_from_human_timecourse(timecourse_source, from_sim_obj_sliding_window_size,
                                                                           sliding_step_size=1)
    r_eff_timecourse_dfs = [pd.DataFrame(
        {'time': times, 'r_eff': r_effs, 'stds_r_eff': stds_r_eff})]
    ylabels = ['r_eff']
    sliding_window_size = from_sim_obj_sliding_window_size
    sliding_step_size = from_sim_obj_sliding_step_size
    different_windows = False

    cmap = cm.get_cmap("Set2")
    plt.figure(figsize=(10, 10))

    if not different_windows:
        for i, tc_df in enumerate(r_eff_timecourse_dfs):
            plt.plot(tc_df['time'], tc_df['r_eff'], label=ylabels[i], color=cmap(i), linewidth=3)
            if plot_std:
                std = tc_df['stds_r_eff']
                plt.fill_between(tc_df['time'], tc_df['r_eff']-std,
                                 tc_df['r_eff']+std, color=cmap(i), alpha=0.2)
            plt.xlabel("Time [h]")
            plt.ylabel("Effective reproduction number $R_\mathrm{{eff}}$")
        plt.legend(ylabels, loc='best', frameon=False, title='Sliding window size = {} day(s), step size = {} h'.format(
            str(round(float(sliding_window_size) / 24, 1)), str(sliding_step_size)))
    else:
        for i, tc_df in enumerate(r_eff_timecourse_dfs):
            plt.plot(tc_df['time'], tc_df['r_eff'], label=ylabels[i], color=cmap(i), linewidth=3)
            if plot_std:
                std = tc_df['stds_r_eff']
                plt.fill_between(tc_df['time'], tc_df['r_eff']-std,
                                 tc_df['r_eff']+std, color=cmap(i), alpha=0.2)
            plt.xlabel("Time [h]")
            plt.ylabel("Effective reproduction number $R_\mathrm{{eff}}$")
        plt.legend(ylabels, loc='best', frameon=False,
                   title='Based on varying window sizes and steps (WSIZE[h],WSTEP[h])')

    plt.axhline(y=1., color='gray', linestyle='--')

    plt.show()

    if save_fig:
        timestr = '_' + time.strftime("%d-%m-%Y_%H-%M-%S")
        plt.savefig('outputs/plots/r_eff_timecourse'+timestr+'.png', dpi=200)
