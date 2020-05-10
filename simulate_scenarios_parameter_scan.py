from virusPropagationModel import *
from get_status_data_and_plots_from_parallel import *
import glob
import os
from multiprocessing import Pool
import copy
import timeit
import argparse
import sys
import csv
import pickle
import numpy as np


scenarios = [{'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':[],                         'reopen_locs':[],                          'infectivity':0.5, 'name':'no_mitigation'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':[],                         'reopen_locs':[],                          'infectivity':0.5, 'name':'no_mitigation_medics_02', 'hospital_coeff': 0.02},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':[],                          'infectivity':0.5, 'name':'close_all'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['public','school','work'],  'infectivity':0.5, 'name':'close_all_reopen_all'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['work'],                    'infectivity':0.5, 'name':'close_all_reopen_work'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['school'],                  'infectivity':0.5, 'name':'close_all_reopen_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['public'],                  'infectivity':0.5, 'name':'close_all_reopen_public'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':[],                          'infectivity':0.5, 'name':'close_public_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['public','school'],         'infectivity':0.5, 'name':'close_public_school_reopen_all'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['school'],                  'infectivity':0.5, 'name':'close_public_school_reopen_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['public'],                  'infectivity':0.5, 'name':'close_public_school_reopen_public'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','work'],          'reopen_locs':[],                          'infectivity':0.5, 'name':'close_public_work'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['work','school'],          'reopen_locs':[],                          'infectivity':0.5, 'name':'close_work_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':[],                         'reopen_locs':[],                          'infectivity':0.3, 'name':'no_mitigation'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':[],                         'reopen_locs':[],                          'infectivity':0.3, 'name':'no_mitigation_medics_02', 'hospital_coeff': 0.02},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':[],                          'infectivity':0.3, 'name':'close_all'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['public','school','work'],  'infectivity':0.3, 'name':'close_all_reopen_all'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['work'],                    'infectivity':0.3, 'name':'close_all_reopen_work'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['school'],                  'infectivity':0.3, 'name':'close_all_reopen_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['public'],                  'infectivity':0.3, 'name':'close_all_reopen_public'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':[],                          'infectivity':0.3, 'name':'close_public_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['public','school'],         'infectivity':0.3, 'name':'close_public_school_reopen_all'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['school'],                  'infectivity':0.3, 'name':'close_public_school_reopen_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['public'],                  'infectivity':0.3, 'name':'close_public_school_reopen_public'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','work'],          'reopen_locs':[],                          'infectivity':0.3, 'name':'close_public_work'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['work','school'],          'reopen_locs':[],                          'infectivity':0.3, 'name':'close_work_school'}]

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
    parser.add_argument("-w", "--world", type=int, help="number of world in '/home/basar/corona_simulations/saved_objects/worlds' ")
    parser.add_argument("-f", "--folder", type=str, help="name of the folder in saved_objects/ ")
    parser.add_argument("-sc", "--scenario", type=str, help="define the simulated scenario_type else: 'default' ")
    parser.add_argument("-p", "--parameter", type=str, help="define the parameter to scan: max_time start_2 start_3 infectivity ")
    parser.add_argument("-r", "--range", nargs='+', type=float, help="define the parameter range (2 inputs): e.g. 1 2 ")
    
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

    my_dict = {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500,
               'closed_locs': ['public', 'school', 'work'], 'reopen_locs': ['public', 'school', 'work'],
               'infectivity': 0.5, 'hospital_coeff': 0.01, 'name': 'default', 'output_folder': 'scenario_output', 'world':None}

    my_dict.update(input_dict)

    max_time = my_dict['max_time']
    start_2 = my_dict['start_2']
    start_3 = my_dict['start_3']
    closed_locs = my_dict['closed_locs']
    reopen_locs = my_dict['reopen_locs']
    infectivity = my_dict['infectivity']
    hospital_coeff = my_dict['hospital_coeff']
    name = my_dict['name']+'_inf_'+str(infectivity)
    modeledWorld = my_dict['world']

    #print(type(modeledWorld))

    simulation1 = Simulation(modeledWorld, start_2, run_immediately=False)
    simulation1.change_agent_attributes(
        {'all': {'behaviour_as_infected': {'value': infectivity, 'type': 'replacement'}}})
    simulation1.change_agent_attributes(
        {'all': {'hospital_coeff': {'value': hospital_coeff, 'type': 'replacement'}}})
    simulation1.simulate()

    #simulation2 = Simulation(simulation1, start_3-start_2, run_immediately=False)
    #del simulation1
    for p in simulation1.people:
        for loc in closed_locs:
            p.stay_home_instead_of_going_to(loc)
    simulation1.time_steps = start_3-start_2
    simulation1.simulate()

    #simulation3 = Simulation(simulation2, max_time-start_3, run_immediately=False)
    #del simulation2
    for p in simulation1.people:
        p.reset_schedule()
        for loc in list(set(closed_locs)-set(reopen_locs)):
            p.stay_home_instead_of_going_to(loc)
    simulation1.time_steps = max_time-start_3
    simulation1.simulate()

    print(my_dict['name']+'_'+str(my_dict['run']))
    #simulation1.save(name+'_'+str(my_dict['run']), # stop saving
    #                 date_suffix=False, folder=my_dict['output_folder'])

    return {'stat_trajectories': simulation1.get_status_trajectories(),
                              'durations': simulation1.get_durations(),
            'flag_trajectories': simulation1.get_flag_sums_over_time(),
            'infections_per_location_type':simulation1.get_infections_per_location_type()}


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
        output_folder = '/home/basar/corona_simulations/saved_objects/scenario_output/'

    if options.parameter:  # number of simulations
        parameter = options.parameter
    else:
        parameter = None 

    if options.range:  # number of simulations
        p_range = np.linsoace(options.parameter[0],options.parameter[1],10)
    else:
        p_range = np.array([1])         

    #if options.scenario_type: # take scenario type as argument or take default
    #    scenario_type = options.scenario_type   
    #else:
    #    scenario_type = 0    

    return scenario_type, cores, number, modeledWorld, output_folder, parameter, p_range


    def generate_scenario_list(used_scenario, number):
        used_scenarios = [copy.deepcopy(used_scenario) for i in range(number)]
        for i, d in enumerate(used_scenarios):
            d['run'] = i
        return used_scenarios    



if __name__ == '__main__':

    input_folder =  '/home/basar/corona_simulations_save/saved_objects/worlds/'
    world_list = os.listdir(input_folder)
    # and x.startswith('sim')] needs to be sorted if several simualtions in folder
    world_files = [x for x in world_list if x.endswith('pkl')]
    options = getOptions(sys.argv[1:])
    scenario_type, cores, number, modeledWorld, output_folder, parameter, p_range = get_simualtion_settings(options)

    used_scenario = scenarios[scenario_type]
  
    for p in p_range:

        used_scenario[parameter] = p
        
        scenario_and_parameter = used_scenario['name'] +'_'+parameter+'_'+":.3f".format(p)
        output_folder_plots = '/home/basar/corona_simulations_save/outputs/' + scenario_and_parameter +'/'
        used_scenario['output_folder'] = output_folder + scenario_and_parameter +'/'

        try:
            os.mkdir(output_folder_plots)
            os.mkdir(output_folder_plots+'/plots')
        except:
            pass

        try:
            os.mkdir(output_folder + scenario_and_parameter +'/')
            print(output_folder + scenario_and_parameter +'/'+' created')
        except:
            pass

        used_scenarios = generate_scenario_list(used_scenario, number)

        start = timeit.default_timer()

        infect_world(modeledWorld, IDs=[i for i in range(5)])
        for sc in used_scenarios:
            sc['world'] = modeledWorld

        with Pool(cores) as pool:
            df_dict_list = pool.map(simulate_scenario, used_scenarios)

        status_trajectories_list = [df['stat_trajectories'] for df in df_dict_list]
        simulation_trajectory_list = [df['durations'] for df in df_dict_list]
        flag_trajectories_list = [df['flag_trajectories'] for df in df_dict_list]
        infections_per_location_type_list = [df['infections_per_location_type'] for df in df_dict_list]

        plot_and_save_statii(status_trajectories_list, filename=scenario_and_parameter, output_folder=output_folder_plots) 
        plot_and_save_durations(simulation_trajectory_list, filename=scenario_and_parameter, output_folder=output_folder_plots)
        plot_flags(flag_trajectories_list, cummulative=False, filename=scenario_and_parameter, output_folder=output_folder_plots)
        plot_flags(flag_trajectories_list, cummulative=True, filename=scenario_and_parameter+'_cumulativ', output_folder=output_folder_plots)
        plot_and_save_infection_per_location(infections_per_location_type_list,filename=scenario_and_parameter, output_folder=output_folder_plots)

        stop = timeit.default_timer()

        used_scenario['runs'] = len(used_scenarios)

        with open(output_folder+'/sim_parameters.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for key in used_scenario:
                writer.writerow([key, used_scenario[key]])

    print(df_dict_list)
    print('time:  ', stop-start)
