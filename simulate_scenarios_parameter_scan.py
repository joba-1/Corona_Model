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


scenarios = [{'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.05, 'name':'no_mitigation_if05'},
             {'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.10, 'name':'no_mitigation_if10'},
             {'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.15, 'name':'no_mitigation_if15'},
             {'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.20, 'name':'no_mitigation_if20'},
             {'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.25, 'name':'no_mitigation_if25'},
             {'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.30, 'name':'no_mitigation_if30'},
             {'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.35, 'name':'no_mitigation_if35'},
             {'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.40, 'name':'no_mitigation_if40'},
             {'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.45, 'name':'no_mitigation_if45'},
             {'run':0 ,'max_time': 2000, 'start_2':2, 'start_3':5, 'closed_locs':[],'reopen_locs':[],'infectivity':0.50, 'name':'no_mitigation_if50'}]

#world_list = os.listdir('/home/basar/corona_simulations/saved_objects/worlds')
#world_files = [input_folder+'/'+x for x in file_list if x.endswith('pkl')]


def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-st", "--scenario_type", type=int, help="Choose your scenario_type else default \n \
                        0: no_mitigation if 0.05 \n \
                        1: no_mitigation if 0.10 \n \
                        2: no_mitigation if 0.15 \n \
                        3: no_mitigation if 0.20 \n \
                        4: no_mitigation if 0.25 \n \
                        5: no_mitigation if 0.30 \n \
                        6: no_mitigation if 0.35 \n \
                        7: no_mitigation if 0.40 \n \
                        8: no_mitigation if 0.45 \n \
                        9: no_mitigation if 0.50 ")

    parser.add_argument("-c", "--cores", type=int, help="default 50, used cpu's cores")
    parser.add_argument("-n", "--number", type=int, help="Number of simularions default 100 ")
    parser.add_argument(
        "-w", "--world", type=int, help="number of world in '/home/basar/corona_simulations/saved_objects/worlds' ")
    parser.add_argument("-f", "--folder", type=str, help="name of the folder in saved_objects/ ")

    parser.add_argument("-sc", "--scenario", type=str, help="define the simulated scenario_type else: 'default' ")
    #parser.add_argument("-n", "--number", type=int, help="Number of simularions default 100 ")
    #parser.add_argument("-w", "--world", help="any input means small world else the whole gangelt is used")

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
    simulation1.save(name+'_'+str(my_dict['run']),
                     date_suffix=False, folder=my_dict['output_folder'])

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



    if options.scenario: # take scenario type as argument or take default
        scenario = options.scenario   
    else:
        scenario = 'default' #no_mitigation'
        
    #if options.scenario_type: # take scenario type as argument or take default
    #    scenario_type = options.scenario_type   
    #else:
    #    scenario_type = 0    


    output_folder_plots = '/home/basar/corona_simulations_save/outputs/'+scenario+'/'

    try:
        os.mkdir(output_folder_plots)
        os.mkdir(output_folder_plots+'/plots')
    except:
        pass

        

    return scenario_type, cores, number, modeledWorld, output_folder, output_folder_plots, scenario


if __name__ == '__main__':

    input_folder =  '/home/basar/corona_simulations_save/saved_objects/worlds/'
    #input_folder = 'saved_objects/worlds/'

    world_list = os.listdir(input_folder)
    # and x.startswith('sim')] needs to be sorted if several simualtions in folder
    world_files = [x for x in world_list if x.endswith('pkl')]
    options = getOptions(sys.argv[1:])
    scenario_type, cores, number, modeledWorld, output_folder, output_folder_plots, scenario = get_simualtion_settings(options)

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
    for sc in used_scenarios:
        sc['world'] = modeledWorld

    with Pool(cores) as pool:
        df_dict_list = pool.map(simulate_scenario, used_scenarios)

    status_trajectories_list = [df['stat_trajectories'] for df in df_dict_list]
    simulation_trajectory_list = [df['durations'] for df in df_dict_list]
    flag_trajectories_list = [df['flag_trajectories'] for df in df_dict_list]
    infections_per_location_type_list = [df['infections_per_location_type'] for df in df_dict_list]

    plot_and_save_statii(status_trajectories_list, filename=scenario, output_folder=output_folder_plots) 
    plot_and_save_durations(simulation_trajectory_list, filename=scenario, output_folder=output_folder_plots)
    plot_flags(flag_trajectories_list, cummulative=False, filename=scenario, output_folder=output_folder_plots)
    plot_flags(flag_trajectories_list, cummulative=True, filename=scenario+'_cumulativ', output_folder=output_folder_plots)
    plot_and_save_infection_per_location(infections_per_location_type_list,filename=scenario, output_folder=output_folder_plots)

    stop = timeit.default_timer()

    used_scenario['runs'] = len(used_scenarios)

    with open(output_folder+'/sim_parameters.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for key in used_scenario:
            writer.writerow([key, used_scenario[key]])

    print(df_dict_list)
    print('time:  ', stop-start)
