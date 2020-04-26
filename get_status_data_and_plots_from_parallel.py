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

#file_list = os.listdir('/home/basar/corona_simulations/saved_objects/scenario_output')
#sim_files = [x for x in file_list if x.endswith('pkl')]#and x.startswith('sim')]
#scenario = 'reopen_schools_100'
scenario = 'test'
status_trajectories_list= []

def get_df_list(filename):
    #sim = load_simulation_object('scenario_output/'+filename)
    sim = load_simulation_object(filename)
    print(filename)
    return {'stat_trajectories': sim.get_status_trajectories(),
            'durations': sim.get_durations()}

sim_files =['sim0_simulationObj.pkl',
            'sim1_simulationObj.pkl',
            'sim2_simulationObj.pkl',
            'sim3_simulationObj.pkl']

def plot_and_save_statii(status_trajectories_list,
                         statii=['I','S','R','D'],
                              filename='scenario',
                                 save_as_csv=True,
                                  save_plots=True):
    """
    Generates from a list of status trajectories from different simulations plots and csv files
    for each status a plot is created that shows all trajectories and the mean
    """
    for i,stat in enumerate(statii):

        try:
            df = pd.concat([status_trajectories_list[j][stat].set_index('time') for j in range(len(status_trajectories_list))], axis=1)#, join='outer', join_axes=None, ignore_index=False,
                      #keys=None, levels=None, names=None, verify_integrity=False,
                      #copy=True)
            df.columns = [stat+str(i) for i in range(len(status_trajectories_list))]
            
            if save_as_csv:
                df.to_csv('outputs/'+filename+'_'+stat+'.csv')
            #df.reset_index().drop('time')


            ax = df.plot(c=cmap(i),alpha=0.2, legend=False)
            ax.plot()
            df.mean(axis=1).plot(c='k')
            ax.set_title(stat); ax.set_ylabel('counts'), ax.set_xlabel('time, h')
            #ax.set_ylim(0,16000)
            ax.set_ylim(0,1500)

            if save_plots:
                plt.savefig('outputs/plots/'+scenario+'_'+stat+'.png') 
            plt.close()
        except:
            print(stat+'  is not in list')

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
                df_d_small.to_csv('outputs/'+filename+'_'+dur+'.csv')

    if save_plot:
        plt.savefig('outputs/plots/'+scenario+'_'+dur+'.png') 
    plt.close()

#def plot_and_save_flag_trajectories(flag_trajectories_list):
#def plot_and_save_infection_per_location(infection_per_location_list):                    



if __name__=='__main__':

    start = timeit.default_timer()

    with Pool(20) as pool:
        df_dict_list = pool.map(get_df_list, sim_files)


    status_trajectories_list = [df['stat_trajectories'] for df in df_dict_list]
    simulation_trajectory_list = [df['durations'] for df in df_dict_list]

    plot_and_save_statii(status_trajectories_list) 
    plot_and_save_durations(simulation_trajectory_list)
    #plot_and_save_flag_trajectories()
    #plot_and_save_location_occupancies()
    

    stop = timeit.default_timer()

