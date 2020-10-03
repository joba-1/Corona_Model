from virusPropagationModel import *
from VPM_save_and_load import *
import glob
import os
import csv 
from multiprocessing import Pool
import argparse
import sys
from functools import partial



def ini_and_save_world(i, output_folder='saved_objects/', size=1, schedule='schedules_v2', **kwargs):
    world = ModeledPopulatedWorld(1000, 10, world_from_file=True,
            geofile_name='datafiles/Buildings_Gangelt_MA_'+str(size)+'.csv',
                                     agent_agent_infection=True,
                             automatic_initial_infections=False,
                                  input_schedules=schedule)
    world.save('Gangelt_MA_'+str(size)+'_'+schedule+'_'+str(i), date_suffix=False, folder=output_folder, **kwargs)#'/home/basar/corona_simulations/saved_objects/worlds/')
    print('worlds/Gangelt_MA_'+str(size)+'_'+schedule+'_'+str(i)+' created')

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-f", "--folder", type=str, 
                        help="save folder")
    parser.add_argument("-n", "--number", type=int, 
                        help="number of worlds")
    parser.add_argument("-c", "--cores", type=int, 
                        help="number of used cores")
    parser.add_argument("-s", "--size", type=int, 
                        help="1 or 3 -> min area for buildings")
    parser.add_argument("-t", "--town", type=str,
                        help="choose town in datafiles/: default Gangelt")
    options = parser.parse_args(args)
    return options    


if __name__ == '__main__':

    options = getOptions()
    options_dict = {}

    if options.folder:
        output_folder = options.folder
    else:
        output_folder = '/home/basar/corona_simulations_save/saved_objects/worlds/V2_RPM2_Gangelt/'
    options_dict['output_folder'] = output_folder
    try:
        os.mkdir(output_folder)
    except:
        pass    

    if options.cores:
        cores = options.cores
    else:
        cores = 50
    options_dict['cores'] = cores
    
    if options.number:
        number = options.number
    else:
        number = 100
    options_dict['number'] = number
    
    if options.size:
        size = options.size
    else:
        size = 1
    options_dict['size'] = size


    schedule = 'schedules_v2'    

    mapfunc = partial(ini_and_save_world, output_folder=output_folder, size=size, schedule=schedule)
    with Pool(cores) as pool:
        pool.map(mapfunc, [i for i in range(number)])

    with open(output_folder + 'gen_world_parameters.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for key in options_dict:
                writer.writerow([key, options_dict[key]])
