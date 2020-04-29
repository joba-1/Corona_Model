from virusPropagationModel import *
import glob
import os
from multiprocessing import Pool
import argparse
import sys



def ini_and_save_world(i):
    world = ModeledPopulatedWorld(1000,10, world_from_file=True,
            geofile_name='datafiles/Buildings_Gangelt_MA_3.csv',
                                     agent_agent_infection=True,
                             automatic_initial_infections=False)#, input_schedules='schedules_v1')
    world.save('worlds/Gangelt_MA_1_'+str(i), date_suffix=False, folder='/home/basar/corona_simulations/saved_objects/worlds')
    print('worlds/Gangelt_MA_1_'+str(i)+' created')
    #return('worlds/Gangelt_MA_1_'+str(i))

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-f", "--folder", type=str, help="save folder")
    options = parser.parse_args(args)
    return options    


if __name__ == '__main__':

    options=getOptions()

    if options.folder:
        output_folder = options.folder
    else:
        output_folder = '/home/basar/corona_simulations/saved_objects/worlds'   

    try:
        os.mkdir(output_folder)
    except:
        pass    

    
    with Pool(2) as pool:
        pool.map(ini_and_save_world,[i for i in range(10)])