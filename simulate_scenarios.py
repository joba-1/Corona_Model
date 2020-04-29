from virusPropagationModel import *
import glob
import os
from multiprocessing import Pool
import copy
import timeit
import argparse
import sys
import csv
import pickle


#modeledWorld.save('OneWorld', date_suffix=False )
#modeledWorld = load_simulation_object('OneWorld')
#scenarios = [{'run':1},{'run':2}]
scenarios = [{'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [],                         'reopen_locs':[],                          'infectivity':0.5, 'name':'no_mitigation'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [],                         'reopen_locs':[
             ],                          'infectivity':0.5, 'name':'no_mitigation_medics_02', 'hospital_coeff': 0.02},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [
                 'public', 'school', 'work'], 'reopen_locs':[],                          'infectivity':0.5, 'name':'close_all'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'public', 'school', 'work'],  'infectivity':0.5, 'name':'close_all_reopen_all'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'work'],                    'infectivity':0.5, 'name':'close_all_reopen_work'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'school'],                  'infectivity':0.5, 'name':'close_all_reopen_school'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'public'],                  'infectivity':0.5, 'name':'close_all_reopen_public'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [
                 'public', 'school'],        'reopen_locs':[],                          'infectivity':0.5, 'name':'close_public_school'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
                 'public', 'school'],         'infectivity':0.5, 'name':'close_public_school_reopen_all'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
                 'school'],                  'infectivity':0.5, 'name':'close_public_school_reopen_school'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
                 'public'],                  'infectivity':0.5, 'name':'close_public_school_reopen_public'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [
                 'public', 'work'],          'reopen_locs':[],                          'infectivity':0.5, 'name':'close_public_work'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [
                 'work', 'school'],          'reopen_locs':[],                          'infectivity':0.5, 'name':'close_work_school'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [],
                 'reopen_locs':[],                          'infectivity':0.3, 'name':'no_mitigation'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [],                         'reopen_locs':[
             ],                          'infectivity':0.3, 'name':'no_mitigation_medics_02', 'hospital_coeff': 0.02},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [
                 'public', 'school', 'work'], 'reopen_locs':[],                          'infectivity':0.3, 'name':'close_all'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'public', 'school', 'work'],  'infectivity':0.3, 'name':'close_all_reopen_all'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'work'],                    'infectivity':0.3, 'name':'close_all_reopen_work'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'school'],                  'infectivity':0.3, 'name':'close_all_reopen_school'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'public'],                  'infectivity':0.3, 'name':'close_all_reopen_public'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [
                 'public', 'school'],        'reopen_locs':[],                          'infectivity':0.3, 'name':'close_public_school'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
                 'public', 'school'],         'infectivity':0.3, 'name':'close_public_school_reopen_all'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
                 'school'],                  'infectivity':0.3, 'name':'close_public_school_reopen_school'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
                 'public'],                  'infectivity':0.3, 'name':'close_public_school_reopen_public'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [
                 'public', 'work'],          'reopen_locs':[],                          'infectivity':0.3, 'name':'close_public_work'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['work', 'school'],          'reopen_locs':[],                          'infectivity':0.3, 'name':'close_work_school'}]

#world_list = os.listdir('/home/basar/corona_simulations/saved_objects/worlds')
#world_files = [input_folder+'/'+x for x in file_list if x.endswith('pkl')]


def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-st", "--scenario_type", type=int, help="Choose your scenario_type else default \n \
                        0: no_mitigation \n \
                        1: no_mitigation_medics_02 \n \
                        2: close_all\n \
                        3: close_all_reopen_all\n \
                        4: close_all_reopen_work\n \
                        5: close_all_reopen_school\n \
                        6: close_all_reopen_public\n \
                        7: close_public_school\n \
                        8: close_public_school_reopen_all\n \
                        9: close_public_school_reopen_school\n \
                        10: close_public_school_reopen_public\n \
                        11: close_public_work\n \
                        12: close_work_school \n \
                        13: no_mitigation \n \
                        14: no_mitigation_medics_02 \n \
                        15: close_all\n \
                        16: close_all_reopen_all\n \
                        17: close_all_reopen_work\n \
                        18: close_all_reopen_school\n \
                        19: close_all_reopen_public\n \
                        20: close_public_school\n \
                        21: close_public_school_reopen_all\n \
                        22: close_public_school_reopen_school\n \
                        23: close_public_school_reopen_public\n \
                        24: close_public_work\n \
                        25: close_work_school ")

    parser.add_argument("-c", "--cores", type=int, help="default 50, used cpu's cores")
    parser.add_argument("-n", "--number", type=int, help="Number of simularions default 100 ")
    parser.add_argument(
        "-w", "--world", help="number of world in '/home/basar/corona_simulations/saved_objects/worlds' ")
    parser.add_argument("-f", "--folder", type=str, help="name of the folder in saved_objects/ ")
    options = parser.parse_args(args)
    return options


def infect_world(world, IDs=[1]):
    world.initialize_infection(specific_people_ids=IDs)


# times: 3 durations for simulations; closed_locs: list of forbidden locations
def simulate_scenario(input_dict):
    '''
    input_dict = {'run':0 ,'max_time': 2000, 'start_2':400, 'start_3':700, 'closed_locs':'public', 'infectivity':0.2, 'name':'scenario_output/default'}
    required: only 'run'
    '''

    my_dict = {'run': 0, 'max_time': 1000, 'start_2': 200, 'start_3': 500,
               'closed_locs': ['public', 'school', 'work'], 'reopen_locs': ['public', 'school', 'work'],
               'infectivity': 0.5, 'hospital_coeff': 0.01, 'name': 'default', 'output_folder': 'scenario_output'}

    my_dict.update(input_dict)

    max_time = my_dict['max_time']
    start_2 = my_dict['start_2']
    start_3 = my_dict['start_3']
    closed_locs = my_dict['closed_locs']
    reopen_locs = my_dict['reopen_locs']
    infectivity = my_dict['infectivity']
    hospital_coeff = my_dict['hospital_coeff']
    name = my_dict['name']+'_inf_'+str(infectivity)

    simulation1 = Simulation(modeledWorld, start_2, run_immediately=False)
    simulation1.change_agent_attributes(
        {'all': {'behaviour_as_infected': {'value': infectivity, 'type': 'replacement'}}})
    simulation1.change_agent_attributes(
        {'all': {'hospital_coeff': {'value': hospital_coeff, 'type': 'replacement'}}})
    simulation1.simulate()

    simulation2 = Simulation(simulation1, start_3-start_2, run_immediately=False)
    #del simulation1
    for p in simulation2.people:
        for loc in closed_locs:
            p.stay_home_instead_of_going_to(loc)
    simulation2.simulate()

    simulation3 = Simulation(simulation2, max_time-start_3, run_immediately=False)
    #del simulation2
    for p in simulation3.people:
        p.reset_schedule()
        for loc in list(set(closed_locs)-set(reopen_locs)):
            p.stay_home_instead_of_going_to(loc)

    simulation3.simulate()

    print(my_dict['name']+'_'+str(my_dict['run']))
    simulation3.save(name+'_'+str(my_dict['run']),
                     date_suffix=False, folder=my_dict['output_folder'])
    return simulation3.time


def get_simualtion_settings(options):

    if options.scenario_type:  # take scenario type as argument or take default
        scenario_type = options.scenario_type
    else:
        scenario_type = 0

    if options.cores:  # used cores
        cores = options.cores
    else:
        cores = 50

    if options.number:  # number of simulations
        number = options.number
    else:
        number = 100

    if options.world:
        modeledWorld = load_simulation_object(world_files[options.world], folder=input_folder)
    else:
        # '/home/basar/corona_simulations/saved_objects/worlds')
        modeledWorld = load_simulation_object(world_files[0], folder=input_folder)

    if options.folder:  # number of simulations
        output_folder = options.folder
    else:
        output_folder = 'saved_objects/scenario_output/'

    return scenario_type, cores, number, modeledWorld, output_folder


if __name__ == '__main__':

    # '/home/basar/corona_simulations/saved_objects/worlds'
    input_folder = 'saved_objects/worlds/'

    world_list = os.listdir(input_folder)
    # and x.startswith('sim')] needs to be sorted if several simualtions in folder
    world_files = [x for x in world_list if x.endswith('pkl')]
    options = getOptions(sys.argv[1:])
    scenario_type, cores, number, modeledWorld, output_folder = get_simualtion_settings(options)

    used_scenario = scenarios[scenario_type]
    used_scenario['output_folder'] = output_folder
    used_scenarios = [copy.deepcopy(used_scenario) for i in range(number)]

    for i, d in enumerate(used_scenarios):
        d['run'] = i

    try:
        os.mkdir(output_folder)
        print(output_folder+' created')
    except:
        pass
    #    os.mkdir('saved_objects/'+output_folder+)
    #    print('saved_objects/'+output_folder+' created')

    start = timeit.default_timer()

    infect_world(modeledWorld, IDs=[i for i in range(5)])

    with Pool(cores) as pool:
        result = pool.map(simulate_scenario, used_scenarios)

    stop = timeit.default_timer()

    used_scenario['runs'] = len(used_scenarios)

    with open(output_folder+'/sim_parameters.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for key in used_scenario:
            writer.writerow([key, used_scenario[key]])

    print(result)
    print('time:  ', stop-start)
