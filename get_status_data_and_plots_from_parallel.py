from virusPropagationModel import *
import glob
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import sys
import matplotlib.cm as cm 



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

file_list = os.listdir('~/../basar/corona_simulations/saved_objects/scenario_output')
sim_files = [x for x in file_list if x.endswith('pkl')]#and x.startswith('sim')]

status_trajectories_list= []

for filename in sim_files:
    sim = load_simulation_object('scenario_output/'+filename)
    status_trajectories_list.append(sim.get_status_trajectories())


for i,stat in enumerate(['I','S','R','D']):

    try:
        df = pd.concat([status_trajectories_list[i][stat].set_index('time') for i in range(len(status_trajectories_list))], axis=1)#, join='outer', join_axes=None, ignore_index=False,
                  #keys=None, levels=None, names=None, verify_integrity=False,
                  #copy=True)
        df.columns = [stat+str(i) for i in range(len(status_trajectories_list))]
        df.to_csv('outputs/'+filename[:-4]+'_'+stat+'.csv')
        #df.reset_index().drop('time')

        #df_sims.mean(axis=1)

        ax = df.plot(c=cmap(i),alpha=0.2, legend=False)
        ax.plot()
        df.mean(axis=1).plot(c='k')
        ax.set_title(stat); ax.set_ylabel('counts'), ax.set_xlabel('time, h')

        
        plt.savefig('outputs/plots/'+filename[:-4]+'_'+stat+'.png') 
        plt.close()
    except:
        print(stat+'  is not in list')