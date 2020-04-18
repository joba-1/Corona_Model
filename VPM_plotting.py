import matplotlib.pyplot as plt
import random
import pandas as pd
import numpy as np

plot_stops_program = False


def plot_distribution_of_location_types(modeled_pop_world_obj):
    """
    plots the distribution of the location types that were initialized in this world
    :param modeled_pop_world_obj: obj of ModeledPopulatedWorld Class
    """
    location_counts = modeled_pop_world_obj.get_distribution_of_location_types()
    plt.bar(location_counts.keys(), location_counts.values())


def plot_status_timecourse(simulation_object, specific_statuses=None, save_figure=False):
    """
    plots the time course for selected statuses
    :param simulation_object: obj of Simulation Class
    :param save_figure:  Bool. Flag for saving the figure as an image
    :param specific_statuses:   List. Optional arg for getting only a
    subset  of statuses. if not specified, will plot all available statuses
    """
    labels = {
        'S': 'Susceptible',
        'R': 'Recovered',
        'I': 'Infected',
        'D': 'Dead'
    }
    trajectories = simulation_object.get_status_trajectories(specific_statuses)
    assert set(labels.keys()) >= set(trajectories.keys()), "label(s) missing for existing statuses in the time " \
                                                           "course "
    simulation_timepoints = trajectories[list(trajectories.keys())[0]]['time'].values
    for status in trajectories.keys():
        plt.plot(simulation_timepoints,
                 trajectories[status][status].values, label=labels[status])

    plt.title('status trajectories')
    plt.legend()
    plt.show(block=plot_stops_program)
    if save_figure:
        plt.savefig('outputs/status_plot.png')


def plot_flags_timecourse(simulation_object, specific_flags=None, save_figure=False):
    """
    plots the time course for the selected flags
    :param specific_flags: list. given flags to be included in the plot
    :param save_figure: bool. Flag for saving the figure as an image
    """
    if specific_flags is None:
        cols = list(simulation_object.simulation_timecourse.columns)
        random_person = random.choice(list(simulation_object.people))
        status_cols = random_person.get_status().keys()
        cols_of_interest = [ele for ele in cols if ele not in list(status_cols)]
    else:
        cols_of_interest = specific_flags + ['time']
    df = simulation_object.simulation_timecourse[set(cols_of_interest)].copy()
    gdf = df.groupby('time')
    flag_sums = gdf.sum()
    simulation_timepoints = list(gdf.groups.keys())
    for flag in flag_sums.columns:
        plt.plot(simulation_timepoints, flag_sums[flag], label=str(flag))
    plt.title('flags trajectories')
    plt.legend()
    plt.show(block=plot_stops_program)
    if save_figure:
        plt.savefig('outputs/flags_plot.png')


def plot_location_type_occupancy_timecourse(simulation_object, specific_types=None, save_figure=False):
    """
    plots the occupancy of the location types in the time course
    :param specific_types: list. List of specific types to plot (only)
    :param save_figure: bool. Whether to save the figure
    """
    locations_df = simulation_object.get_location_with_type_trajectory()
    available_loc_types = set(locations_df['loc_type'])
    if specific_types is not None:
        assert available_loc_types >= set(specific_types), \
            " specific types provided (" + str(specific_types) + ") " \
                                                                 "do not match those in the timecourse (" + str(
                available_loc_types) + " )"
        loc_types = specific_types
    else:
        loc_types = available_loc_types
    for loc_type in loc_types:
        df = locations_df[['time', 'loc_type']]
        zero_occupancy_array = df['time'].copy().unique()
        df_of_location = df[df['loc_type'] == loc_type].rename(columns={'loc_type': loc_type})
        time_grouped_location_count = df_of_location.groupby('time').count()
        zero_occupancy_df = pd.DataFrame({'time': zero_occupancy_array, loc_type: np.zeros(
            len(zero_occupancy_array))}).set_index('time')
        merged_df = time_grouped_location_count.merge(zero_occupancy_df, left_index=True, right_index=True,
                                                      suffixes=('', '_zeros'), how='right').fillna(0)
        plt.plot(list(merged_df.index.values), merged_df[loc_type], label=loc_type)
    plt.title('location occupancy trajectories')
    plt.legend()
    plt.show(block=plot_stops_program)
    if save_figure:
        plt.savefig('outputs/loc_types_occupancy_plot.png')


def plot_distributions_of_durations(simulation_object, save_figure=False):
    """
    plots the distributions of the total duration of the infection,
    the time from infection to hospitalization,
    the times from hospitalization to death or recovery
    and the time from hospitalisation to ICU.
    :param save_figure:  Bool. Flag for saving the figure as an image
    """
    simulation_object.get_durations().hist()
    plt.tight_layout()
    plt.show(block=plot_stops_program)
    if save_figure:
        plt.savefig('outputs/duration_distributions.png')
