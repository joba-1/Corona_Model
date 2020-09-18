from virusPropagationModel import *
from VPM_save_and_load import *
import glob
import os
from multiprocessing import Pool
import argparse
import sys
from functools import partial



def ini_and_save_world(i,size=1,**kwargs):
    world = ModeledPopulatedWorld(1000,10, world_from_file=True,
            geofile_name='datafiles/Buildings_Gangelt_MA_'+str(size)+'.csv',
                                     agent_agent_infection=True,
                             automatic_initial_infections=False,
                                  input_schedules='schedules_v2')
    world.save('Gangelt_MA_'+str(size)+'_'+str(i), date_suffix=False, folder=output_folder, **kwargs)#'/home/basar/corona_simulations/saved_objects/worlds/')
    print('worlds/Gangelt_MA_'+str(size)+'_'+str(i)+' created')

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-f", "--folder", type=str, help="save folder")
    parser.add_argument("-n", "--number", type=int, help="number of worlds")
    parser.add_argument("-c", "--cores", type=int, help="number of used cores")
    parser.add_argument("-s", "--size", type=int, help="1 or 3 -> min area for buildings")
    options = parser.parse_args(args)
    return options    


if __name__ == '__main__':

    options=getOptions()

    if options.folder:
        output_folder = options.folder
    else:
        output_folder = '/home/basar/corona_simulations_save/saved_objects/worlds/V2_RPM2_Gangelt'

    try:
        os.mkdir(output_folder)
    except:
        pass    

    if options.cores:
        cores = options.cores
    else:
        cores = 50
    
    if options.number:
        number = options.number
    else:
        number = 100
    
    if options.size:
        size = options.size
    else:
        size = 1
    
    mapfunc = partial(ini_and_save_world, size=3)
    with Pool(cores) as pool:
        pool.map(mapfunc, [i for i in range(number)])
