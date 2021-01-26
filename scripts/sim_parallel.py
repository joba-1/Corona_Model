#!/usr/bin/env python3

import glob
import os
import copy
import timeit
import argparse
import sys
import csv
import pickle
import random

import numpy as np
import gerda.utilities.VPM_save_and_load as vpm_save_load

from multiprocessing import Pool
from gerda.core.virusPropagationModel import *
from gerda.utilities.parallel_utilities import *


scenarios = [{'run': 0, 'max_time': 2000, 'start_2': 50, 'start_3': 100, 'closed_locs': [], 'reopen_locs':[], 'infectivity':0.0, 'name':'no_mitigation_IF00'},

             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': [],                         'reopen_locs':[
             ],                          'infectivity':0.5, 'name':'no_mitigation_medics_02', 'hospital_coeff': 0.02},
             {'run': 0, 'max_time': 600, 'start_2': 200, 'start_3': 500, 'closed_locs': [
                 'public', 'school', 'work'], 'reopen_locs':[],                          'infectivity':0.3, 'name':'close_all_IF06'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'public', 'school', 'work'],  'infectivity':0.6, 'name':'close_all_reopen_all_IF06'},
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

             {'run': 0, 'max_time': 3000, 'start_2': 200, 'start_3': 300, 'closed_locs': [],
                 'reopen_locs':[],                          'infectivity':0.3, 'name':'no_mitigation_IF03'},

             {'run': 0, 'max_time': 3000, 'start_2': 200, 'start_3': 500, 'closed_locs': [],                         'reopen_locs':[
             ],                          'infectivity':0.3, 'name':'no_mitigation_medics_02_IF03', 'hospital_coeff': 0.02},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 1500, 'closed_locs': [
                 'public', 'school', 'work'], 'reopen_locs':[],                          'infectivity':0.3, 'name':'close_all_IF03'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'public', 'school', 'work'],  'infectivity':0.3, 'name':'close_all_reopen_all_IF03'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'work'],                    'infectivity':0.3, 'name':'close_all_reopen_work_IF03'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'school'],                  'infectivity':0.3, 'name':'close_all_reopen_school_IF03'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['public', 'school', 'work'], 'reopen_locs':[
                 'public'],                  'infectivity':0.3, 'name':'close_all_reopen_public_IF03'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
             ],                          'infectivity':0.3, 'name':'close_public_school_IF03'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
                 'public', 'school'],         'infectivity':0.3, 'name':'close_public_school_reopen_all_IF03'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
                 'school'],                  'infectivity':0.3, 'name':'close_public_school_reopen_school_IF03'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['public', 'school'],        'reopen_locs':[
                 'public'],                  'infectivity':0.3, 'name':'close_public_school_reopen_public_IF03'},
             {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500, 'closed_locs': ['public', 'work'],          'reopen_locs':[
             ],                          'infectivity':0.3, 'name':'close_public_work_IF03'},
             {'run': 0, 'max_time': 3000, 'start_2': 250, 'start_3': 500, 'closed_locs': ['work', 'school'],          'reopen_locs':[],                          'infectivity':0.3, 'name':'close_work_school_IF03'},
             {'run': 0, 'max_time': 2000, 'start_2': 250, 'start_3': 1900, 'closed_locs': ['public'],          'reopen_locs':[],                          'infectivity':0.15, 'name':'close_public_IF015'}]

#world_list = os.listdir('/home/basar/corona_simulations/saved_objects/worlds')
#world_files = [input_folder+'/'+x for x in file_list if x.endswith('pkl')]

'''
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
                        25: close_work_school
                        26: close_public IF015
'''

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-st", "--scenario_type", type=int, help="Choose your scenario_type else default \n \
                        13: no_mitigation  IF03\n \
                        15: close_all IF03\n \
                        16: close_all_reopen_all IF03\n \
                        17: close_all_reopen_work IF03\n \
                        18: close_all_reopen_school IF03\n \
                        19: close_all_reopen_public IF03")
    parser.add_argument("-c", "--cores", type=int, help="default 50, used cpu's cores")
    parser.add_argument("-n", "--number", type=int, help="Number of simularions default 100 ")
    parser.add_argument("-w", "--world", type=int,
                        help="number of world in '/home/basar/corona_simulations/saved_objects/worlds' ")
    parser.add_argument("-f", "--folder", type=str,
                        help="defalut '/home/basar/corona_simulations/saved_objects/scenario_output/' ")
    parser.add_argument("-sc", "--scenario", type=str,
                        help="define the simulated scenario_type else: 'default' ")
    parser.add_argument("-p", "--parameter", type=str,
                        help="define the parameter to scan: max_time, start_2, start_3, infectivity, recover_frac")
    parser.add_argument("-pr", "--p_range", nargs='+', type=float,
                        help="define the parameter range (2 inputs): e.g. 1 2 ")
    parser.add_argument("-ps", "--p_steps", type=int,
                        help="define in how many steps the parameter should be scanned (default is 10)")
    parser.add_argument("-d", "--disobedience", type=float,
                        help="disobedience parameter (frequency 0.0-1.0), default 0")
    parser.add_argument("-r", "--reinfections", type=int,
                        help="number of reinfections if reinfection time is not 0 (default 1)")
    parser.add_argument("-rt", "--reinfection_times", nargs='*', type=int,
                        help="times for reinfections (default empty = no reinfections)")
    parser.add_argument("-prod", "--product", type=float,
                        help="fixed product infectivity*mu (default = 0: ignored)")
    parser.add_argument("-mu", "--mu", type=float, help="interaction frequency (default = 2)")
    parser.add_argument("-rec", "--recovered", type=float,
                        help="fraction (0.0-1.0) of initial recoverd agents default = 0.0")
    parser.add_argument("-rec_by", "--recover_by", type=str,
                        help="choose how initial recovered agents are obtained (random, world, overrepresentation, interactions, households) ")
    parser.add_argument("-rec_schedule", "--recovered_schedule", type=str,
                        help="simulates the world after recovering all agents with given schedule type (default=None)")
    parser.add_argument("-mht", "--max_houshold_time", type=int,
                        help="max time for monitoring infected housholds (default is None ->max)")
    parser.add_argument("-mix", "--mixing", type=bool,
                        help="use homogeneous mixing when True (default is False)")
    parser.add_argument("-iar", "--im_age_range", nargs='+', type=float,
                        help="""choose the interaction modifier for a specific age range 
                        in order : IM min_age max_age (default 1 -1 100)""")
    parser.add_argument("-part_imnty", "--partial_immunity", type=float,
                        help="""choose value (0-1) for partial immunity""")
    parser.add_argument("-imnty_mode", "--immunity_mode", type=str,
                        help="""choose if partial immunity is as susceptible ('sus') or infected ('inf') or both ('both') """)
    options = parser.parse_args(args)
    return options

# /home/basar/corona_simulations_save/outputs/parralel_HM_V2_recover_testing_Ifreq_2_no_mitigation_IF03_None_ri_1_rx_0/parralel_HM_V2_recover_testing_Ifreq_2_no_mitigation_IF03_None_1.000_ri_1_rx_0/infection_informations/
# IAR_1_0_99_parralel_HM_V2_recover_testing_Ifreq_2_no_mitigation_IF03_None_1.000_infection_information_0.csv

def get_previous_infections(world, n,
                            save_folder='',
                            time_steps=1500,
                            infectivity=0.3,
                            mu=2,
                            save_df_inf=True,
                            folder='saved_objects/',
                            world_name='gangelt',
                            initial_infectees=[1, 2, 3, 4]
                            ):
    world.initialize_infection(specific_people_ids=initial_infectees)
    #print(folder+world_name + 'previous_infections.csv')
    #folder_name = '/home/basar/corona_simulations_save/simulation_results_20201028/base_scenario_inf_0.15/parralel_HM_V2_recover_scan_Ifreq_2_no_mitigation_IF015_None_1.000_ri_1_rx_0/infection_informations/'
    #file_name = 'IAR_1_0_99_parralel_HM_V2_recover_scan_Ifreq_2_no_mitigation_IF015_None_1.000_infection_information_'+str(n)+'.csv'
    folder_name = '/home/basar/corona_simulations_save/outputs/new_sim_obj_Ifreq_2_no_mitigation_IF03_None_ri_1_rx_0/new_sim_obj_Ifreq_2_no_mitigation_IF03_None_1.000_ri_1_rx_0/infection_informations/'
    file_name = 'new_sim_obj_Ifreq_2_no_mitigation_IF03_None_1.000_infection_information_'+str(n)+'.csv'

    try:
        df_inf = pd.read_csv(folder_name+file_name)
        print(folder_name+file_name + ' used for infection pattern')
    except:
        print('no files found, simulating previous infections.')
        simulation_inf_ini = Simulation(world, time_steps, run_immediately=False)
        simulation_inf_ini.change_agent_attributes(
            {'all': {'behaviour_as_infected': {'value': infectivity, 'type': 'replacement'}}})
        simulation_inf_ini.interaction_frequency = mu
        simulation_inf_ini.simulate()
        df_inf = simulation_inf_ini.get_infection_event_information()
        if save_df_inf:
            df_inf.to_csv(folder+world_name + 'previous_infections.csv')
            print(folder+world_name +
                  'previous_infections.csv is created  for infection pattern')
    infected = list(df_inf['h_ID'].values)
    all_agents = infected+[a.ID for a in world.people if a.ID not in infected]
    return all_agents


def infect_world(world, IDs=[1], exclude_list=[]):
    ID_list = world.get_remaining_possible_initial_infections(IDs, exclude_list)
    world.initialize_infection(specific_people_ids=ID_list)

def get_ordered_ids(world, n, save_folder='', **kwargs):
    schedule_types = ['under_age', 'adult', 'teacher', 'medical_professional', 'public_worker', 'pensioner']
    ids_by_type = {s_type:[] for s_type in schedule_types}
    for p in world.people:
        ids_by_type[p.schedule['type']].append(p.ID)
    ordered_ids = []
    for s_type in schedule_types:
        ordered_ids.extend(ids_by_type[s_type])
    return ordered_ids

def get_ids_by_interactions(world, n, save_folder='', **kwargs):
    server_data_folder = 'saved_objects/new_sim_obj_no_infections_Ifreq_2_no_mitigation_IF00_None_ri_1_rx_0/new_sim_obj_no_infections_Ifreq_2_no_mitigation_IF00_None_1.000_ri_1_rx_0/'
    filename = 'new_sim_obj_no_infections_Ifreq_2_no_mitigation_IF00_None_1.000_'
    contacts = pd.read_csv(server_data_folder+filename+'contacts.csv')
    contacts_mean = contacts.groupby('ID').mean()
    contacts_mean.reset_index(inplace=True)
    contacts_sorted = contacts_mean.sort_values('interactions', axis=0, ascending=False)
    #contacts_sorted = pd.read_csv(save_folder+'agents_sorted_by_interactions_0.5_0.9.csv')
    contacts_sorted.to_csv(save_folder+'agents_sorted_by_interactions.csv')
    to_recover_list = list(contacts_sorted['ID'].values)
    return to_recover_list

def get_ids_by_households(world, n, save_folder='', **kwargs):
    #server_data_folder = 'outputs/no_infections/parralel_HM_V2_no_inf_mix_Ifreq_2.0_no_mitigation_IF06_None_1.000_ri_1_rx_0/'
    #filename = 'IAR_1_0_99_parralel_HM_V2_no_inf_mix_Ifreq_2.0_no_mitigation_IF06_None_1.000_'
    ai = world.get_agent_infos()
    home_count_dict = dict(zip(list(ai.groupby('Home').count().index), list(ai.groupby('Home').count()['ID'])))
    ai['Home_size']=ai['Home'].map(home_count_dict)

    ai_sorted = ai.sort_values('Home')
    home_list = ai_sorted['Home'].values

    count_list=[]
    predecessor = 0
    count = 1
    for x in home_list:
        if x == predecessor:
            count +=1
        else:
            count = 1
        count_list.append(count)
        predecessor = x

    ai_sorted['Home_position'] = count_list

    ai_sorted.sort_values('Home_position') ## dataframe
    households_sorted = ai_sorted.sort_values(by=['Home_position'])
    households_sorted.to_csv(save_folder+'agents_sorted_by_households.csv')
    to_recover_list = list(households_sorted['ID']) ### id list
    return to_recover_list

def get_random_id_list(world, n, save_folder='', **kwargs):
    agent_ids = [p.ID for p in world.people]
    random.shuffle(agent_ids)
    #df = pd.read_csv('/home/basar/corona_simulations_save/simulation_results_20201028/recover_random_scan_0.5_0.9/recovery_id_lists.csv')
    #print(df)
    #agent_ids = list(df[str(n)])
    return agent_ids

def get_ids_by_age(world, n, save_folder='', **kwargs):
    ages_and_ids = [(p.age, p.ID) for p in world.people]
    ages_and_ids_df = pd.DataFrame(ages_and_ids, columns=['age','id'])
    ages_and_ids_df.sort_values('age', ascending=False, inplace=True)
    #ages_and_ids_df = pd.read_csv('/home/basar/corona_simulations_save/outputs/parralel_HM_V2_recover_scan_Ifreq_2_no_mitigation_IF03_recover_frac_rec_age_ri_1_rx_0/ages_and_ids_0.5_0.9.csv')
    ages_and_ids_df.to_csv(save_folder+'ages_and_ids.csv')
    ids_only = list(ages_and_ids_df['id'])
    return ids_only

def get_ids_by_age_and_interactions(world, n, save_folder='', **kwargs):
    server_data_folder = 'outputs/new_sim_obj_no_infections_Ifreq_2_no_mitigation_IF00_None_ri_1_rx_0/new_sim_obj_no_infections_Ifreq_2_no_mitigation_IF00_None_1.000_ri_1_rx_0/'
    filename = 'new_sim_obj_no_infections_Ifreq_2_no_mitigation_IF00_None_1.000_'
    contacts = pd.read_csv(server_data_folder+filename+'contacts.csv')
    contacts_mean = contacts.groupby('ID').mean()
    contacts_sorted = contacts_mean.sort_values('interactions', axis=0, ascending=False)

    ages_and_ids = [(p.age, p.ID) for p in world.people]
    ages_and_ids_df = pd.DataFrame(ages_and_ids, columns=['age','id'])
    ages_and_ids_under_thirteen = ages_and_ids_df[ages_and_ids_df['age']<13]
    ages_and_ids_under_thirteen.sort_values('age', ascending=False, inplace=True)
    #ages_and_ids_under_thirteen = pd.read_csv(save_folder+'ages_and_ids_under_13_0.5_0.9.csv')
    ages_and_ids_under_thirteen.to_csv(save_folder+'ages_and_ids_under_13_0.1_0.46.csv')

    ages_and_ids_short = ages_and_ids_df[ages_and_ids_df['age']>59]
    ages_and_ids_short.sort_values('age', ascending=False, inplace=True)
    #ages_and_ids_short = pd.read_csv(save_folder+'ages_and_ids_over_59_0.5_0.9.csv')
    ages_and_ids_short.to_csv(save_folder+'ages_and_ids_over_59_0.1_0.46.csv')

    contacts_sorted.drop(index=list(ages_and_ids_under_thirteen['id'])+list(ages_and_ids_short['id']), inplace=True)
    #contacts_sorted = pd.read_csv(save_folder+'ages_13_to_59_by_interactions_0.5_0.9.csv')
    contacts_sorted.to_csv(save_folder+'ages_13_to_59_by_interactions_0.1_0.46.csv')

    final_ids = list(ages_and_ids_short['id'])+list(contacts_sorted.index)+list(ages_and_ids_under_thirteen['id'])
    return final_ids

def get_ids_for_recovery(world, rec_by, n, save_folder='', **kwargs):
    print(kwargs)
    ids_list=[]
    if rec_by:
        get_ids_func = get_rec_by(rec_by)
        for i in range(n):
            ids_list.append(get_ids_func(world, i, save_folder=save_folder, **kwargs))
    else:
        for i in range(n):
            ids_list.append([])
    #print(ids_list)
    df_ids_list = pd.DataFrame({i: l for i,l in enumerate(ids_list)})
    df_ids_list.to_csv(save_folder+'recovery_id_lists.csv')
    return ids_list

def get_rec_by(rec_by):
    switcher = {
        'random': get_random_id_list,
        'world': get_previous_infections,
        'overrepresentation': get_ordered_ids,
        'interactions': get_ids_by_interactions,
        'households': get_ids_by_households,
        'age': get_ids_by_age,
        'age_interactions': get_ids_by_age_and_interactions,
    }
    return switcher.get(rec_by)

def recover_world(world, frac, recover_id_list):

    ps_to_recover = recover_id_list[:int(frac*len(recover_id_list))]

    # recover agents
    for p in world.people:
        if p.ID in ps_to_recover:
            p.set_initially_recovered()
    return ps_to_recover

def partially_immunise_world(world, frac, recover_id_list, immunity_factor, imnty_mode='sus'):

    ps_to_recover = recover_id_list[:int(frac*len(recover_id_list))]

    # recover agents
    for p in world.people:
        if p.ID in ps_to_recover:
            if imnty_mode=='sus' or imnty_mode=='both':  
                p.behaviour_as_susceptible *= immunity_factor
            if imnty_mode=='inf' or imnty_mode=='both':  
                p.behaviour_as_infected *= immunity_factor
    return ps_to_recover


def set_interaction_modifier_for_age_range(world, iar_list, keep_average=True,):
    """
    set interaction modifier for agents with min_age<age<max_age,
    and if  keep_average: change the modfifier for the rest accordingly
    """
    im = iar_list[0]
    min_age = iar_list[1]
    max_age = iar_list[2]
    p_subset_ids = [p.ID for p in world.people if (
        p.age > min_age) & (p.age < max_age)]
    world.set_im_for_subset(im, id_list=p_subset_ids)
    print('nr of agents with changed IM', len(p_subset_ids))


def simulate_scenario(input_dict):
    '''
    input_dict = {'run':0 ,'max_time': 2000, 'start_2':400, 'start_3':700, 'closed_locs':'public', 'infectivity':0.2, 'name':'scenario_output/default'}
    required: only 'run'
    '''

    my_dict = {'run': 0, 'max_time': 2000, 'start_2': 200, 'start_3': 500,
               'closed_locs': ['public', 'school', 'work'], 'reopen_locs': ['public', 'school', 'work'],
               'infectivity': 0.5, 'hospital_coeff': 0.01, 'name': 'default',
               'output_folder': 'scenario_output', 'world': None, 'disobedience': 0,
               'reinfection_times': [], 'reinfections': 1, 'mu': 2, 'product': 0, 'mix': False, 'home_office': 0.0,
               'recover_lists':[[]], 'recover_fraction': 0.0, 'infectees':[1,2,3,4]}

    my_dict.update(input_dict)

    max_time = int(my_dict['max_time'])
    start_2 = int(my_dict['start_2'])
    start_3 = int(my_dict['start_3'])
    closed_locs = my_dict['closed_locs']
    reopen_locs = my_dict['reopen_locs']
    infectivity = my_dict['infectivity']
    hospital_coeff = my_dict['hospital_coeff']
    name = my_dict['name']+'_inf_'+str(infectivity)
    modeledWorld = copy.deepcopy(my_dict['world'])
    disobedience = my_dict['disobedience']
    reinfection_times = my_dict['reinfection_times']
    reinfections = int(my_dict['reinfections'])
    mu = my_dict['mu']
    product = my_dict['product']
    max_houshold_time = my_dict['max_houshold_time']
    # ['time', 'h_ID', 'status', 'Temporary_Flags', 'Cumulative_Flags', 'loc', 'Infection_event']
    timecourse_keys = my_dict['timecourse_keys']
    mix = my_dict['mix']
    home_office = my_dict['home_office']
    recover_lists = my_dict['recover_lists']
    infectees = my_dict['infectees']
    recover_fraction = my_dict['recover_fraction']
    part_imnty = my_dict['part_imnty']
    imnty_mode = my_dict['imnty_mode']

    if part_imnty:
        recover_list = partially_immunise_world(modeledWorld, recover_fraction, recover_lists[my_dict['run']], part_imnty, imnty_mode=imnty_mode)
    else:
        recover_list = recover_world(modeledWorld, recover_fraction, recover_lists[my_dict['run']])
    infect_world(modeledWorld, IDs=infectees, exclude_list=recover_list)

    # print(type(modeledWorld))
    if len(reinfection_times) > 0:
        times = [start_2, start_3, max_time]
        times.extend(reinfection_times)
        times = list(dict.fromkeys(times))  # get rid of duplicates
        times.sort()
    else:
        times = [start_2, start_3, max_time]

    simulation1 = Simulation(modeledWorld, times[0], run_immediately=False)

    del(modeledWorld)

    if mix:
        simulation1.set_homogeneous_mixing()

    if product != 0:
        simulation1.change_agent_attributes(
            {'all': {'behaviour_as_infected': {'value': float(product)/float(mu), 'type': 'multiplicative_factor'}}})
    else:
        simulation1.change_agent_attributes(
            {'all': {'behaviour_as_infected': {'value': infectivity, 'type': 'multiplicative_factor'}}})
    #simulation1.change_agent_attributes(
     #   {'all': {'hospital_coeff': {'value': hospital_coeff, 'type': 'multiplicative_factor'}}}) 

    # simulation1.set_seed(3)
    simulation1.interaction_frequency = mu
    #simulation1.interaction_matrix = False
    simulation1.simulate(timecourse_keys=timecourse_keys)
    # simulation1.simulate()

    obedient_people = []
    outside_workers = []

    for p in simulation1.people:
        prob = random.random()
        if not prob < disobedience:
            obedient_people.append(p.ID)
    for p in simulation1.people:
        if p.schedule['type']=='adult':
            prob = random.random()
            if not prob < home_office:
                outside_workers.append(p.ID)

    for i, t in enumerate(times):
        # print(simulation1.time)
        if simulation1.time+1 == start_2:
            infectivities_at_2 = simulation1.get_infectivities()
            for p in simulation1.people:
                if p.ID in obedient_people:
                    for loc in closed_locs:
                        if not (loc=='work' and p.ID in outside_workers):
                            p.stay_home_instead_of_going_to(loc)

        if simulation1.time+1 == start_3:
            infectivities_at_3 = simulation1.get_infectivities()
            for p in simulation1.people:
                p.reset_schedule()
                for loc in list(set(closed_locs)-set(reopen_locs)):
                    if p.ID in obedient_people:
                        p.stay_home_instead_of_going_to(loc)

        if simulation1.time+1 in reinfection_times:
            # print(simulation1.time)
            susceptibles = [p.ID for p in simulation1.people if p.status == 'S']
            if len(susceptibles) <= reinfections:
                chosen_ones = susceptibles
            else:
                chosen_ones = random.sample(susceptibles, reinfections)
            # print(chosen_ones)
            for p in simulation1.people:
                if p.ID in chosen_ones:
                    p.get_initially_infected()

        if not simulation1.time+1 == max_time:
            simulation1.time_steps = times[i+1]-t
            for p in simulation1.people:
                if p.loc not in simulation1.locations.values():
                    print('ploc:',p.loc.ID,'; ltype:',p.loc.location_type,'; agent:',p.ID,'; diagnosed:',p.diagnosed,'; was diagnosed:',p.was_diagnosed)
                    print('times:', p.stati_times)
                    print(simulation1.locations[p.loc.ID].location_type)
                    print(id(simulation1.locations[p.loc.ID]), id(p.loc))
                else:
                    print('no additional locations found')
            # print(simulation1.time_steps)
            print(simulation1.time)
            simulation1.simulate(timecourse_keys=timecourse_keys)
            # simulation1.simulate()
        for p in simulation1.people:
            if p.loc not in simulation1.locations.values():
                print('ploc:',p.loc.ID,'; ltype:',p.loc.location_type,'; agent:',p.ID,'; diagnosed:',p.diagnosed,'; was diagnosed:',p.was_diagnosed)
                print('times:', p.stati_times)
                print(simulation1.locations[p.loc.ID].location_type)
                print(id(simulation1.locations[p.loc.ID]), id(p.loc))
            else:
                print('no additional locations found')

    # print(my_dict['name']+'_'+str(my_dict['run']))
    print(name+'_'+str(my_dict['run']))
    print(my_dict['output_folder'])
    #simulation1.save(name+'_'+str(my_dict['run']), date_suffix=False, folder=my_dict['output_folder'])

    try:
        infectivities_at_2
    except NameError:
        print('infectivities_at_2 does not exist')
        infectivities_at_2 = pd.DataFrame(columns = ['ID','infectivity'])

    try:
        infectivities_at_3
    except NameError:
        print('infectivities_at_3 does not exist')
        infectivities_at_3 = pd.DataFrame(columns = ['ID','infectivity'])

    df_transition_times = simulation1.get_agent_specific_duration_info()
    df_transition_times['run'] = [my_dict['run']]*len(df_transition_times)

    df_recover_list = pd.DataFrame({my_dict['run']: recover_list})   

    sim_dict = {
        #'timecourse': simulation1.simulation_timecourse,
        'stat_trajectories': simulation1.get_status_trajectories(),
        'durations': simulation1.get_durations(),
        'flag_trajectories': simulation1.get_flag_sums_over_time(),
        'number_of_infected_households': simulation1.get_number_of_infected_households(time_span=[0, max_houshold_time]),
        'infection_timecourse': simulation1.get_infection_event_information(),
        'infection_patterns': simulation1.get_age_group_specific_infection_patterns(),
        #'r_eff': simulation1.get_r_eff_trajectory(96),
        #'cumaltive_unique_contacts': simulation1.get_contact_distributions(),
        'infections_per_schedule_type': simulation1.get_infections_per_schedule_type(fraction_most_infectious=1., relative=True),
        'infections_per_location_type': simulation1.get_infections_per_location_type(relative=True),
        #'contact_distribution_per_week': simulation1.get_contact_distributions(min_t=0, max_t=168),
        'infectivities_at_2': infectivities_at_2,
        'infectivities_at_3': infectivities_at_3,
        'transition_times': df_transition_times,
        'recovered_list': df_recover_list,
    }

    if 'Interaction_partner' in timecourse_keys:
        sim_dict['interaction_patterns'] = simulation1.get_age_group_specific_interaction_patterns()
        #sim_dict['contact_tracing'] = simulation1.contact_tracing(tracing_window=240,
         #                                                         loc_time_overlap_tracing=False,
          #                                                        trace_all_following_infections=True)
    return sim_dict


def get_simualtion_settings(options):
    input_parameter_dict = {}

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
        input_parameter_dict['modeledWorld'] = vpm_save_load.load_world_object(
            world_files[options.world], folder=input_folder)
    else:
        # '/home/basar/corona_simulations/saved_objects/worlds')
        input_parameter_dict['modeledWorld'] = vpm_save_load.load_world_object(
            world_files[0], folder=input_folder)

    if options.folder:  # number of simulations
        if options.folder.endswith('/'):
            input_parameter_dict['output_folder'] = options.folder
        else:
            input_parameter_dict['output_folder'] = options.folder + '/'
    else:
        #input_parameter_dict['output_folder'] = '/home/basar/corona_simulations_save/'
        input_parameter_dict['output_folder'] = ''

    if options.parameter:  # number of simulations
        input_parameter_dict['parameter'] = options.parameter
    else:
        input_parameter_dict['parameter'] = None

    if options.p_range:  # lower and upper bounds are passed
        p_bounds = options.p_range  # if given take list of bounds
        if options.p_steps:  # if given take number of steps
            p_steps = options.p_steps
        else:
            p_steps = 10
        input_parameter_dict['p_range'] = np.linspace(p_bounds[0], p_bounds[1], int(
            p_steps))  # define parameter range/values to simulate
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

    if options.max_houshold_time:
        input_parameter_dict['max_houshold_time'] = options.max_houshold_time
    else:
        input_parameter_dict['max_houshold_time'] = None

    if options.recovered:
        try:
            assert((options.recovered >= 0) & (options.recovered <= 1)
                   ), "recovered fraction musst be between 0 and 1. ()"
            input_parameter_dict['recover_fraction'] = options.recovered
        except AssertionError as msg:
            print(msg)
            input_parameter_dict['recover_fraction'] = 0.0
    else:
        input_parameter_dict['recover_fraction'] = 0.0

    if options.recovered_schedule:
        input_parameter_dict['rec_schedule'] = options.recovered_schedule
    else:
        input_parameter_dict['rec_schedule'] = None

    if options.recover_by:
        try:
            assert(options.recover_by in ['random','world','overrepresentation','interactions','households','age','age_interactions']
                   ), "recover by must be in ['random','world','overrepresentation','interactions','households','age','age_interactions']"
            input_parameter_dict['recover_by'] = options.recover_by
        except AssertionError as msg:
            print(msg)
            input_parameter_dict['recover_by'] = ''
    else:
        input_parameter_dict['recover_by'] = ''

    if options.mixing:
        input_parameter_dict['mix'] = options.mixing
    else:
        input_parameter_dict['mix'] = False

    if options.im_age_range:  # interaction modifier, lower and upper bounds for ages are passed
        # if given take list of bounds
        input_parameter_dict['im_age_range'] = options.im_age_range
    else:
        input_parameter_dict['im_age_range'] = [1,-1,100] # nothing changes IM 1 -1<age<100

    if options.partial_immunity:
        input_parameter_dict['part_imnty'] = options.partial_immunity
    else:
        input_parameter_dict['part_imnty'] = None 

    if options.immunity_mode:
        input_parameter_dict['imnty_mode'] = options.immunity_mode
    else:
        input_parameter_dict['imnty_mode'] = 'sus' 

    return input_parameter_dict
    #scenario_type, cores, number, modeledWorld, output_folder, parameter, p_range, disobedience, reinfections, reinfection_times, product, mu


def generate_scenario_list(used_scenario, number):
    print('generating scenario list')
    for k in used_scenario:
        if not k=='recover_lists':
            print(k, used_scenario[k])
    used_scenarios = [copy.deepcopy(used_scenario) for i in range(number)]
    for i, d in enumerate(used_scenarios):
        d['run'] = i
    return used_scenarios


if __name__ == '__main__':

    #input_folder =  '/home/basar/corona_simulations_save/saved_objects/worlds_V2_RPM2_Gangel/'
    input_folder = 'models/new_sim_obj/'
    world_name = 'new_sim_obj_partial_imnty_sus_'
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
    used_scenario['timecourse_keys'] = ['time', 'h_ID', 'status',
                                        'Temporary_Flags', 'Cumulative_Flags',
                                        'loc', 'Infection_event', 'Interaction_partner']  # Interaction_partner
    #used_scenario['reinfections'] = input_parameter_dict['reinfections']
    #used_scenario['reinfection_times'] = input_parameter_dict['reinfection_times']
    #used_scenario['disobedience'] = input_parameter_dict['disobedience']
    #used_scenario['product'] = input_parameter_dict['product']
    #used_scenario['mu'] = input_parameter_dict['mu']
    output_folder = used_scenario['output_folder']
    product = used_scenario['product']
    parameter = used_scenario['parameter']
    mu = used_scenario['mu']
    rec_by = used_scenario['recover_by']
    currentWorld = used_scenario['modeledWorld']

    if used_scenario['product'] != 0:
        if parameter == 'mu':
            scenario_and_parameter = world_name + used_scenario['name'] + '_prod_'+str(
                product)
        else:
            scenario_and_parameter = world_name + used_scenario['name'] + '_prod_'+str(
                product)
    elif used_scenario['parameter'] == 'recover_frac':
        scenario_and_parameter = world_name + 'Ifreq_'+str(mu)+'_'+used_scenario['name'] + '_'+str(
            parameter)+'_rec_'+str(used_scenario['recover_by'])
    else:
        scenario_and_parameter = world_name + 'Ifreq_' + \
            str(mu)+'_'+used_scenario['name'] + '_'+ str(parameter)
    if used_scenario['mix']:
        scenario_and_parameter = 'mix_'+ scenario_and_parameter

    collector_folder = output_folder + 'outputs/' + scenario_and_parameter + '_ri_' + \
        str(used_scenario['reinfections']) + '_rx_' + \
        str(len(used_scenario['reinfection_times'])) + '/'

    try:
        os.mkdir(collector_folder)
        #os.makedirs(collector_folder)
        print('created '+collector_folder)
    except:
        print('could not create '+collector_folder)
        pass

    used_scenario['recover_lists'] = get_ids_for_recovery(currentWorld, rec_by, input_parameter_dict['number'],
                                                            save_folder=collector_folder,
                                                            time_steps=used_scenario['max_time'],
                                                            infectivity=used_scenario['infectivity'],
                                                            mu=mu,
                                                            save_df_inf=True,
                                                            folder=output_folder,
                                                            world_name=world_name,
                                                            initial_infectees=[1, 2, 3, 4])

    for p in used_scenario['p_range']:

        if used_scenario['parameter'] == 'recover_frac':
            used_scenario['recover_fraction'] = p

        if used_scenario['parameter'] == 'initial_infections':
            infectees_list = [i+1 for i in range(int(p))]
        elif used_scenario['parameter'] == 'random_initial_infections':
            infectees_list = np.random.choice([agent.ID for agent in currentWorld.people], size=p*len(currentWorld.people))

        else:
            used_scenario[ used_scenario['parameter'] ] = p
            # if used_scenario['parameter'] == 'recover_frac':
            #     recover_world(currentWorld, p, recover_list,
            #                   time_steps=used_scenario['max_time'],
            #                   infectivity=used_scenario['infectivity'],
            #                   mu=mu,
            #                   save_df_inf=True,
            #                   folder=output_folder,
            #                   world_name=world_name,
            #                   initial_infectees=[1, 2, 3, 4])
            infectees_list = [i+1 for i in range(4)]

        print(infectees_list)
        used_scenario['infectees'] = infectees_list
        
        #set_interaction_modifier_for_age_range(currentWorld, used_scenario['im_age_range'], keep_average=True,)

        if used_scenario['product'] != 0:
            if parameter == 'mu':
                scenario_and_parameter = world_name + used_scenario['name'] + '_prod_'+str(
                    product)+'_inf_'+str(float(product)/float(p))+'_'+str(parameter)+'_'+'{:.3f}'.format(p)
            else:
                scenario_and_parameter = world_name + used_scenario['name'] + '_prod_'+str(
                    product)+'_inf_'+str(float(product)/float(mu))+'_'+str(parameter)+'_'+'{: .3f}'.format(p)
        elif used_scenario['parameter'] == 'recover_frac':
            scenario_and_parameter = world_name + 'Ifreq_'+str(mu)+'_'+used_scenario['name'] + '_'+str(
                parameter)+'_'+'{:.3f}'.format(p)+'_rec_'+str(used_scenario['recover_by'])
        else:
            scenario_and_parameter = world_name + 'Ifreq_' + \
                str(mu)+'_'+used_scenario['name'] + '_'+ str(parameter)+'_'+'{:.3f}'.format(p)
        if used_scenario['mix']:
            scenario_and_parameter = 'mix_'+ scenario_and_parameter

        output_folder_plots = collector_folder + scenario_and_parameter + '_ri_' + \
            str(used_scenario['reinfections']) + '_rx_' + \
            str(len(used_scenario['reinfection_times'])) + '/'

        used_scenarios = generate_scenario_list(used_scenario, input_parameter_dict['number'])
        # scenario_and_parameter = 'IAR_' \
        #     + str(used_scenario['im_age_range'][0]) + '_' \
        #     + str(used_scenario['im_age_range'][1]+1) + '_' \
        #     + str(used_scenario['im_age_range'][2]-1) + '_' \
        #     + scenario_and_parameter  
        for sc in used_scenarios:
            sc['world'] = currentWorld

        try:
            os.mkdir(output_folder_plots)
            os.mkdir(output_folder_plots+'/plots')
        except:
            pass

        # try:
        #    os.mkdir(output_folder + scenario_and_parameter +'/')
        #    print(output_folder + scenario_and_parameter +'/'+' created')
        # except:
        #    pass

        #infectees_list = [131,132,133,134]
        #infect_world(currentWorld, IDs = infectees_list)

        start = timeit.default_timer()

        # parallel starts here
        with Pool(input_parameter_dict['cores']) as pool:
            df_dict_list = pool.map(simulate_scenario, used_scenarios)
        print(df_dict_list[0].keys())

        #timecourse_list = [df['timecourse'] for df in df_dict_list]
        status_trajectories_list = [df['stat_trajectories'] for df in df_dict_list]
        simulation_trajectory_list = [df['durations'] for df in df_dict_list]
        flag_trajectories_list = [df['flag_trajectories'] for df in df_dict_list]
        infections_per_location_type_list = [df['infections_per_location_type'] for df in df_dict_list]
        infections_per_schedule_type_list = [df['infections_per_schedule_type'] for df in df_dict_list]
        number_of_infected_households_list = [df['number_of_infected_households'] for df in df_dict_list]
        infection_timecourse_list = [df['infection_timecourse'] for df in df_dict_list]
        infection_patterns_list = [df['infection_patterns'] for df in df_dict_list]
        #encounters_number_list = [dfs['contact_distribution_per_week'][0] for dfs in df_dict_list]
        #contacts_list = [dfs['contact_distribution_per_week'][1] for dfs in df_dict_list]
        #r_eff_list = [df['r_eff'] for df in df_dict_list]
        infectivities_at_2_list = [df['infectivities_at_2'] for df in df_dict_list]
        infectivities_at_3_list = [df['infectivities_at_3'] for df in df_dict_list]
        transition_times = [df['transition_times'] for df in df_dict_list]
        recovered_lists = [df['recovered_list'] for  df in df_dict_list]

        kwargs_plot = {'filename': scenario_and_parameter, 'output_folder': output_folder_plots}

        #save_timecourse(timecourse_list, **kwargs_plot)
        plot_and_save_statii(status_trajectories_list, **kwargs_plot)
        plot_and_save_durations(simulation_trajectory_list, **kwargs_plot)
        plot_flags(flag_trajectories_list, cummulative=False, **kwargs_plot)
        plot_flags(flag_trajectories_list, cummulative=True,
                   filename=scenario_and_parameter+'_cumulativ', output_folder=output_folder_plots)
        plot_and_save_infection_per_location(infections_per_location_type_list, **kwargs_plot)
        plot_and_save_infections_per_location_type_delta(infections_per_location_type_list,
                                                         used_scenario['modeledWorld'],
                                                         locs_to_hide=['morgue'],
                                                         relative=False,
                                                         label_offset=0.03,
                                                         title='Infections per location type',
                                                         **kwargs_plot)
        plot_and_save_infections_per_schedule_type_delta(infections_per_schedule_type_list,
                                                         used_scenario['modeledWorld'],
                                                         save_figure=True,
                                                         fraction_most_infectious=1.,
                                                         sched_to_hide=[],
                                                         title='Infections per schedule type',
                                                         label_offset=0.03,
                                                         relative=False, **kwargs_plot)
        plot_and_save_patterns(infection_patterns_list, pattern='infections',
                               filename=scenario_and_parameter, output_folder=output_folder_plots)
        # plot_infection_per_schedule_type(infection_timecourse_list,
        #                                 used_scenario['modeledWorld'],
        #                                 **kwargs_plot)
        #plot_and_save_r_eff(r_eff_list, save_figure=True, **kwargs_plot)
        #plot_and_save_encounters(encounters_number_list,  save_figure=True, **kwargs_plot)
        #plot_and_save_contacts(contacts_list, used_scenario['modeledWorld'],  save_figure=True, **kwargs_plot)
        

        save_number_of_infected_households(number_of_infected_households_list, **kwargs_plot)
        save_infection_timecourse(infection_timecourse_list, **kwargs_plot)

        save_infectivities(infectivities_at_2_list,'_2_', **kwargs_plot)
        save_infectivities(infectivities_at_3_list,'_3_', **kwargs_plot)

        save_transition_times(transition_times, **kwargs_plot)
        save_recovered_lists(recovered_lists, **kwargs_plot)

        if 'contact_tracing' in df_dict_list[0].keys():
            contact_tracing = [df['contact_tracing'] for df in df_dict_list]
            plot_and_save_contact_tracing(
                contact_tracing, **kwargs_plot)
        if 'interaction_patterns' in df_dict_list[0].keys():
            interaction_patterns_list = [df['interaction_patterns'] for df in df_dict_list]
            plot_and_save_patterns(interaction_patterns_list, pattern='interactions',
                                   **kwargs_plot)

        stop = timeit.default_timer()

        with open(output_folder_plots + 'sim_parameters.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for key in used_scenario:
                writer.writerow([key, used_scenario[key]])

        agent_infos = currentWorld.get_agent_info()
        agent_infos.to_csv(output_folder_plots +
                           scenario_and_parameter +'_agent_infos.csv')
        location_infos = currentWorld.get_location_info()
        location_infos.to_csv(output_folder_plots + scenario_and_parameter + '_location_infos.csv')

        #del(currentWorld)

    print(df_dict_list)
    print('time:  ', stop-start)
