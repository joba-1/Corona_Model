import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os 
from functools import partial
from virusPropagationModel import *
import VPM_plotting as vpm_plot

confi_z_dict = {99: 2.576,
                98: 2.326,
                95: 1.96,
                90: 1.645, }

def plot_stat_para(ax, folder_scenario, server_data_folder, statii=['S', 'I', 'R', 'D'], log=False):
    for stat in statii:
        try:
            df_stat = pd.read_csv(server_data_folder + folder_scenario +
                             '/'+folder_scenario+'_'+stat+'.csv')
        except:
            try:
                df_stat = pd.read_csv(server_data_folder + folder_scenario +
                                 '/IAR_1_0_99_'+folder_scenario[:-10]+'_'+stat+'.csv')
            except:
                print("can't read ", server_data_folder + folder_scenario +
                      '/'+folder_scenario+'_'+stat+'.csv')
        df_stat.drop('time', axis=1, inplace=True)
        if not stat.startswith('c'):    
            df_stat.plot(legend=False, alpha=0.1,
                         c=vpm_plot.statusAndFlagsColors[stat], ax=ax)
        else:
            df_stat.plot(legend=False, alpha=0.1,
                         c=vpm_plot.statusAndFlagsColors[stat[10:]], ax=ax)
    ax.set_ylabel('People')
    ax.set_xlabel('Time [hours]')
    if log:
        ax.set_yscale('log')


def plot_stat_para_mean_error(ax, folder_scenario, server_data_folder,
                              statii=['S', 'I', 'R', 'D'],
                              error_type = 'std', 
                              ci = 95,
                              log=False):
    for stat in statii:
        try:
            df_stat = pd.read_csv(server_data_folder + folder_scenario +
                                  '/'+folder_scenario+'_'+stat+'.csv')
        except:
            try:
                df_stat = pd.read_csv(server_data_folder + folder_scenario +
                                      '/IAR_1_0_99_'+folder_scenario[:-10]+'_'+stat+'.csv')
            except:
                print("can't read ", server_data_folder + folder_scenario +
                      '/'+folder_scenario+'_'+stat+'.csv')
        df_stat.drop('time', axis=1, inplace=True)

        df_stat_m = df_stat.mean(axis=1)
        df_stat_std = df_stat.std(axis=1)
        
        if error_type == 'std':
            error = df_stat_std
        elif error_type == 'CI' :
            error = confi_z_dict[ci]*df_stat_std.values / \
                np.sqrt(len(df_stat.columns))

        ax.plot(df_stat_m,
                color=vpm_plot.statusAndFlagsColors[stat.split('_')[-1]],
                label=stat.split('_')[-1])
        ax.fill_between(df_stat_m.index, df_stat_m.values-error,
                        df_stat_m.values+error, color=vpm_plot.statusAndFlagsColors[stat.split('_')[-1]],
                        alpha=0.3)

        #if not stat.startswith('c'):
        #    df_stat.plot(legend=False, alpha=0.1,
        #                 c=vpm_plot.statusAndFlagsColors[stat], ax=ax)
        #else:
        #    df_stat.plot(legend=False, alpha=0.1,
        #                 c=vpm_plot.statusAndFlagsColors[stat[10:]], ax=ax)
    ax.set_ylabel('People')
    ax.set_xlabel('Time [hours]')
    if log:
        ax.set_yscale('log')


def get_df_total_status(files_folder, server_data_folder, status='I', digits=5, time_loc=-1):
    """:returns: DataFrame with status at each t-1 for each repetition and each parameter"""
    if status == 'I':
        stat = 'cumulativ_WasInfected'
    else:
        stat = status
    files_dict = {}
    for folder_scenario in files_folder:
        try:
            df = pd.read_csv(server_data_folder + folder_scenario +
                             '/'+folder_scenario+'_'+stat+'.csv')
        except:
            try:
                df = pd.read_csv(server_data_folder + folder_scenario +
                                 '/IAR_1_0_99_'+folder_scenario[:-10]+'_'+stat+'.csv')
            except:                     
                df = pd.read_csv(server_data_folder + folder_scenario +
                             '/'+folder_scenario[:-10]+'_'+stat+'.csv')
        df.drop('time', axis=1, inplace=True)
        param_value = float(folder_scenario.split('_')[-digits])
        files_dict[param_value] = df.iloc[time_loc].values
    return pd.DataFrame(files_dict)


def get_delta_total_infection(data_set_name, scenarios, filenames, server_data_folder, rw='0', status='I'):
    rec_folders = [x for x in filenames if scenarios[data_set_name]
                   [:25] in x and x.split('_')[-5] == rw]
    df_I_1 = get_df_total_status(
        rec_folders, server_data_folder, status=status, digits=7, time_loc=1)
    df_I_2 = get_df_total_status(
        rec_folders, server_data_folder, status=status, digits=7, time_loc=-1)
    df_delta_I = df_I_2 - df_I_1
    return df_delta_I


def plot_total_infections_scan(ax, data_set_name, filenames, server_data_folder,
                               scenarios, status='I', color='r', size=2, ylim=(-500, 11000),
                               digits=5, time_loc=-1, reduce_name_by=25):

    scan_folders = [
        x for x in filenames if scenarios[data_set_name][:-reduce_name_by] in x]

    df_reopen_all = get_df_total_status(scan_folders,
                                        server_data_folder,
                                        status=status,
                                        digits=digits,
                                        time_loc=time_loc,)
    col = list(df_reopen_all.keys())

    col.sort()
    plt.figure(figsize=(4, 4))
    sns.swarmplot(data=df_reopen_all[col], color='r', size=2, ax=ax)
    ax.set_xticklabels([float(x) if col.index(x) %
                        2 == 0 else None for x in col])
    ax.set_ylim(ylim)
    print(scan_folders[0])
    return ax


def plot_frac_of_Inf_waves_vs_recover_frac(ax, filenames, scenarios,
                                           server_data_folder, cutoff=20,
                                           legend=True, status='I'):
    df_delta_I_nw = get_delta_total_infection(
        'Herd Immunity W', scenarios, filenames, server_data_folder, rw='1', status=status)
    df_delta_I_rnd = get_delta_total_infection(
        'Herd Immunity R', scenarios, filenames, server_data_folder, rw='0', status=status)
    df_nw_I_new = df_delta_I_nw[df_delta_I_nw > cutoff]
    df_nw = df_nw_I_new.count().sort_index()
    df_rnd_I_new = df_delta_I_rnd[df_delta_I_rnd > cutoff]
    df_rnd = df_rnd_I_new.count().sort_index()

    ax.plot(df_rnd, '--d', label='random recovery', color='red')
    ax.plot(df_nw, '--d', label='network recovery', color='blue')
    if status == 'I':
        ax.set_ylabel('Fraction of emerged infection wave')
    elif status == 'D':
        ax.set_ylabel('Fraction of infection wave with deceased people')
    ax.set_xlabel('Recover Fraction')
    if  legend:
        ax.legend(markerscale=1, frameon=False)

def get_total_infections(data_set_name, scenarios, server_data_folder):
    filename = scenarios[data_set_name][:-10]+'_cumulativ_WasInfected.csv'
    df_I_tot = pd.read_csv(
        server_data_folder+scenarios[data_set_name] + '/' + filename)
    df_I_tot.drop('time', axis=1, inplace=True)
    df_I_tot.columns = [int(x[11:]) for x in list(df_I_tot.columns)]
    I_tot = df_I_tot.iloc[-1]
    return I_tot

def get_sw_dict(data_set_name, scenarios, server_data_folder, threshold=3000):
    a = get_total_infections(data_set_name, scenarios,
                             server_data_folder) > threshold
    return a.to_dict()

def get_infectivities_at_T(data_set_name, scenarios, server_data_folder, threshold=3000,):
    I_tot = get_total_infections(data_set_name, scenarios, server_data_folder)
    sw_dict = get_sw_dict(data_set_name, scenarios,
                          server_data_folder, threshold=3000)
    inf_t_df_list = []

    for inf_t in ['infectivities_2', 'infectivities_3']:
        filename = scenarios[data_set_name][:-10]+'_'+inf_t+'_.csv'
        df_infectivities_1 = pd.read_csv(
            server_data_folder+scenarios[data_set_name] + '/' + filename)
        df_infectivities_1.drop('ID', axis=1, inplace=True)
        df_inf_long = df_infectivities_1.stack().reset_index()
        df_inf_long.columns = ['h_ID', 'name', inf_t]
        df_inf_long['run'] = [int(x[13:]) for x in df_inf_long['name'].values]
        df_inf_long['sw'] = df_inf_long['run'].map(sw_dict)
        df_new = df_inf_long.groupby('run').mean()
        #plt.figure(inf_t)
        #sns.swarmplot(data=df_new, x='sw', y=inf_t)
        inf_t_df_list.append(df_inf_long)
    df_inf_all = pd.concat(inf_t_df_list)
    return(df_inf_all)

def assign_types(agent_id_type_dict, location_id_type_dict, df):
    df.sort_values(by='time', inplace=True)
    df['loc_type'] = df['infection_loc_ID'].map(location_id_type_dict)
    df['agent_type'] = df['infected_by_ID'].map(agent_id_type_dict)
    return(df)

def get_delta_ds(ds1, ds2, relative=False):
    if relative:
        return((ds1-ds2)/ds2)
    else:
        return(ds1-ds2)

def get_ID_Type_dicts(scenario, server_data_folder):
    df_ai = pd.read_csv(server_data_folder+scenario+'/' +
                        scenario[:-10]+'_agent_infos.csv')
    df_li = pd.read_csv(server_data_folder+scenario+'/' +
                        scenario[:-10]+'_location_infos.csv')
    agent_id_type_dict = dict(zip(df_ai['ID'].values, df_ai['Type'].values))
    location_id_type_dict = dict(zip(df_li['ID'].values, df_li['Type'].values))
    return(agent_id_type_dict, location_id_type_dict)


def get_df_list(scenario, server_data_folder):
    agent_id_type_dict, location_id_type_dict = get_ID_Type_dicts(
        scenario, server_data_folder)
    infect_info_filenames = os.listdir(
        server_data_folder+scenario+'/'+'infection_informations/')
    df_list = [pd.read_csv(server_data_folder+scenario+'/' +
                           'infection_informations/'+x) for x in infect_info_filenames]
    mapfunc = partial(assign_types, agent_id_type_dict, location_id_type_dict)
    return(list(map(mapfunc, df_list)))


def get_df_delta(scenario, server_data_folder, object_type, fraction_nr_type_dict,  fraction=1,):
    df_list_assigned = get_df_list(scenario, server_data_folder)
    df_ratios_list = [df_s[:int(fraction*len(df_s))].groupby(object_type).count()[
        'h_ID']/(int(fraction*len(df_s))) for df_s in df_list_assigned]
    df_ratios_all = pd.concat(df_ratios_list, axis=1)
    df_ratios_all.columns = [str(x) for x in range(100)]
    df_ratios_all.sort_index(inplace=True)

    df_is_m = df_ratios_all.mean(axis=1)
    df_is_std = df_ratios_all.std(axis=1)

    df_delta = get_delta_ds(
        df_is_m, fraction_nr_type_dict[object_type][0], relative=False)

    return(df_delta)


def plot_delta(ax, df_delta, color_dict=vpm_plot.scheduleTypeColors, width=0.8, label_offset=0.01):

    df_delta.plot(ax=ax, kind='bar', color=df_delta.index.map(
        color_dict), width=width)  # , color=df['positive'].map(

    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # {True: colors[0], False: colors[1]}), ax=ax)
    ax.spines['top'].set_visible(False)
    if not 0:
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])
    #ax.set_ylim(df['values'].min() * 1.4-0.1, df['values'].max() * 1.5+0.1)
    ax.xaxis.set_ticks_position('none')
    #ax.set_title(title, pad=30)

    for p in ax.patches:
        print(p.get_facecolor())
        if p.get_height() > 0:
            ax.annotate('{:.0%}'.format(p.get_height()),
                        (p.get_x(), p.get_height() * 1.02 + label_offset))
        else:
            ax.annotate('{:.0%}'.format(p.get_height()),
                        (p.get_x(), p.get_height() * 1.02 - label_offset*2))

    ax.tick_params(axis='x', direction='out', pad=100, labelrotation=90)

    return(ax)


def get_fractions_and_numbers_agents_locs(scenario, server_data_folder, with_mixing_loc=True):
    df_ai = pd.read_csv(server_data_folder+scenario+'/' +
                        scenario[:-10]+'_agent_infos.csv')
    df_li = pd.read_csv(server_data_folder+scenario+'/' +
                        scenario[:-10]+'_location_infos.csv')

    df_fraction_s = df_ai.groupby('Type').count()['ID']/len(df_ai)
    df_fraction_l = df_li.groupby('Type').count()['ID']/len(df_li)
    try:
        if with_mixing_loc:
            pass
        else:
            df_fraction_l.drop(['mixing_loc'], inplace=True)
        df_fraction_l.drop(['morgue'], inplace=True)
    except:
        pass

    n_people = len(df_ai)
    n_locs = len(df_li)
    fraction_nr_type_dict = {
        'agent_type': (df_fraction_s, n_people, vpm_plot.scheduleTypeColors),
        'loc_type': (df_fraction_l, n_locs, vpm_plot.locationTypeColors),
    }
    return(fraction_nr_type_dict)
