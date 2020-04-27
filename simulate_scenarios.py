from virusPropagationModel import *
import glob
import os
from multiprocessing import Pool
import copy
import timeit
import argparse
import sys
import csv



modeledWorld = ModeledPopulatedWorld(1,10, world_from_file=True, geofile_name='datafiles/Buildings_Gangelt_MA_3.csv', agent_agent_infection=True, input_schedules='schedules_v1')
modeledWorld.save('OneWorld', date_suffix=False )
#modeledWorld = load_simulation_object('OneWorld')
#scenarios = [{'run':1},{'run':2}]
scenarios = [{'run':0 ,'max_time': 2000, 'start_2':1800, 'start_3':1900, 'closed_locs':[], 'reopen_locs':[], 'infectivity':0.2, 'name':'default'},
             {'run':0 ,'max_time': 2000, 'start_3':500, 'reopen_locs':['school'], 'infectivity':0.2, 'name':'reopen_schools_100'},
             {'run':0 ,'max_time': 2000, 'start_3':600, 'reopen_locs':['school'], 'infectivity':0.2, 'name':'reopen_schools_200'},
             {'run':0 ,'max_time': 2000, 'start_3':700, 'reopen_locs':['school'], 'infectivity':0.2, 'name':'reopen_schools_300'},
             {'run':0 ,'max_time': 2000, 'start_3':900, 'reopen_locs':['school'], 'infectivity':0.2, 'name':'reopen_schools_500'}]

output_folder = 'scenario_output'


def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-st", "--scenario_type", type=int, help="Choose your scenario_type else default")
    #parser.add_argument("-ma", "--min_area", type=int, help="default 3  (*1e-8) to reduce locations")
    #parser.add_argument("-n", "--number", type=int, help="A number.")
    #parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode.")
    options = parser.parse_args(args)
    return options


def simulate_scenario(input_dict):   # times: 3 durations for simulations; closed_locs: list of forbidden locations
    '''
    input_dict = {'run':0 ,'max_time': 2000, 'start_2':400, 'start_3':700, 'closed_locs':'public', 'infectivity':0.2, 'name':'scenario_output/default'}
    required: only 'run'
    '''

    my_dict = {'run':0 ,'max_time': 2000, 'start_2':400, 'start_3':700, 'closed_locs':['public','school','work'], 'reopen_locs':['public','school','work'], 'infectivity':0.2, 'name':'default'}

    my_dict.update(input_dict)

    max_time = my_dict['max_time']
    start_2 = my_dict['start_2']
    start_3 = my_dict['start_3']
    closed_locs = my_dict['closed_locs']
    infectivity = my_dict['infectivity']
    name = my_dict['name']

    simulation1 = Simulation(modeledWorld, start_2, run_immediately=False)
    simulation1.change_agent_attributes({'all':{'behaviour_as_infected':{'value':infectivity,'type':'replacement'}}})
    simulation1.simulate()

    simulation2 = Simulation(simulation1, start_3-start_2, run_immediately=False)
    del simulation1
    for p in simulation2.people:
        for loc in closed_locs:
            p.stay_home_instead_of_going_to(loc)
    simulation2.simulate()

    simulation3 = Simulation(simulation2, max_time-start_3, run_immediately=False)
    del simulation2
    for p in simulation3.people:
        p.reset_schedule()
    simulation3.simulate()

    print(my_dict['name']+'_'+str(my_dict['run']))
    simulation3.save( output_folder+'/'+name+'_'+str(my_dict['run']), date_suffix=False )
    return simulation3.time

if __name__=='__main__':

    options = getOptions(sys.argv[1:])

    if options.scenario_type: # take scenario type as argument or take default
        scenario_type = options.scenario_type   
    else:
        scenario_type = 0

    used_scenario = scenarios[scenario_type]
    used_scenarios = [copy.deepcopy(used_scenario) for i in range(4)]

    for i,d in enumerate(used_scenarios):
        d['run']=i    

    if not output_folder in os.listdir('saved_objects'):
        os.mkdir('saved_objects/'+output_folder)
        print('saved_objects/'+output_folder+' created')
    #else:
    #    os.mkdir('saved_objects/'+output_folder+)
    #    print('saved_objects/'+output_folder+' created')
        

    start = timeit.default_timer()

    with Pool(15) as pool:
        result = pool.map(simulate_scenario, used_scenarios)

    stop = timeit.default_timer()

    used_scenario['runs']=len(used_scenarios)
    
    with open('saved_objects/'+output_folder+'/sim_parameters.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for key in used_scenario:
            writer.writerow([key, used_scenario[key]])

    print(result)
    print('time:  ',stop-start)