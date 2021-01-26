#!/usr/bin/env python3

import sys
import argparse
import csv
import os
import glob
from multiprocessing import Pool
from functools import partial
from gerda.core.virusPropagationModel import *


def ini_and_save_world(i, output_folder='models/worlds/', size='1', schedule='schedules_v2', town='Gangelt', **kwargs):
    world = ModeledPopulatedWorld(1000, 10, world_from_file=True,
                                  geofile_name='input_data/geo/Buildings_'+town+'_MA_'+size+'.csv',
                                  agent_agent_infection=True,
                                  automatic_initial_infections=False,
                                  input_schedules=schedule)
    # '/home/basar/corona_simulations/saved_objects/worlds/')
    world.save(town+'_MA_'+size+'_'+schedule+'_'+str(i),
               date_suffix=False, folder=output_folder)
    print('worlds/'+town+'_MA_'+size+'_'+schedule+'_'+str(i)+' created')


def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-f", "--folder", type=str,
                        help="save folder")
    parser.add_argument("-n", "--number", type=int,
                        help="number of worlds")
    parser.add_argument("-c", "--cores", type=int,
                        help="number of used cores")
    parser.add_argument("-s", "--size", type=str,
                        help="1 or 3 -> min area for buildings")
    parser.add_argument("-t", "--town", type=str,
                        help="choose town in datafiles/: default Gangelt")
    parser.add_argument("-sc", "--schedule", type=str,
                        help="choose schedule in inputs/: default schedules_v2")
    options = parser.parse_args(args)
    return options


if __name__ == '__main__':

    options = getOptions()
    options_dict = {}

    if options.folder:
        output_folder = options.folder
    else:
        output_folder = 'models/worlds/'
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
        size = '1'
    options_dict['size'] = size

    if options.town:
        assert options.town in ['Gangelt', 'Heinsberg', 'Simbach_a.Inn', 'Oranienbaum-Wörlitz', 'Linsengericht', 'Hessisch_Lichtenau', 'Grünheide', 'Bockhorn', 'Gangelt_plus_10_work_locations',
                                'Gangelt_plus_10_public_locations'], "town must be in ['Gangelt','Heinsberg','Simbach_a.Inn','Oranienbaum-Wörlitz','Linsengericht','Hessisch_Lichtenau','Grünheide','Bockhorn','Gangelt_plus_10_work_locations','Gangelt_plus_10_public_locations']"
        town = options.town
    else:
        town = 'Gangelt'
    options_dict['town'] = town

    if options.schedule:
        assert options.schedule in [
            'schedules_v2', 'schedules_v2_different_school_times'], "schedule must be in ['schedules_v2','schedules_v2_different_school_times']"
        schedule = options.schedule
    else:
        schedule = 'schedules_v2'
    options_dict['schedule'] = schedule

    mapfunc = partial(ini_and_save_world, output_folder=output_folder,
                      size=size, schedule=schedule, town=town)
    with Pool(cores) as pool:
        pool.map(mapfunc, [i for i in range(number)])

    with open(output_folder + 'gen_world_parameters.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for key in options_dict:
            writer.writerow([key, options_dict[key]])
