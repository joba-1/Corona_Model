from virusPropagationModel import *
import glob
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import sys
import matplotlib.cm as cm
from multiprocessing import Pool
import timeit
import numpy as np

#colors = vpm_plt.statusAndFlagsColors

#def getOptions(args=sys.argv[1:]):
#    parser = argparse.ArgumentParser(description="Parses command.")
#    parser.add_argument("-f", "--folder", type=int, help="Choose your location (1) Heinsberg (2) Gerangel")
#    parser.add_argument("-ma", "--min_area", type=int, help="default 3  (*1e-8) to reduce locations")
    #parser.add_argument("-n", "--number", type=int, help="A number.")
    #parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode.")
#    options = parser.parse_args(args)
#    return options
folder = '~/../basar/corona_simulations'

cmap = cm.get_cmap('Set1')
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

file_list = os.listdir('saved_objects/simulations')
sim_files = ['simulations/'+x for x in file_list if x.endswith('pkl')]#and x.startswith('sim')]
#scenario = 'reopen_schools_100'
scenario = 'different_worlds'
output_folder = 'outputs/'+scenario+'/'



def get_df_list(filename):
    #sim = load_simulation_object('scenario_output/'+filename)
    sim = load_simulation_object(filename)
    print(filename)
    return {'stat_trajectories': sim.get_status_trajectories(),
                              'durations': sim.get_durations(),
            'flag_trajectories': sim.get_flag_sums_over_time(),
            'infections_per_location_type':sim.get_infections_per_location_type()}

#sim_files =['sim0_simulationObj.pkl',
#            'sim1_simulationObj.pkl',
#            'sim2_simulationObj.pkl',
#            'sim3_simulationObj.pkl',
#            'sim4_simulationObj.pkl',
#            'sim5_simulationObj.pkl',
#            'sim6_simulationObj.pkl',
#            'sim7_simulationObj.pkl',
#            'sim8_simulationObj.pkl',
#            'sim9_simulationObj.pkl']


def plot_and_save_statii(status_trajectories_list,
                         statii=['I','S','R','D'],
                              filename='scenario',
                                 save_as_csv=True,
                                  save_plots=True):
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
            df.mean(axis=1).plot(c=statusAndFlagsColors[stat],ax=ax)

        except:
            print(stat+'  is not in list')

    ax.set_title(filename); ax.set_ylabel('counts'); ax.set_xlabel('time, h'); ax.set_ylim(0,1500)        
     
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
                                              save_plot=True):
    """
    Generates from a list of durations from different simulations one plot
    and different csv files.
    For each status a plot is created that shows all trajectories and the mean.
    """                                               
    st_l = simulation_trajectory_list   
    n= len(dur_list)
    fig, axes = plt.subplots(int(n/2),2,figsize=(8,16))

    for k,dur in enumerate(dur_list):
        row = k%2
        col = int(k/2)
        ax= axes[col][row]
        print(dur)
        data = [np.histogram(st_l[i][dur].values, bins=10, range=(0,600))[0] for i in range(len(st_l))]
        bins = np.histogram(st_l[0][dur].values, bins=10, range=(0,600))[1] 
        bins1 = [x for x in bins[1:]]
        df_d_small = pd.DataFrame(columns=bins1, data=data)
        ax.set_title(dur)
        df_d_small.boxplot(ax=ax)
        ax.set_xticklabels(ax.get_xticklabels(),rotation=30)

        if save_as_csv:
                df_d_small.to_csv(output_folder+filename+'_'+dur+'.csv')

    if save_plot:
        plt.savefig(output_folder+'plots/'+filename+'_'+dur+'.png') 
    plt.close()


def plot_flags(flags_l, cummulative=False,
                      filename='scenario',
                      save_as_csv=True,
                      save_plot=True):
    
    fig, ax = plt.subplots(1,1,figsize=(8,8))
    if cummulative:
        flags = ['WasHospitalized', 'WasDiagnosed', 'WasICUed',  'WasInfected']
    else:
        flags = ['Hospitalized', 'ICUed','IsInfected', 'Diagnosed']
        
    for i,flag in enumerate(flags):

        try:
            df = pd.concat([flags_l[i][flag] for i in range(len(flags_l))], axis=1)#, join='outer', join_axes=None, ignore_index=False,
                      #keys=None, levels=None, names=None, verify_integrity=False,
                      #copy=True)
            df.columns = [flag+str(i) for i in range(len(flags_l))]
            
            if save_as_csv:
                df.to_csv(output_folder+filename+'_'+flag+'.csv')
            #df.reset_index().drop('time')

            #df_sims.mean(axis=1)
            for col in df.columns:
                ax.plot(df.index,df[col],color=statusAndFlagsColors[flag],alpha=0.2,)
            #df.plot(c=cmap(i),alpha=0.2, legend=False, ax=ax)
            df.mean(axis=1).plot(ax=ax,c=statusAndFlagsColors[flag], label=flag)
            ax.set_title(filename); ax.set_ylabel('counts'), ax.set_xlabel('time, h')
        except:
            print(flag+'  is not in list')
                        
    legend = plt.legend()        
        
    if save_plot:
        plt.savefig(output_folder+'plots/'+filename+'_flags.png') 

def plot_and_save_infection_per_location(infection_per_location_list,
                                                 filename='scenario',
                                                    save_as_csv=True,
                                                      save_plot=True):
    fig, ax = plt.subplots(1,1,figsize=(8,6)) 
    inf_per_loc_df = pd.DataFrame(infection_per_location_list)
    inf_per_loc_df.boxplot(ax=ax)
    plt.title('scenario')
    plt.ylabel('infections per location type/locations of type')

    if save_as_csv:
        inf_per_loc_df.to_csv(output_folder+filename+'_infections_per_location_type.csv')

    if save_plot:
        plt.savefig(output_folder+'plots/'+filename+'_infections_per_location_type.png')                   



if __name__=='__main__':

    try:
        os.mkdir(output_folder)
        os.mkdir(output_folder+'/plots')
    except:
        pass

    start = timeit.default_timer()

    with Pool(20) as pool:
        df_dict_list = pool.map(get_df_list, sim_files)


    status_trajectories_list = [df['stat_trajectories'] for df in df_dict_list]
    simulation_trajectory_list = [df['durations'] for df in df_dict_list]
    flag_trajectories_list = [df['flag_trajectories'] for df in df_dict_list]
    infections_per_location_type_list = [df['infections_per_location_type'] for df in df_dict_list]

    
    plot_and_save_statii(status_trajectories_list, filename=scenario) 
    plot_and_save_durations(simulation_trajectory_list, filename=scenario)
    plot_flags(flag_trajectories_list, cummulative=False, filename=scenario)
    plot_flags(flag_trajectories_list, cummulative=True, filename=scenario+'_cumulativ')
    plot_and_save_infection_per_location(infections_per_location_type_list,filename=scenario)   


    stop = timeit.default_timer()

