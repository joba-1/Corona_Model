from virusPropagationModel import *
import glob
import matplotlib.pyplot as plt
import pandas as pd
from argparse import ArgumentParser
import sys
import matplotlib.cm as cm
from multiprocessing import Pool
import timeit
import numpy as np
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import matplotlib.pyplot as plt
import pandas as pd
#colors = vpm_plt.statusAndFlagsColors

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

def getOptions_1(args=sys.argv[1:]):
    parser = ArgumentParser(description="Parses command.")
    parser.add_argument("-sc", "--scenario", type=str, help="define the simulated scenario_type else: 'default' ")
    parser.add_argument("-c", "--cores", type=int, help="default 50, used cpu's cores")
    #parser.add_argument("-n", "--number", type=int, help="Number of simularions default 100 ")
    #parser.add_argument("-w", "--world", help="any input means small world else the whole gangelt is used")
    parser.add_argument("-if", "--input_folder", type=str, help="name of the folder with the simulations ")
    options = parser.parse_args(args)
    return options

def get_df_list(filename):#, input_folder='saved_objects/scenario_output/'):
    """
    load simulation file with filename in saved_objects/scenario_output/
    : return : dict with data frames of 'stat_trajectories', 'durations', 'flag_trajectories',
    'infections_per_location_type'
    """
    print(filename, input_folder)
    sim = load_simulation_object(filename, folder=input_folder)
    #sim = load_simulation_object(filename)
    #print(filename)
    return {'stat_trajectories': sim.get_status_trajectories(),
            'medic_trajectories': sim.get_status_trajectories(specific_people='medical_professional'),
                              'durations': sim.get_durations(),
            'flag_trajectories': sim.get_flag_sums_over_time(),
            'infections_per_location_type':sim.get_infections_per_location_type()}

def plot_and_save_statii(status_trajectories_list,
                         statii=['I','S','R','D'],
                              filename='scenario',
                                 save_as_csv=True,
                                  save_plots=True, output_folder='outputs/'):
    """
    Generates from a list of status trajectories from different, one simulation
    plot and and different csv files.
    for each status a plot is created that shows all trajectories and the mean
    """
    fig, ax = plt.subplots(1,1, figsize=(8,8))

    for i,stat in enumerate(statii):

        try:
            df = pd.concat([status_trajectories_list[j][stat].set_index('time') for j in range(len(status_trajectories_list))], axis=1)
            df.columns = [stat+str(i) for i in range(len(status_trajectories_list))]
            
            if save_as_csv:
                df.to_csv(output_folder+filename+'_'+stat+'.csv')

            df.plot(c=statusAndFlagsColors[stat],alpha=0.2, legend=False, ax=ax)
            df.mean(axis=1).plot(c='k',ax=ax, label=stat)#statusAndFlagsColors[stat]

        except:
            print(stat+'  is not in list')

    ax.set_title(filename); ax.set_ylabel('counts'); ax.set_xlabel('time, h'); #ax.set_ylim(0,1500)        
     
    if save_plots:
        plt.savefig(output_folder+'plots/'+filename+'_statii.png') 
    plt.close()                    

def plot_and_save_durations(simulation_trajectory_list,
                            dur_list=['infection_to_recovery',
                                         'infection_to_death',
                                      'infection_to_hospital',
                                       'hospital_to_recovery',
                                          'hospital_to_death',
                                           'hospital_to_icu'],
                                          filename='scenario',
                                             save_as_csv=True,
                                              save_plot=True, output_folder='outputs/'):
    """
    Generates from a list of durations from different simulations one plot
    and different csv files.
    For each status a plot is created that shows all trajectories and the mean.
    """                                               
    st_l = simulation_trajectory_list   
    n= len(dur_list)
    fig, axes = plt.subplots(int(n/2),2,figsize=(8,16))

    for k,dur in enumerate(dur_list):

        max_v=max([d[dur].max() for d in st_l])
        
        if np.isnan(max_v):
            max_value = 600
        else:
            max_value = (int(max_v/10)+1)*10
             

        row = k%2
        col = int(k/2)
        ax= axes[col][row]
        print(dur)
        data = [np.histogram(st_l[i][dur].values, bins=10, range=(0,max_value))[0] for i in range(len(st_l))]
        bins = np.histogram(st_l[0][dur].values, bins=10, range=(0,max_value))[1] 
        bins1 = [x for x in bins[1:]]
        df_d_small = pd.DataFrame(columns=bins1, data=data)
        ax.set_title(dur)
        df_d_small.boxplot(ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(),rotation=30)
        ax.set_xlabel('time, h')
        ax.set_ylabel('counts')

        if save_as_csv:
                df_d_small.to_csv(output_folder+filename+'_'+dur+'.csv')
    plt.tight_layout()            

    if save_plot:
        plt.savefig(output_folder+'plots/'+filename+'_'+dur+'.png') 
    plt.close()

def plot_flags(flags_l, cummulative=False,
                      filename='scenario',
                      save_as_csv=True,
                      save_plot=True, output_folder='outputs/'):
    
    fig, ax = plt.subplots(1,1,figsize=(8,8))
    if cummulative:
        flags = ['WasHospitalized', 'WasDiagnosed', 'WasICUed',  'WasInfected']
    else:
        flags = ['Hospitalized', 'ICUed','IsInfected', 'Diagnosed']
        
    for flag in flags:

        try:
            df = pd.concat([flags_l[i][flag] for i in range(len(flags_l))], axis=1)#, join='outer', join_axes=None, ignore_index=False,
                      #keys=None, levels=None, names=None, verify_integrity=False,
                      #copy=True)
            df.columns = [flag+str(i) for i in range(len(flags_l))]
            
            if save_as_csv:
                df.to_csv(output_folder+filename+'_'+flag+'.csv')

            for col in df.columns:
                ax.plot(df.index,df[col], color=statusAndFlagsColors[flag], alpha=0.2)
            #df.plot(c=cmap(i),alpha=0.2, legend=False, ax=ax)
            df.mean(axis=1).plot(ax=ax, c=statusAndFlagsColors[flag], label=flag)
            ax.set_title(filename); ax.set_ylabel('counts'), ax.set_xlabel('time, h')
            ax.set_yscale('log')
        except:
            print(flag+'  is not in list')
                        
    legend = plt.legend()        
        
    if save_plot:
        plt.savefig(output_folder+'plots/'+filename+'_flags.png')
    plt.close()

def plot_and_save_infection_per_location(infection_per_location_list,
                                                 filename='scenario',
                                                    save_as_csv=True,
                                                      save_plot=True, output_folder='outputs/'):
    fig, ax = plt.subplots(1,1,figsize=(8,6)) 
    inf_per_loc_df = pd.DataFrame(infection_per_location_list)
    inf_per_loc_df.boxplot(ax=ax)
    plt.title('scenario')
    plt.ylabel('infections per location type/locations of type')

    if save_as_csv:
        inf_per_loc_df.to_csv(output_folder+filename+'_infections_per_location_type.csv')

    if save_plot:
        plt.savefig(output_folder+'plots/'+filename+'_infections_per_location_type.png')    
    plt.close()    

def plot_and_save_patterns(df_list, save_figure=True,
                           pattern='interactions',
                           output_folder='output_folder/',
                           filename='scenario',
                           ):

    if pattern =='interactions':
        c = 'Blues'
    elif pattern == 'infections':
        c = 'Reds'    
    else:
        raise ValueError
    
    Interaction_Patterns = sum(df_list)/len(df_list) # mean over all dfs
    max_tot = Interaction_Patterns.max().max()
    min_tot = Interaction_Patterns.min().min()
    y_tick_positions = np.arange(0.5, len(Interaction_Patterns.index), 1)[::2]
    x_tick_positions = np.arange(0.5, len(Interaction_Patterns.index), 1)[::2]
    x_tick_labels = [int(i) for i in Interaction_Patterns.columns][::2]
    y_tick_labels = [int(i) for i in Interaction_Patterns.index][::2]

    plt.figure(figsize=(6/1.25, 5/1.25))
    heatmap = plt.pcolor(Interaction_Patterns, cmap=c,
                         vmin=min_tot, vmax=max_tot)
    plt.yticks(y_tick_positions, y_tick_labels)
    plt.xticks(x_tick_positions, x_tick_labels)
    plt.colorbar(heatmap)
    plt.title(pattern+' per age-group')
    plt.xlabel(pattern+' subject (age-groups)')
    plt.ylabel(pattern+' object (age-groups)')
    #plt.show()
    if save_figure:
        plt.savefig(output_folder+'plots/' + filename +
                    'age_group_dependent_'+pattern+'_patterns.svg', bbox_inches='tight')
        plt.savefig(output_folder+'plots/' + filename +
                    'age_group_dependent_'+pattern+'_patterns.png', bbox_inches='tight')
    plt.close()                
    Interaction_Patterns.to_csv(
        output_folder+filename + '_' + 'age_group_dependent' + '_' + pattern+'_patterns.csv')

def plot_and_save_contact_tracing(df_list, filename='scenario', output_folder='outputs/'):
    '''only save no plotting yet'''
    df = pd.concat(df_list, axis=0)
    df.reset_index(inplace=True)
    df_mean = df.groupby('aggregated_time').mean()
    df.to_csv(output_folder+filename + '_' + 'contact_tracing.csv')
    
def save_number_of_infected_households(number_of_infected_households_list, filename='scenario', output_folder='outputs/'):
    df = pd.concat([number_of_infected_households_list[j].set_index('time') for j in range(len(number_of_infected_households_list))], axis=1)
    df.columns = ['households'+str(i) for i in range(len(number_of_infected_households_list))]         
    df.to_csv(output_folder+filename+'_'+'households'+'.csv')

def plot_infection_per_schedule_type(df_I_list, world,
                                     cutoff_time=100, nr_most_inf_p=800,
                                     save_figure=True,filename='scenario',
                                     output_folder='outputs/',
                                     relative=True,):

    ####data
    #world
    id_Type_dict = {p.ID: p.type for p in world.people}  # faster
    schedule_types = set(id_Type_dict.values())
    n_people = len(id_Type_dict)
    type_ratio_dict = {t: sum([1 for x in id_Type_dict if id_Type_dict[x] == t])/n_people for t in schedule_types}
    df_world = pd.DataFrame([type_ratio_dict])
    df_world_m = df_world.mean()
    
    #infections
    group_list = [df[df.index > cutoff_time].groupby(
            'infected_by_ID').count().sort_values('h_ID') for df in df_I_list]
    type_ratio_inf_list = []
    for df in group_list:
        type_list_inf = [id_Type_dict[x] for x in df[-nr_most_inf_p:].index]
        type_ratio_inf_list.append(
            {t: len([1 for x in type_list_inf if x == t])/len(type_list_inf) for t in schedule_types})
    df_inf_ratios = pd.DataFrame(type_ratio_inf_list)
    
    #combine world and infection
    if relative:
        df_series = (df_inf_ratios.mean()-df_world_m)/df_world_m
    else: 
        df_series = (df_inf_ratios.mean()-df_world_m)
    df = df_series.to_frame('values')
    df['positive'] = df > 0
    df.sort_index(inplace=True)

    ###figure
    cmap = plt.get_cmap("Set1")
    colors = cmap(np.arange(0, 3))
    label_offset = 0.1
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))

    #df_test[df_test>0].plot(kind='bar', ax=ax, colormap='Set1')
    df['values'].plot(kind='bar', color=df['positive'].map(
        {True: colors[0], False: colors[1]}), ax=ax, )
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='x', direction='out', pad=150, labelrotation=90)
    ax.set_yticks([])
    ax.set_ylim(min(df_series)*1.4, max(df_series)*1.4)
    ax.xaxis.set_ticks_position('none')
    ax.set_title(filename, pad=30)

    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate('{:.2%}'.format(p.get_height()),
                        (p.get_x() * 1.005, p.get_height() + label_offset))
        else:
            ax.annotate('{:.2%}'.format(p.get_height()),
                        (p.get_x() * 1.005, p.get_height() - label_offset))

    #save plots and data
    if save_figure:
        plt.savefig(output_folder + 'plots/' + filename
                    + 'contributions_per_schedule.png', bbox_inches='tight')
        plt.savefig(output_folder + 'plots/' + filename
                    + 'contributions_per_schedule.svg', bbox_inches='tight')
    df.to_csv(output_folder+filename + '_' + 'df_schedules_inf_ratios.csv')

def save_infection_timecourse(df_I_list, filename='scenario', output_folder='outputs/'):
    try:
        os.mkdir(output_folder+'infection_informations/')
    except:
        pass

    for i, df_I in enumerate(df_I_list):
        df_I.to_csv(output_folder + 'infection_informations/' + filename +
                    '_' + 'infection_information' + '_' + str(i) + '.csv')

def plot_and_save_r_eff(df_list, save_figure=True,
                        output_folder='output_folder/',
                        filename='scenario',
                        ):
    """just save the mean df for R_eff"""
    df_r_eff_mean = sum(df_list)/len(df_list)
    df_r_eff_mean.to_csv(output_folder+filename+'_r_eff.csv')



if __name__=='__main__':

    options = getOptions_1(sys.argv[1:])

    if options.scenario: # take scenario type as argument or take default
        scenario = options.scenario   
    else:
        scenario = 'default' #no_mitigation'

    if options.input_folder: # take scenario type as argument or take default
        input_folder = options.input_folder   
    else:
        input_folder = 'saved_objects/scenario_output/'

    if options.cores: # used cores
        cores = options.cores   
    else:
        cores = 50     
        
    #if options.scenario_type: # take scenario type as argument or take default
    #    scenario_type = options.scenario_type   
    #else:
    #    scenario_type = 0    


    output_folder = '/home/basar/corona_simulations_save/outputs/'+scenario+'/'

    try:
        os.mkdir(output_folder)
        os.mkdir(output_folder+'/plots')
    except:
        pass

    file_list = os.listdir(input_folder)
    sim_files = [x for x in file_list if x.endswith('pkl')] #and x.startswith('sim')] needs to be sorted if several simualtions in folder

    print(sim_files)
    start = timeit.default_timer()

    with Pool(cores) as pool:
        df_dict_list = pool.map(get_df_list, sim_files)


    status_trajectories_list = [df['stat_trajectories'] for df in df_dict_list]
    medic_trajectories_list = [df['medic_trajectories'] for df in df_dict_list]
    simulation_trajectory_list = [df['durations'] for df in df_dict_list]
    flag_trajectories_list = [df['flag_trajectories'] for df in df_dict_list]
    infections_per_location_type_list = [df['infections_per_location_type'] for df in df_dict_list]

    
    plot_and_save_statii(status_trajectories_list, filename=scenario, output_folder=output_folder)
    plot_and_save_statii(medic_trajectories_list, filename=scenario+'_medical_professionals', output_folder=output_folder) 
    plot_and_save_durations(simulation_trajectory_list, filename=scenario, output_folder=output_folder)
    plot_flags(flag_trajectories_list, cummulative=False, filename=scenario, output_folder=output_folder)
    plot_flags(flag_trajectories_list, cummulative=True, filename=scenario+'_cumulativ', output_folder=output_folder)
    plot_and_save_infection_per_location(infections_per_location_type_list,filename=scenario, output_folder=output_folder)   


    stop = timeit.default_timer()

