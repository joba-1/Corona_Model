import random
import time

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.cm as cm
import seaborn as sns

from collections import OrderedDict as ordered_dict

statusLabels = {
    'I': 'Infected',
    'S': 'Susceptible',
    'R': 'Recovered',
    'D': 'Dead'
}

defaultCmap = cm.get_cmap('Set2')  # as default for undefined objects
mainModelCmap = cm.get_cmap('Set1')  # for our statuses and flags
statusAndFlagsColors = {
    'I': mainModelCmap(0),  # red
    'S': mainModelCmap(1),  # blue
    'R': mainModelCmap(2),  # green
    'D': 'black',

    'IsInfected': mainModelCmap(0),  # red
    'WasInfected': mainModelCmap(0),  # red
    'WasDiagnosed': mainModelCmap(4),  # blue
    'Diagnosed': mainModelCmap(4),  # orange
    'Hospitalized': mainModelCmap(6),  # brown
    'WasHospitalized': mainModelCmap(6),
    'WasICUed': mainModelCmap(7),
    'ICUed': mainModelCmap(7),  # pink
}
locationsCmap1 = cm.get_cmap('Dark2')  # for our locations
locationsCmap2 = cm.get_cmap('tab20')
locationTypeColors = {
    'home': locationsCmap1(0),  # aquamarine
    'public': locationsCmap1(2),  # purple-blue
    'work': locationsCmap1(3),  # deep pink
    'hospital': locationsCmap1(5),  # mustard yellow
    'school': locationsCmap2(17),  # olive green - khaki
    'morgue': locationsCmap1(7),  # gray
    'mixing_loc': locationsCmap1(1)
}
scheduleTypeColors = {
    'adult': defaultCmap(0),
    'medical_professional': defaultCmap(1),
    'pensioner': defaultCmap(2),
    'public_worker': defaultCmap(3),
    'teacher': defaultCmap(4),
    'under_age': defaultCmap(5),
}


def plot_contact_distributions_as_violins(Contact_DF, specific_agent_types=None, timesteps_per_aggregate=168, ScheduleType_name_map=None, ax=None):

    if specific_agent_types == None:
        agent_types_forplot = list(Contact_DF['schedule_type'].unique())
    else:
        if type(specific_agent_types) is list:
            agent_types_forplot = specific_agent_types
        elif type(specific_agent_types) is str:
            agent_types_forplot = [specific_agent_types]

    if ScheduleType_name_map == None:
        dict(zip(agent_types_forplot, agent_types_forplot))

    DF_interactions = pd.DataFrame()
    DF_unique = pd.DataFrame()
    DF_interactions['all'] = Contact_DF['interactions']/timesteps_per_aggregate
    DF_unique['all'] = Contact_DF['unique_interactions']/timesteps_per_aggregate

    for t in agent_types_forplot:
        DF_interactions[t] = Contact_DF.loc[Contact_DF['schedule_type']
                                            == t, 'interactions']/timesteps_per_aggregate
        DF_unique[t] = Contact_DF.loc[Contact_DF['schedule_type']
                                      == t, 'unique_interactions']/timesteps_per_aggregate

    DF_interactions['Type'] = ['Total']*DF_interactions.shape[0]
    DF_unique['Type'] = ['Unique']*DF_unique.shape[0]

    df_type_i = pd.concat([DF_interactions['all'], DF_interactions['Type']], axis=1)
    df_type_i.columns = ['N', 'Type']
    df_type_i['schedule_type'] = ['All']*df_type_i.shape[0]

    df_type_u = pd.concat([DF_unique['all'], DF_unique['Type']], axis=1)
    df_type_u.columns = ['N', 'Type']
    df_type_u['schedule_type'] = ['All']*df_type_u.shape[0]

    out = pd.concat([df_type_i, df_type_u], axis=0)
    for i in agent_types_forplot:
        df_type_i = pd.concat([DF_interactions[i], DF_interactions['Type']], axis=1)
        df_type_i.columns = ['N', 'Type']
        df_type_i['schedule_type'] = [ScheduleType_name_map[i]]*df_type_i.shape[0]

        df_type_u = pd.concat([DF_unique[i], DF_unique['Type']], axis=1)
        df_type_u.columns = ['N', 'Type']
        df_type_u['schedule_type'] = [ScheduleType_name_map[i]]*df_type_u.shape[0]

        df_to_append = pd.concat([df_type_i, df_type_u], axis=0)
        out = pd.concat([out, df_to_append], axis=0)

    if not ax:
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))

    # v = seaborn.violinplot(data=outDF,hue='Type',split=True,x='schedule_type',y='N', inner=None,scale='area',scale_hue=True,linewidth=1,palette=['teal','cornflowerblue'])
    ax = sns.violinplot(data=out, hue='Type', split=True, x='schedule_type', y='N', inner=None,
                        scale='area', scale_hue=True, linewidth=1, palette=['royalblue', 'lightblue'])

    ax.set_title('Total and unique interactions')
    ax.set_xlabel('')
    ax.set_ylabel('Interactions per hour')
    ax.legend(loc='upper right', frameon=False)
    return ax


def plot_infections_per_location_type_over_time(modeled_pop_world_obj, save_figure=False):
    df = modeled_pop_world_obj.get_infections_per_location_type_over_time()
    fig, ax = plt.subplots()
    for loc_type in df['loc_type'].unique():
        df_l = df[df['loc_type'] == loc_type]
        sc = ax.scatter(df_l['time'], df_l['number_of_infection_events'], marker='o',
                        color=locationTypeColors[loc_type], alpha=0.3, label=loc_type)
    plt.legend()
    plt.title('Infection events over time')
    plt.xlabel('Time [hours]')
    plt.ylabel('# Infection events')
    plt.legend()
    plt.show()

    if save_figure:
        plt.savefig('output/plots/infections_per_time_per_loc_type.png')


def plot_infections_per_location_type(sim_obj, save_figure=False, relative=False, ax=None):
    """
    plot infections per location type in a bar plot
    :params: save_figure: bool,
                relative: bool as a fraction of all infections,
                      ax: ax object to plot on if None figure is created
    :returns: ax
    """
    if not ax:
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    inf_loc_series = sim_obj.get_infections_per_location_type(
        relative=relative).mean()
    df = inf_loc_series.to_frame('values')
    df.sort_index(inplace=True)
    colors = [locationTypeColors[loc] for loc in df.index.values]
    df['values'].plot(kind='bar', color=colors, ax=ax)
    ax.set_title('Infections per location-type')
    ax.set_xlabel('Location-type')
    ax.set_ylabel(' Infection events')
    return ax, df


def plot_infections_per_schedule_type(sim_obj, relative=False, fraction_most_infect_p=1,
                                      ax=None, save_figure=False, **kwargs):
    """
    plot infections per schedule type in a bar plot
    :params: save_figure: bool,
                relative: bool as a fraction of all infections,
                      ax: ax object to plot on if None figure is created
    :returns: ax
    """
    if not ax:
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    inf_sched_series = sim_obj.get_infections_per_schedule_type(fraction_most_infectious=fraction_most_infect_p,
                                                                relative=relative).mean()
    df = inf_sched_series.to_frame('values')
    df.sort_index(inplace=True)
    colors = [scheduleTypeColors[schedule_type]
              for schedule_type in df.index.values]
    df['values'].plot(kind='bar', color=colors, ax=ax)
    ax.set_title('Infections per schedule-type')
    ax.set_xlabel('schedule-type')
    ax.set_ylabel(' Infection events')
    return ax, df


def plot_distribution_of_location_types(modeled_pop_world_obj,
                                        kind='bar',
                                        ax=None,
                                        save_fig=False,
                                        **kwargs):
    """
    plots the distribution of the location types that were initialized in this world
    :param modeled_pop_world_obj: obj of ModeledPopulatedWorld Class
    """
    if not ax:
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    loc_series = modeled_pop_world_obj.get_distribution_of_location_types(**kwargs).mean()
    df = loc_series.to_frame('values')
    df.sort_index(inplace=True)
    colors = [locationTypeColors[loc] for loc in df.index.values]

    if kind == 'bar':
        df['values'].plot(kind='bar', color=colors, ax=ax)
        ax.set_title('Distribution of generated location types')
        ax.set_xlabel('Location type')
        ax.set_ylabel('# generated of this type')
    elif kind == 'pie':
        pass  # todo
    if save_fig:
        plt.savefig('output/plots/location_distribution.png', bbox_inches='tight')
    return ax, df


def plot_locations_and_schedules(modeled_pop_world_obj,
                                 locs_to_hide=[],  # example ['home']
                                 axes=None,
                                 save_figure=False):
    """
    plots two pie plots for location and schedule types
    :params: locs_to_hide list of location types, # example ['home']  axes=None,
                                 save_figure=False
    """
    location_distribution_df = modeled_pop_world_obj.get_distribution_of_location_types()
    location_distribution_df.drop(columns=locs_to_hide, inplace=True)
    location_distribution_df_m = location_distribution_df.mean()
    if not axes:
        fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    colors = [locationTypeColors[x]
              for x in location_distribution_df_m.index.values]
    locs_to_show = ['home', 'school', 'public', 'hospital', 'work', 'morgue']
    location_distribution_df_m.plot(kind='pie', radius=1, colors=colors, ax=axes[0],
                                    wedgeprops=dict(width=0.7, edgecolor='w'),)
    # explode=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],)
    # schedule types

    schedules = [p.type for p in modeled_pop_world_obj.people]
    schedule_types = modeled_pop_world_obj.schedule_types
    values = [len([x for x in schedules if x == st]) /
              len(schedules) for st in schedule_types]
    colors = [scheduleTypeColors[x]
              for x in schedule_types]
    axes[1].pie(values, labels=schedule_types, radius=1, colors=colors,
                wedgeprops=dict(width=0.7, edgecolor='w'), explode=[0., 0.0, 0.0, 0.0, 0.0, 0.0], )
    if save_figure:
        plt.savefig('output/plots/location_schedules_pie.png', bbox_inches='tight')


def plot_initial_distribution_of_ages_and_infected(modeled_pop_world_obj, age_groups_step=10, save_figure=False):
    age_groups_status_distribution = modeled_pop_world_obj.get_distribution_of_ages_and_infected(
        age_groups_step)
    width_of_bars = 0.50
    fig, ax = plt.subplots()
    fig_width_factor = 1/(age_groups_step/10)
    fig.set_figwidth(12*fig_width_factor)
    fig.set_figheight(7)
    tot_ppl = modeled_pop_world_obj.number_of_people
    age_groups = [str(age_group) for age_group in age_groups_status_distribution.index]
    per_of_inf = (age_groups_status_distribution['I'] / tot_ppl) * 100
    per_of_sus = (age_groups_status_distribution['S'] / tot_ppl) * 100
    ax.bar(age_groups, per_of_inf, width_of_bars,
           label=statusLabels['I'], color=statusAndFlagsColors['I'])
    ax.bar(age_groups, per_of_sus, width_of_bars, bottom=per_of_inf,
           label=statusLabels['S'], color=statusAndFlagsColors['S'])
    ax.set_title('Distribution of infected among age groups ({} people in total)'.format(tot_ppl))
    ax.set_ylabel('% of population')
    ax.set_xlabel('Age groups')
    # ax.legend()
    plt.tight_layout()

    if save_figure:
        fig.savefig('output/plots/initial_distribution_of_ages_and_infected.png')
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
        plt.savefig('output/plots/status_plot.png')


def plot_age_groups_status_timecourse(simulation_object, age_groups_step=10, save_figure=False):
    trajectories_df = simulation_object.get_distribution_of_statuses_per_age(
        age_groups_step=age_groups_step)
    nr_of_figure_rows = int(round(age_groups_step / 2, 0) + (age_groups_step % 2))
    fig, axes = plt.subplots(nr_of_figure_rows, 2, figsize=(9, 3*nr_of_figure_rows))
    all_axes = axes.flatten()
    for i, age_group_category in enumerate(trajectories_df.index.get_level_values(0).categories):
        age_group_df = trajectories_df.loc[age_group_category]
        ax = all_axes[i]
        statuses = age_group_df.columns
        for status in statuses:
            ax.plot(age_group_df.index.get_level_values('time'),
                    age_group_df[status], label=statusLabels[status],
                    color=statusAndFlagsColors[status])
            ax.set_title(age_group_category)
            ax.set_xlabel('Time [hours]')
            ax.set_ylabel('# People')
            # ax.legend()
    plt.tight_layout()
    plt.show()
    if save_figure:
        plt.savefig('output/plots/age_groups_status_plot.png')


def plot_strains_timecourse(simulation_object, type='cumulative'):
    strain_sums = simulation_object.get_strain_sums_over_time(type=type)
    count = 0
    for strain in strain_sums.columns:
        plt.plot(strain_sums.index, strain_sums[strain],
                 label=str(strain), color=mainModelCmap(count))
        count += 1
    plt.title('Cumulative strain-abundance trajectories')
    plt.xlabel('Time [hours]')
    plt.ylabel('# People')
    plt.legend()
    plt.show()


def plot_flags_timecourse(simulation_object, specific_flags=None, save_figure=False):
    """
    plots the time course for the selected flags
    :param specific_flags: list. given flags to be included in the plot
    :param save_figure: bool. Flag for saving the figure as an image
    """
    flag_sums = simulation_object.get_flag_sums_over_time(specific_flags=specific_flags)
    for flag in flag_sums.columns:
        plt.plot(flag_sums.index, flag_sums[flag], linestyle='--' if 'Was' in flag else '-',
                 label=str(flag), color=statusAndFlagsColors[flag])
    plt.title('flag trajectories')
    plt.xlabel('Time [hours]')
    plt.ylabel('# People')
    plt.xlabel('Time [hours]')
    plt.legend()
    plt.show()
    if save_figure:
        plt.savefig('output/plots/flags_plot.png')


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
        plt.savefig('output/plots/loc_types_occupancy_plot.png')


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
        try:
            ax = axes[col, row]
        except IndexError:
            ax = axes[k]
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
        plt.savefig('output/plots/loc_types_occupancy_plot.png')


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
            plt.savefig('output/plots/loc_t_'+str(time)+'.png')


def plot_distributions_of_durations(simulation_object, save_figure=False, log=False):
    """
    plots the distributions of the total duration of the infection,
    the time from infection to hospitalization,
    the times from hospitalization to death or recovery
    and the time from hospitalisation to ICU.
    :param save_figure:  Bool. Flag for saving the figure as an image
    """
    simulation_object.get_durations().hist(color=defaultCmap(1))
    plt.tight_layout()
    plt.show()
    if save_figure:
        plt.savefig('output/plots/duration_distributions.png')


def plot_interaction_patterns(simulation_object, lowest_timestep, highest_timestep, timesteps_per_aggregate, age_groups, save_figure):
    Interaction_Patterns = simulation_object.get_age_group_specific_interaction_patterns(
        lowest_timestep=lowest_timestep, highest_timestep=highest_timestep, timesteps_per_aggregate=timesteps_per_aggregate, age_groups=age_groups)

    max_tot = Interaction_Patterns.max().max()
    min_tot = Interaction_Patterns.min().min()
    y_tick_positions = np.arange(0.5, len(Interaction_Patterns.index), 1)[::2]
    x_tick_positions = np.arange(0.5, len(Interaction_Patterns.index), 1)[::2]
    x_tick_labels = [int(i) for i in Interaction_Patterns.columns][::2]
    y_tick_labels = [int(i) for i in Interaction_Patterns.index][::2]

    plt.figure(figsize=(6/1.25, 5/1.25))
    heatmap = plt.pcolor(Interaction_Patterns, cmap='Blues', vmin=min_tot, vmax=max_tot)
    plt.yticks(y_tick_positions, y_tick_labels)
    plt.xticks(x_tick_positions, x_tick_labels)
    plt.colorbar(heatmap)
    plt.title('Interactions per age-group')
    plt.xlabel('Interaction subject (age-groups)')
    plt.ylabel('Interaction object (age-groups)')
    plt.show()
    if save_figure:
        plt.savefig('output/plots/age_group_dependent_interaction_patterns.png')


def plot_infection_patterns(simulation_object, lowest_timestep, highest_timestep, timesteps_per_aggregate, age_groups, save_figure):
    Interaction_Patterns = simulation_object.get_age_group_specific_infection_patterns(
        lowest_timestep=lowest_timestep, highest_timestep=highest_timestep, timesteps_per_aggregate=timesteps_per_aggregate, age_groups=age_groups)
    max_tot = Interaction_Patterns.max().max()
    min_tot = Interaction_Patterns.min().min()
    y_tick_positions = np.arange(0.5, len(Interaction_Patterns.index), 1)[::2]
    x_tick_positions = np.arange(0.5, len(Interaction_Patterns.index), 1)[::2]
    x_tick_labels = [int(i) for i in Interaction_Patterns.columns][::2]
    y_tick_labels = [int(i) for i in Interaction_Patterns.index][::2]

    plt.figure(figsize=(6/1.25, 5/1.25))
    heatmap = plt.pcolor(Interaction_Patterns, cmap='Reds', vmin=min_tot, vmax=max_tot)
    plt.yticks(y_tick_positions, y_tick_labels)
    plt.xticks(x_tick_positions, x_tick_labels)
    plt.colorbar(heatmap)
    plt.title('Infections per age-group')
    plt.xlabel('Infection donor (age-groups)')
    plt.ylabel('Infection acceptor (age-groups)')
    plt.show()
    if save_figure:
        plt.savefig('output/plots/age_group_dependent_infection_patterns.png')


def plot_interaction_timecourse(simulation_object, save_figure=False, log=False, diagnosed_contact=False):
    """
    plot the interaction timecourse for all agents and the interaction of all agents which will be diagnosed at some point
    """

    fig, ax = plt.subplots()
    simulation_object.get_interaction_timecourse(
        diagnosed_contact=diagnosed_contact).plot(ax=ax, logy=log)
    # simulation_object.get_interaction_timecourse(diagnosed_contact=True).plot(ax=ax, logy=log)
    ax.legend(['safe contact', 'possible infectious event', 'infection event',
               'safe contact_d', 'possible infectious event_d', 'infection event_d'], loc=(1.1, 0))
    ax.set_title('Interaction Timcourse'), ax.set_ylabel('counts'), ax.set_xlabel('time, h')
    if save_figure:
        plt.savefig('output/plots/interaction_timecourse.png')


def plot_r_eff_trajectory(simulation_object,
                          sliding_window_size=None,
                          sliding_step_size=1,
                          plot_std=True,
                          save_fig=False):
    """
    plot effictive R-value for given window size from simulation object
    """
    assert sliding_window_size is not None, "the desired sliding window size has to be specified under from_sim_obj_sliding_window_size"
    tc_df = simulation_object.get_r_eff_trajectory(
        sliding_window_size, sliding_step_size=1)

    ylabels = ['r_eff']
    different_windows = False

    cmap = cm.get_cmap("Set2")
    plt.figure(figsize=(10, 10))

    if not different_windows:
        plt.plot(tc_df['time'], tc_df['r_eff'],
                 label='r_eff', color=cmap(0), linewidth=3)
        if plot_std:
            std = tc_df['stds_r_eff']
            plt.fill_between(
                tc_df['time'], tc_df['r_eff']-std, tc_df['r_eff']+std, color=cmap(0), alpha=0.2)
        plt.xlabel("Time [h]")
        plt.ylabel("Effective reproduction number $R_\mathrm{{eff}}$")
        plt.legend(ylabels, loc='best', frameon=False, title='Sliding window size = {} day(s), step size = {} h'.format(
            str(round(float(sliding_window_size) / 24, 1)), str(sliding_step_size)))
    else:
        plt.plot(tc_df['time'], tc_df['r_eff'],
                 label='r_eff', color=cmap(0), linewidth=3)
        if plot_std:
            std = tc_df['stds_r_eff']
            plt.fill_between(
                tc_df['time'], tc_df['r_eff']-std, tc_df['r_eff']+std, color=cmap(0), alpha=0.2)
        plt.xlabel("Time [h]")
        plt.ylabel("Effective reproduction number $R_\mathrm{{eff}}$")
        plt.legend(ylabels, loc='best', frameon=False,
                   title='Based on varying window sizes and steps (WSIZE[h],WSTEP[h])')

    plt.axhline(y=1., color='gray', linestyle='--')

    plt.show()

    if save_fig:
        timestr = '_' + time.strftime("%d-%m-%Y_%H-%M-%S")
        plt.savefig('output/plots/r_eff_timecourse'+timestr+'.png', dpi=200)


def plot_ratio_change(df, cmap_='Set1',
                      ax=None,
                      label_offset=0.09,
                      title='Title',
                      save_figure=True,
                      output_folder='output/plots/',
                      y_axis=True,
                      ):
    """
    plot the change between two input Dataframes as bar plot without grid
    :return: axes of plot
    """
    # if df.index.values[0] in scheduleTypeColors:
    #    colors = [scheduleTypeColors[x] for x in df.index.values]
    # elif df.index.values[0] in locationTypeColors:
    #    colors = [locationTypeColors[x] for x in df.index.values]
    # else:
    cmap = plt.get_cmap(cmap_)
    colors = cmap(np.arange(0, 2))
    if not ax:
        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
    # plot
    df['values'].plot(kind='bar', color=df['positive'].map(
        {True: colors[0], False: colors[1]}), ax=ax)
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='x', direction='out', pad=100, labelrotation=90)
    if not y_axis:
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
    ax.set_ylim(df['values'].min() * 1.4-0.1, df['values'].max() * 1.5+0.1)
    ax.xaxis.set_ticks_position('none')
    ax.set_title(title, pad=30)

    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate('{:.0%}'.format(p.get_height()),
                        (p.get_x(), p.get_height() * 1.02 + label_offset))
        else:
            ax.annotate('{:.0%}'.format(p.get_height()),
                        (p.get_x(), p.get_height() * 1.02 - label_offset*2))

    if save_figure:
        plt.savefig(output_folder + title + '.png', bbox_inches='tight')
    return ax
