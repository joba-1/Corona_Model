import matplotlib.pyplot as plt
import random
import pandas as pd
import numpy as np
import matplotlib.cm as cm

statusLabels = {
    'I': 'Infected',
    'S': 'Susceptible',
    'R': 'Recovered',
    'D': 'Dead'
}

defaultCmap = cm.get_cmap('Set3')
mainModelCmap = cm.get_cmap('Set1')  # for our statuses and flags
statusAndFlagsColors = {
    'I': mainModelCmap(0),  # red
    'S': mainModelCmap(1),  # blue
    'R': mainModelCmap(2),  # green
    'D': 'black',

    'WasInfected': mainModelCmap(0),  # red
    'Diagnosed': mainModelCmap(4),  # orange
    'Hospitalized': mainModelCmap(6),  # brown
    'ICUed': mainModelCmap(7),  # pink
}


def plot_infections_per_location_type_over_time(modeled_pop_world_obj, save_figure=False):
    infection_events = modeled_pop_world_obj.get_infection_event_information()
    infection_locations = list(infection_events['place_of_infection'])
    location_types = {str(l.ID): l.location_type for l in modeled_pop_world_obj.locations.values()
                      if str(l.ID) in infection_locations}
    unique_locs = list(set(list(location_types.values())))
    for i in infection_events.index:
        if not infection_events.loc[i, 'infected_by'] == 'nan':
            infection_events.loc[i,
                                 'place_of_infection_loc_type'] = location_types[infection_events.loc[i, 'place_of_infection']]

    simulation_timepoints = modeled_pop_world_obj.simulation_timecourse['time']
    colorindex = 0
    for loc in unique_locs:

        times = list(
            infection_events.loc[infection_events['place_of_infection_loc_type'] == loc, 'infection_time'])
        infections_in_loc_type_time_series = []
        for t in times:
            df1 = infection_events.loc[infection_events['place_of_infection_loc_type'] == loc, :]
            df2 = df1.loc[df1['infection_time'] == t, :]
            infections_in_loc_type_time_series.append(df2.shape[0])
        #plt.plot(times, infections_in_loc_type_time_series, label=loc)
        plt.scatter(times, infections_in_loc_type_time_series,
                    label=loc, color=defaultCmap(colorindex))
        colorindex += 1

    plt.xlim(left=0, right=max(list(simulation_timepoints)))
    plt.title('Infection events over time')
    plt.xlabel('Time [hours]')
    plt.ylabel('# Infection events')
    plt.legend()
    plt.show()
    if save_figure:
        plt.savefig('outputs/infections_per_time_per_loc_type.png')


def plot_infections_per_location_type(modeled_pop_world_obj, save_figure=False):
    infection_events = modeled_pop_world_obj.get_infection_event_information()
    infection_locations = list(infection_events['place_of_infection'])
    location_types = {str(l.ID): l.location_type for l in modeled_pop_world_obj.locations.values()
                      if str(l.ID) in infection_locations}
    unique_locs = list(set(list(location_types.values())))
    loc_infection_dict = dict(zip(unique_locs, [0]*len(unique_locs)))
    total_buildings_of_type = {}
    for i in unique_locs:
        total_buildings_of_type[i] = len([1 for j in modeled_pop_world_obj.locations.keys(
        ) if modeled_pop_world_obj.locations[j].location_type == i])
    for i in infection_events.index:
        if not infection_events.loc[i, 'infected_by'] == 'nan':
            respective_type = location_types[infection_events.loc[i, 'place_of_infection']]
            loc_infection_dict[respective_type] += 1/total_buildings_of_type[respective_type]
    x = np.arange(len(list(loc_infection_dict.keys())))
    fig, ax = plt.subplots()
    plt.bar(x, list(loc_infection_dict.values()), color=defaultCmap(0))
    plt.xticks(x, set(list(loc_infection_dict.keys())))
    plt.title('Total number of infections per location-type (relative to number of type)')
    plt.xlabel('Location-type')
    plt.ylabel('# Infection events')
    plt.show()


def plot_distribution_of_location_types(modeled_pop_world_obj):
    """
    plots the distribution of the location types that were initialized in this world
    :param modeled_pop_world_obj: obj of ModeledPopulatedWorld Class
    """
    location_counts = modeled_pop_world_obj.get_distribution_of_location_types()
    plt.bar(location_counts.keys(), location_counts.values(), color=defaultCmap(0))


def plot_initial_distribution_of_ages_and_infected(modeled_pop_world_obj, age_groups_step=10):
    age_groups_status_distribution = modeled_pop_world_obj.get_distribution_of_ages_and_infected(
        age_groups_step)
    width_of_bars = 0.50
    fig, ax = plt.subplots()
    fig_width_factor = 1/(age_groups_step/10)
    fig.set_figwidth(12*fig_width_factor)
    fig.set_figheight(7)
    tot_ppl = modeled_pop_world_obj.number_of_people
    age_groups = [str(age_group) for age_group in age_groups_status_distribution.index]
    per_of_inf = (age_groups_status_distribution['I']/tot_ppl)*100
    per_of_sus = (age_groups_status_distribution['S'] / tot_ppl) * 100
    ax.bar(age_groups, per_of_inf, width_of_bars,
           label=statusLabels['I'], color=statusAndFlagsColors['I'])
    ax.bar(age_groups, per_of_sus, width_of_bars, bottom=per_of_inf,
           label=statusLabels['S'], color=statusAndFlagsColors['S'])
    ax.set_title('Distribution of infected among age groups ({} people in total)'.format(tot_ppl))
    ax.set_ylabel('% of population')
    ax.set_xlabel('Age groups')
    ax.legend()
    plt.tight_layout()
    plt.show()


"""def plot_distribution_of_ages_and_infected(simulation_object, age_groups_step=10):
    age_groups_status_distribution = simulation_object.get_distribution_of_ages_and_infected(age_groups_step)
    width_of_bars = 0.50
    fig, ax = plt.subplots()
    fig.set_figwidth(12)
    fig.set_figheight(7)
    tot_ppl = simulation_object.number_of_people
    age_groups = [str(age_group) for age_group in age_groups_status_distribution.index]
    statuses_in_distribution = [str(stat_in_dist) for stat_in_dist in age_groups_status_distribution.columns]
    statuses_to_plot = [status for status in statusLabels.keys() if status in statuses_in_distribution]
    print(statuses_to_plot)
    ax.bar(age_groups,age_groups_status_distribution['I'],width_of_bars,label=statusLabels['I'])
    ax.bar(age_groups,age_groups_status_distribution['S'],width_of_bars,bottom=age_groups_status_distribution['I'],label=statusLabels['S'])
    ax.set_title('Distribution of infected among age groups ({} people in total)'.format(tot_ppl))
    ax.set_ylabel('Nr of people')
    ax.set_xlabel('Age groups')
    ax.legend()
    plt.tight_layout()
    plt.show()"""


def plot_status_timecourse(simulation_object, specific_statuses=None, specific_people=None, save_figure=False):
    """
    plots the time course for selected statuses
    :param simulation_object: obj of Simulation Class
    :param save_figure:  Bool. Flag for saving the figure as an image
    :param specific_statuses:   List. Optional arg for getting only a
    subset  of statuses. if not specified, will plot all available statuses
    """
    trajectories = simulation_object.get_status_trajectories(
        specific_statuses, specific_people=specific_people)
    assert set(statusLabels.keys()) >= set(trajectories.keys()
                                           ), "label(s) missing for existing statuses in the time "
    "course "
    simulation_timepoints = trajectories[list(trajectories.keys())[0]]['time'].values
    for status in trajectories.keys():
        plt.plot(simulation_timepoints,
                 trajectories[status][status].values, label=statusLabels[status], color=statusAndFlagsColors[status])

    if specific_people is None:
        plt.title('status trajectories')
    else:
        plt.title('status trajectories ('+specific_people+')')

    plt.xlabel('Time [hours]')
    plt.ylabel('# People')
    plt.legend()
    plt.show()
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
        plt.plot(simulation_timepoints, flag_sums[flag],
                 label=str(flag), color=statusAndFlagsColors[flag])
    plt.title('flags trajectories')
    plt.xlabel('Time [hours]')
    plt.ylabel('# People')
    plt.xlabel('Time [hours]')
    plt.legend()
    plt.show()
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
        assert available_loc_types >= set(
            specific_types), " specific types provided (" + str(specific_types) + ") "
        "do not match those in the timecourse (" + str(available_loc_types) + " )"
        loc_types = specific_types
    else:
        loc_types = available_loc_types
    color_index = 0
    for loc_type in loc_types:
        df = locations_df[['time', 'loc_type']]
        zero_occupancy_array = df['time'].copy().unique()
        df_of_location = df[df['loc_type'] == loc_type].rename(columns={'loc_type': loc_type})
        time_grouped_location_count = df_of_location.groupby('time').count()
        zero_occupancy_df = pd.DataFrame({'time': zero_occupancy_array, loc_type: np.zeros(
            len(zero_occupancy_array))}).set_index('time')
        merged_df = time_grouped_location_count.merge(zero_occupancy_df, left_index=True, right_index=True,
                                                      suffixes=('', '_zeros'), how='right').fillna(0)
        plt.plot(list(merged_df.index.values),
                 merged_df[loc_type], label=loc_type, color=defaultCmap(color_index))
        color_index += 1
    plt.title('location occupancy trajectories')
    plt.xlabel('Time [hours]')
    plt.ylabel('# People')
    plt.legend()
    plt.show()
    if save_figure:
        plt.savefig('outputs/loc_types_occupancy_plot.png')


def plot_status_at_location(simulation_object, save_figure=False):
    loc_stat = simulation_object.get_location_and_status()
    n = len(loc_stat['location_type'].unique())
    df_ls = loc_stat.groupby(['location_type', 'time']).sum()
    status_at_loc = df_ls.reset_index().drop(
        ['x_coordinate', 'y_coordinate', 'loc'], axis=1).groupby('location_type')

    fig, axes = plt.subplots(2, int(n/2)+n % 2, figsize=(8, 8))

    zero_occupancy_array = loc_stat['time'].copy().unique()
    zero_occupancy_df = pd.DataFrame({'time': zero_occupancy_array,
                                      'D': np.zeros(len(zero_occupancy_array)),
                                      'I': np.zeros(len(zero_occupancy_array)),
                                      'R': np.zeros(len(zero_occupancy_array)),
                                      'S': np.zeros(len(zero_occupancy_array)),
                                      })

    for k, (stat, loc) in enumerate(status_at_loc):

        loc1 = loc.reset_index().set_index('time')
        merged_df = loc1.merge(zero_occupancy_df, left_index=True,
                               right_index=True, suffixes=('', '_zeros'), how='right').fillna(0)
        col = k % 2
        row = int(k/2)
        ax = axes[col, row]
        cols_to_plot = ['D', 'I', 'R', 'S']
        merged_df.plot(y=cols_to_plot, ax=ax, color=[
                       statusAndFlagsColors[st] for st in cols_to_plot])
        ax.set_title(stat)
        ax.set_xlabel('Time [hours]')

    plt.tight_layout()

    # for k,(stat,loc) in enumerate(status_at_loc):

    #    loc.set_index('time')
    #    merged_df = loc.reset_index().set_index('time').merge(zero_occupancy_df, left_index=True, right_index=True,suffixes=('', '_zeros'), how='right').fillna(0)
    #    #merged_df.drop('time', axis=1).reset_index()
    #    merged_df.sort_values('time', inplace=True)
    # plt.xlim(0,200)
    #    col = k%2; row = int(k/2)
    #    ax = axes[col,row]
    #    for i,status in enumerate(['I','R','D','S']):
    #        #ax.plot(list(loc['time'].values).append(times_0), list(loc[status].values).append(zeros))
    #        merged_df.plot(ax=ax,x='time', y=status, kind='line', label=status, color=cmap(i))
    #        ax.set_title(stat)
    #       ax.set_xlabel('Time [hours]')

    # plt.tight_layout()
    plt.show()
    if save_figure:
        plt.savefig('outputs/loc_types_occupancy_plot.png')


def map_status_at_loc(simulation_object, save_figure=False, time_steps=2):

    loc_stat = simulation_object.get_location_and_status()

    for time in range(time_steps):
        loc_stat_t = loc_stat[loc_stat['time'] == time]

        plt.figure(figsize=(10, 10))
        for k, stat in enumerate(['R', 'S', 'I', 'D']):
            plt.subplot(2, 2, k+1)
            plt.title(stat)
            plt.scatter(loc_stat_t['x_coordinate'], loc_stat_t['y_coordinate'], s=20 *
                        loc_stat_t[stat], alpha=0.3, label=stat, color=statusAndFlagsColors[stat])
        plt.suptitle('status at time '+str(time))
        plt.tight_layout()
        plt.legend()

        if save_figure:
            plt.savefig('plots/loc_t_'+str(time)+'.png')


def plot_distributions_of_durations(simulation_object, save_figure=False):
    """
    plots the distributions of the total duration of the infection,
    the time from infection to hospitalization,
    the times from hospitalization to death or recovery
    and the time from hospitalisation to ICU.
    :param save_figure:  Bool. Flag for saving the figure as an image
    """
    simulation_object.get_durations().hist(color=defaultCmap(0))
    plt.tight_layout()
    plt.show()
    if save_figure:
        plt.savefig('outputs/duration_distributions.png')
