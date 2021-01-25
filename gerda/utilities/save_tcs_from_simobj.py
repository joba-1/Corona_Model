import os

import matplotlib.pyplot as plt
import pandas as pd
import pickle as pkl

from gerda.core.virusPropagationModel import *


def main():

    input_folder = '/home/basar/corona_simulations_save/saved_objects/scenario_output/RPM02_Gangelt_big_Ifreq_2.0_close_all_reopen_all_IF03_start_3_1500.000/'

    input_list = os.listdir(input_folder)
    input_files = [x for x in input_list if x.endswith('pkl')]

    for file_number in range(len(input_files)):
        h_IDs = []
        inf_times = []
        rec_times = []
        death_times = []
        
        current_file = input_files[file_number]
        current_sim = load_simulation_object(current_file, folder=input_folder)
        
        tc_df = current_sim.simulation_timecourse
        tc_df.drop(columns=['loc','Temporary_Flags','Cumulative_Flags','Infection_event'], inplace=True)
        
        tc_df.to_pickle('analysis_temp/TC_'+current_file)
        
        for p in current_sim.people:
            h_IDs.append(p.ID)
            inf_times.append(p.stati_times['infection_time'])
            rec_times.append(p.stati_times['recover_time'])
            death_times.append(p.stati_times['death_time'])
            
        times_dict = {'infection_time':inf_times, 'recovery_time':rec_times, 'death_time':death_times}
        times_df = pd.DataFrame(times_dict, index=h_IDs)
        
        times_df.to_pickle('analysis_temp/TIMES_'+current_file)


if __name__=='__main__':
    main()
