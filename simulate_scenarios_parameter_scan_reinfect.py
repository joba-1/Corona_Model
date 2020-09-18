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
import random 

scenarios = [{'run':0 ,'max_time': 2500, 'start_2':200, 'start_3':500, 'closed_locs':[],                         'reopen_locs':[],                          'infectivity':0.6, 'name':'no_mitigation_IF06'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':[],                         'reopen_locs':[],                          'infectivity':0.5, 'name':'no_mitigation_medics_02', 'hospital_coeff': 0.02},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':1000, 'closed_locs':['public','school','work'], 'reopen_locs':[],                          'infectivity':0.6, 'name':'close_all_IF06'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['public','school','work'],  'infectivity':0.6, 'name':'close_all_reopen_all_IF06'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['work'],                    'infectivity':0.5, 'name':'close_all_reopen_work'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['school'],                  'infectivity':0.5, 'name':'close_all_reopen_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['public'],                  'infectivity':0.5, 'name':'close_all_reopen_public'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':[],                          'infectivity':0.5, 'name':'close_public_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['public','school'],         'infectivity':0.5, 'name':'close_public_school_reopen_all'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['school'],                  'infectivity':0.5, 'name':'close_public_school_reopen_school'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['public'],                  'infectivity':0.5, 'name':'close_public_school_reopen_public'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['public','work'],          'reopen_locs':[],                          'infectivity':0.5, 'name':'close_public_work'},
             {'run':0 ,'max_time': 2000, 'start_2':200, 'start_3':500, 'closed_locs':['work','school'],          'reopen_locs':[],                          'infectivity':0.5, 'name':'close_work_school'},
             {'run':0 ,'max_time': 3000, 'start_2':200, 'start_3':500, 'closed_locs':[],                         'reopen_locs':[],                          'infectivity':0.3, 'name':'no_mitigation_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':200, 'start_3':500, 'closed_locs':[],                         'reopen_locs':[],                          'infectivity':0.3, 'name':'no_mitigation_medics_02_IF03', 'hospital_coeff': 0.02},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':1500, 'closed_locs':['public','school','work'], 'reopen_locs':[],                          'infectivity':0.3, 'name':'close_all_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['public','school','work'],  'infectivity':0.3, 'name':'close_all_reopen_all_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['work'],                    'infectivity':0.3, 'name':'close_all_reopen_work_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['school'],                  'infectivity':0.3, 'name':'close_all_reopen_school_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','school','work'], 'reopen_locs':['public'],                  'infectivity':0.3, 'name':'close_all_reopen_public_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':[],                          'infectivity':0.3, 'name':'close_public_school_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['public','school'],         'infectivity':0.3, 'name':'close_public_school_reopen_all_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['school'],                  'infectivity':0.3, 'name':'close_public_school_reopen_school_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','school'],        'reopen_locs':['public'],                  'infectivity':0.3, 'name':'close_public_school_reopen_public_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['public','work'],          'reopen_locs':[],                          'infectivity':0.3, 'name':'close_public_work_IF03'},
             {'run':0 ,'max_time': 3000, 'start_2':250, 'start_3':500, 'closed_locs':['work','school'],          'reopen_locs':[],                          'infectivity':0.3, 'name':'close_work_school_IF03'}]

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
                        13: no_mitigation  IF03\n \
                        14: no_mitigation_medics_02  IF03\n \
                        15: close_all IF03\n \
                        16: close_all_reopen_all IF03\n \
                        17: close_all_reopen_work IF03\n \
                        18: close_all_reopen_school IF03\n \
                        19: close_all_reopen_public IF03\n \
                        20: close_public_school IF03\n \
                        21: close_public_school_reopen_all IF03\n \
                        22: close_public_school_reopen_school IF03\n \
                        23: close_public_school_reopen_public IF03\n \
                        24: close_public_work IF03\n \
                        25: close_work_school ")
    parser.add_argument("-c", "--cores", type=int, help="default 50, used cpu's cores")
    parser.add_argument("-n", "--number", type=int, help="Number of simularions default 100 ")
    parser.add_argument("-w", "--world", type=int, help="number of world in '/home/basar/corona_simulations/saved_objects/worlds' ")
    parser.add_argument("-f", "--folder", type=str, help="defalut '/home/basar/corona_simulations/saved_objects/scenario_output/' ")
    parser.add_argument("-sc", "--scenario", type=str, help="define the simulated scenario_type else: 'default' ")
    parser.add_argument("-p", "--parameter", type=str, help="define the parameter to scan: max_time, start_2, start_3, infectivity, recover_frac")
    parser.add_argument("-pr", "--p_range", nargs='+', type=float, help="define the parameter range (2 inputs): e.g. 1 2 ")
    parser.add_argument("-ps", "--p_steps", type=int, help="define in how many steps the parameter should be scanned (default is 10)")
    parser.add_argument("-d", "--disobedience", type=float, help="disobedience parameter (frequency 0.0-1.0), default 0")
    parser.add_argument("-r", "--reinfections", type=int, help="number of reinfections if reinfection time is not 0 (default 1)")
    parser.add_argument("-rt", "--reinfection_times", nargs='*', type=int, help="times for reinfections (default empty = no reinfections)")
    parser.add_argument("-prod", "--product", type=float, help="fixed product infectivity*mu (default = 0: ignored")
    parser.add_argument("-mu", "--mu", type=float, help="interaction frequency (default = 2")
    parser.add_argument("-rec", "--recovered", type=float, help="fraction (0.0-1.0) of initial recoverd agents default = 0.0")
    parser.add_argument("-rec_world", "--recovered_world", type=float,
                        help="recovered world simulates the world and uses the infection pattern to define the recovered population 0 or 1  (default 1")

    options = parser.parse_args(args)
    return options


def get_previous_infections(world,
                            time_steps=1500,
                            infectivity=0.3,
                            mu=2,
                            save_df_inf=True,
                            folder='saved_objects/',
                            world_name='gangelt',
                            initial_infectees = [1,2,3,4]
                            ):
    world.initialize_infection(specific_people_ids=initial_infectees)
    try:
        df_inf=pd.read_csv(folder+world_name + 'previous_infections.csv')
        print(folder+world_name + 'previous_infections.csv used for infection pattern')
    except:
        simulation_inf_ini = Simulation(world,time_steps,run_immediately=False)
        simulation_inf_ini.change_agent_attributes({'all':{'behaviour_as_infected':{'value':infectivity,'type':'replacement'}}})
        simulation_inf_ini.interaction_frequency = mu
        simulation_inf_ini.simulate()
        df_inf = simulation_inf_ini.get_infection_event_information()
        if save_df_inf:
            df_inf.to_csv(folder+world_name + 'previous_infections.csv')
            print(folder+world_name +
                  'previous_infections.csv is created  for infection pattern')
    return df_inf

def infect_world(world, IDs=[1]):
    ID_list = world.get_remaining_possible_initial_infections(IDs)
    world.initialize_infection(specific_people_ids=ID_list)

def recover_world(world, frac, from_world=True, **kwargs):
    susceptibles = [p.ID for p in world.people if p.status == 'S']
    n = len(susceptibles)

    ## define recovered agents
    if not from_world:
        ps_to_recover = []
        for pid in susceptibles:
            prob=random.random()
            if prob <= frac:
                ps_to_recover.append(pid)
    else:
        df_inf = get_previous_infections(world, **kwargs)
        infected = df_inf['h_ID'].values
        ps_to_recover = infected[:int(frac*n)]
    
    ##recover agents
    for p in world.people:
        if p.ID in ps_to_recover:
            p.set_initially_recovered()

# times: 3 durations for simulations; closed_locs: list of forbidden locations
def simulate_scenario(input_dict):
    '''
    input_dict = {'run':0 ,'max_time': 2000, 'start_2':400, 'start_3':700, 'closed_locs':'public', 'infectivity':0.2, 'name':'scenario_output/default'}
    required: only 'run'
    '''

    my_dict = {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500,
               'closed_locs': ['public', 'school', 'work'], 'reopen_locs': ['public', 'school', 'work'],
               'infectivity': 0.5, 'hospital_coeff': 0.01, 'name': 'default',
               'output_folder': 'scenario_output', 'world':None, 'disobedience': 0,
               'reinfection_times': [], 'reinfections': 1, 'mu': 2, 'product': 0}

    my_dict.update(input_dict)

    max_time = int(my_dict['max_time'])
    start_2 = int(my_dict['start_2'])
    start_3 = int(my_dict['start_3'])
    closed_locs = my_dict['closed_locs']
    reopen_locs = my_dict['reopen_locs']
    infectivity = my_dict['infectivity']
    hospital_coeff = my_dict['hospital_coeff']
    name = my_dict['name']+'_inf_'+str(infectivity)
    modeledWorld = my_dict['world']
    disobedience = my_dict['disobedience']
    reinfection_times = my_dict['reinfection_times']
    reinfections = int(my_dict['reinfections'])
    mu = my_dict['mu']
    product = my_dict['product']

    #print(disobedience, reinfections, reinfection_times)

    #print(type(modeledWorld))
    if len(reinfection_times)>0:
        times = [start_2, start_3, max_time]
        times.extend(reinfection_times)
        times = list(dict.fromkeys(times))  # get rid of duplicates
        times.sort()
    else:
        times = [start_2, start_3, max_time]

    simulation1 = Simulation(modeledWorld, times[0], run_immediately=False)
    if product!=0:
        simulation1.change_agent_attributes(
            {'all': {'behaviour_as_infected': {'value': float(product)/float(mu), 'type': 'replacement'}}})
    else:
        simulation1.change_agent_attributes(
            {'all': {'behaviour_as_infected': {'value': infectivity, 'type': 'replacement'}}})
    simulation1.change_agent_attributes(
        {'all': {'hospital_coeff': {'value': hospital_coeff, 'type': 'replacement'}}})
    #simulation1.set_seed(3)
    simulation1.interaction_frequency=mu
    #simulation1.interaction_matrix = False
    simulation1.simulate(timecourse_keys=['time', 'h_ID', 'status', 'Temporary_Flags', 'Cumulative_Flags', 'loc', 'Infection_event'])
    #simulation1.simulate()

    obedient_people = []

    for p in simulation1.people:
        prob=random.random()
        if not prob < disobedience:
            obedient_people.append(p.ID)

    for i,t in enumerate(times):
        #print(simulation1.time)
        if simulation1.time+1 == start_2:
            for p in simulation1.people:
                if p.ID in obedient_people:
                    for loc in closed_locs:
                        p.stay_home_instead_of_going_to(loc)

        if simulation1.time+1 == start_3:
            for p in simulation1.people:
                p.reset_schedule()
                for loc in list(set(closed_locs)-set(reopen_locs)):
                    if p.ID in obedient_people:
                        p.stay_home_instead_of_going_to(loc)

        if simulation1.time+1 in reinfection_times:
            #print(simulation1.time)
            susceptibles = [p.ID for p in simulation1.people if p.status=='S']
            if len(susceptibles)<=reinfections:
                chosen_ones = susceptibles
            else:
                chosen_ones = random.sample(susceptibles, reinfections)
            #print(chosen_ones)
            for p in simulation1.people:
                if p.ID in chosen_ones:
                    p.get_initially_infected()

        if not simulation1.time+1 == max_time:
            simulation1.time_steps = times[i+1]-t
            #print(simulation1.time_steps)
            simulation1.simulate(timecourse_keys=['time', 'h_ID', 'status', 'Temporary_Flags', 'Cumulative_Flags', 'loc', 'Infection_event'])
            #simulation1.simulate()

    #print(my_dict['name']+'_'+str(my_dict['run']))
    print(name+'_'+str(my_dict['run']))
    print(my_dict['output_folder'])
    #simulation1.save(name+'_'+str(my_dict['run']), date_suffix=False, folder=my_dict['output_folder'])

    return {'stat_trajectories': simulation1.get_status_trajectories(),
                              'durations': simulation1.get_durations(),
            'flag_trajectories': simulation1.get_flag_sums_over_time(),
            'infections_per_location_type':simulation1.get_infections_per_location_type(),
            'number_of_infected_households':simulation1.get_number_of_infected_households(time_span=[0,480])}


def get_simualtion_settings(options):
    input_parameter_dict={}

    if options.scenario_type:  # take scenario type as argument or take default
        input_parameter_dict['scenario_type'] = options.scenario_type
    else:
        input_parameter_dict['scenario_type'] = 0

    if options.cores:  # used cores
        input_parameter_dict['cores'] = options.cores
    else:
        input_parameter_dict['cores'] = 50

    if options.number:  # number of simulations
        input_parameter_dict['number'] = options.number
    else:
        input_parameter_dict['number'] = 100

    if options.world:
        input_parameter_dict['modeledWorld'] = load_simulation_object(world_files[options.world], folder=input_folder)
    else:
        # '/home/basar/corona_simulations/saved_objects/worlds')
        input_parameter_dict['modeledWorld'] = load_simulation_object(world_files[0], folder=input_folder)

    if options.folder:  # number of simulations
        if options.folder.endswith('/'):
            input_parameter_dict['output_folder'] = options.folder
        else:
            input_parameter_dict['output_folder'] = options.folder + '/'
    else:
        input_parameter_dict['output_folder'] = '/home/basar/corona_simulations_save/'
        #output_folder = 'saved_objects/scenario_output/'

    if options.parameter:  # number of simulations
        input_parameter_dict['parameter'] = options.parameter
    else:
        input_parameter_dict['parameter'] = None 

    if options.p_range: # lower and upper bounds are passed
        p_bounds = options.p_range  # if given take list of bounds
        if options.p_steps: # if given take number of steps
            p_steps = options.p_steps
        else:
            p_steps = 10
        input_parameter_dict['p_range'] = np.linspace(p_bounds[0],p_bounds[1],int(p_steps)) # define parameter range/values to simulate
    else:
        input_parameter_dict['p_range'] = np.array([1])

    if options.disobedience:
        input_parameter_dict['disobedience'] = options.disobedience
    else:
        input_parameter_dict['disobedience'] = 0

    if options.reinfections:
        input_parameter_dict['reinfections'] = options.reinfections
    else:
        input_parameter_dict['reinfections'] = 1

    if options.reinfection_times:
        input_parameter_dict['reinfection_times'] = options.reinfection_times
    else:
        input_parameter_dict['reinfection_times'] = []

    if options.product:
        input_parameter_dict['product'] = options.product
    else:
        input_parameter_dict['product'] = 0

    if options.mu:
        input_parameter_dict['mu'] = options.mu
    else:
        input_parameter_dict['mu'] = 2
    
    if options.recovered:
        try:
            assert((options.recovered>=0)&(options.recovered<=1)), "recovered fraction musst be between 0 and 1. ()"
            input_parameter_dict['recovered_frac'] = options.recovered
        except AssertionError as msg:
            print(msg)
            input_parameter_dict['recovered_frac'] = 0.0
    else:
        input_parameter_dict['recovered_frac'] = 0.0

    if options.recovered_world:
        try:
            assert(options.recovered_world in [0,1]
                   ), "recovered fraction musst be 0 or 1"
            input_parameter_dict['recovered_world'] = options.recovered_world
        except AssertionError as msg:
            print(msg)
            input_parameter_dict['recovered_world'] = 1
    else:
        input_parameter_dict['recovered_world'] = 1
    return input_parameter_dict
    #scenario_type, cores, number, modeledWorld, output_folder, parameter, p_range, disobedience, reinfections, reinfection_times, product, mu


def generate_scenario_list(used_scenario, number):
    print('generating scenario list')
    print(used_scenario)
    used_scenarios = [copy.deepcopy(used_scenario) for i in range(number)]
    for i, d in enumerate(used_scenarios):
        d['run'] = i
    return used_scenarios    


if __name__ == '__main__':

    #input_folder =  '/home/basar/corona_simulations_save/saved_objects/Gangelt_big_RPM_02_schedules_v2_ifm/'
    input_folder = 'saved_objects/worldsV2/'
    world_name = 'V2_RPM02_Gangelt_big_'
    world_list = os.listdir(input_folder)
    print(world_list[0])
    # and x.startswith('sim')] needs to be sorted if several simualtions in folder
    world_files = [x for x in world_list if x.endswith('pkl')]
    options = getOptions(sys.argv[1:])
    #scenario_type, cores, number, modeledWorld, output_folder, parameter, p_range, disobedience, reinfections, reinfection_times, product, mu
    input_parameter_dict = get_simualtion_settings(options)
    used_scenario = scenarios[input_parameter_dict['scenario_type']]
    used_scenario.update(input_parameter_dict)
    used_scenario['input_folder'] = input_folder
    used_scenario['world_files'] = world_files
    used_scenario['world_name'] = world_name
    #used_scenario['reinfections'] = input_parameter_dict['reinfections']
    #used_scenario['reinfection_times'] = input_parameter_dict['reinfection_times']
    #used_scenario['disobedience'] = input_parameter_dict['disobedience']
    #used_scenario['product'] = input_parameter_dict['product']
    #used_scenario['mu'] = input_parameter_dict['mu']
    output_folder = used_scenario['output_folder']
    product = used_scenario['product']
    parameter = used_scenario['parameter']
    mu = used_scenario['mu']
    
    for p in used_scenario['p_range']:
        currentWorld = copy.deepcopy(used_scenario['modeledWorld'])
        if used_scenario['parameter'] == 'initial_infections':
            infect_world(currentWorld, IDs=[i+1 for i in range(int(p))])
        else:
            if used_scenario['parameter'] == 'recover_frac':
                recover_world(currentWorld, p, from_world=used_scenario['recovered_world'],
                              time_steps = used_scenario['max_time'],
                              infectivity = used_scenario['infectivity'],
                              mu = mu,
                              save_df_inf = True,
                              folder = output_folder,
                              world_name = world_name,
                              initial_infectees=[1,2,3,4])
                used_scenario[used_scenario['parameter']] = p
                infect_world(currentWorld, IDs=[i+1 for i in range(4)])
                

        if used_scenario['product'] != 0:
            if parameter == 'mu':
                scenario_and_parameter = world_name + used_scenario['name'] + '_prod_'+str(
                    product)+'_inf_'+str(float(product)/float(p))+'_'+str(parameter)+'_'+'{:.3f}'.format(p)
            else:
                scenario_and_parameter = world_name + used_scenario['name'] +'_prod_'+str(product)+'_inf_'+str(float(product)/float(mu))+'_'+str(parameter)+'_'+'{: .3f}'.format(p)
        elif used_scenario['parameter'] == 'recover_frac':
            scenario_and_parameter = world_name + 'Ifreq_'+str(mu)+'_'+used_scenario['name'] + '_'+str(
                parameter)+'_'+'{:.3f}'.format(p)+'_rw_'+str(used_scenario['recovered_world'])
        else:
            scenario_and_parameter = world_name + 'Ifreq_'+str(mu)+'_'+used_scenario['name'] + '_'+str(parameter)+'_'+'{:.3f}'.format(p)

        output_folder_plots = output_folder + 'outputs/' + scenario_and_parameter + '_ri_'+str(used_scenario['reinfections']) + '_rx_'+str(len(used_scenario['reinfection_times'])) +'/'
        #output_folder_plots = 'outputs/' + scenario_and_parameter + '_ri_'+str(reinfections) + '_rx_'+str(len(reinfection_times)) +'/'
        #'/home/basar/corona_simulations_save/'
        used_scenarios = generate_scenario_list(used_scenario, input_parameter_dict['number'])

        for sc in used_scenarios:
            sc['world'] = currentWorld

        try:
            os.mkdir(output_folder_plots)
            os.mkdir(output_folder_plots+'/plots')
        except:
            pass

        #try:
        #    os.mkdir(output_folder + scenario_and_parameter +'/')
        #    print(output_folder + scenario_and_parameter +'/'+' created')
        #except:
        #    pass


        start = timeit.default_timer()

    
        with Pool(input_parameter_dict['cores']) as pool:
            df_dict_list = pool.map(simulate_scenario, used_scenarios)

        status_trajectories_list = [df['stat_trajectories'] for df in df_dict_list]
        simulation_trajectory_list = [df['durations'] for df in df_dict_list]
        flag_trajectories_list = [df['flag_trajectories'] for df in df_dict_list]
        infections_per_location_type_list = [df['infections_per_location_type'] for df in df_dict_list]
        number_of_infected_households_list = [df['number_of_infected_households'] for df in df_dict_list]

        plot_and_save_statii(status_trajectories_list, filename=scenario_and_parameter, output_folder=output_folder_plots) 
        plot_and_save_durations(simulation_trajectory_list, filename=scenario_and_parameter, output_folder=output_folder_plots)
        plot_flags(flag_trajectories_list, cummulative=False, filename=scenario_and_parameter, output_folder=output_folder_plots)
        plot_flags(flag_trajectories_list, cummulative=True, filename=scenario_and_parameter+'_cumulativ', output_folder=output_folder_plots)
        plot_and_save_infection_per_location(infections_per_location_type_list,filename=scenario_and_parameter, output_folder=output_folder_plots)
        save_number_of_infected_households(number_of_infected_households_list, filename=scenario_and_parameter, output_folder=output_folder_plots)

        stop = timeit.default_timer()

        with open(output_folder_plots + 'sim_parameters.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for key in used_scenario:
                writer.writerow([key, used_scenario[key]])
        del(currentWorld)

    print(df_dict_list)
    print('time:  ', stop-start)
