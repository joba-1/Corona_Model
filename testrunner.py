import unittest
import glob
import os
import gerda.utilities.VPM_save_and_load as vpm_save_load

from gerda.core.virusPropagationModel import *

class TestVPM(unittest.TestCase):

    def setUp(self):  # runs automatically before each one of the tests
        self.modeledWorld1 = ModeledPopulatedWorld(1000, 10,
                                                   world_from_file=True, geofile_name='input_data/geo/Buildings_Gangelt_MA_3.csv',
                                                   agent_agent_infection=True)
        self.simulation1 = Simulation(self.modeledWorld1, 100)

    def test_modeled_pop_world_plotting(self):
        self.modeledWorld1.plot_distribution_of_location_types()
        self.modeledWorld1.plot_initial_distribution_of_ages_and_infected()

    def test_ModeledPopulatedWorld_initialization(self):
        self.assertEqual(1000, self.modeledWorld1.number_of_locs, "not all given amount of locations was initialized."
                         " # initialized: " +
                         str(self.modeledWorld1.number_of_locs))

    def test_multiple_sims_and_worlds_parallel(self):
        self.modeledWorld2 = ModeledPopulatedWorld(500, 50)
        self.simulation2 = Simulation(self.modeledWorld1, 100)
        self.simulation3 = Simulation(self.modeledWorld1, 50)
        self.simulation4 = Simulation(self.modeledWorld2, 10)

    def test_simulation_plotting_no_errors(self):
        self.simulation1.plot_status_timecourse()
        self.simulation1.plot_flags_timecourse()
        self.simulation1.plot_location_type_occupancy_timecourse()
        self.simulation1.plot_distributions_of_durations()
        self.simulation1.plot_status_at_location()
        self.simulation1.map_status_at_loc()
        self.simulation1.plot_age_groups_status_timecourse()

    def test_multiple_subsequent_sims_and_plot(self):
        self.sim_1_1 = Simulation(self.simulation1, 50)
        self.sim_1_2 = Simulation(self.sim_1_1, 50)
        self.sim_1_2.plot_status_timecourse()
        self.sim_1_2.plot_flags_timecourse()
        self.sim_1_2.plot_location_type_occupancy_timecourse()
        self.sim_1_2.plot_distributions_of_durations()

    def test_export_simulation_csvs(self):
        self.simulation1.export_time_courses_as_csvs(identifier='testing')
        self.assertTrue(len(glob.glob("output/simulation_results/testing*"))
                        != 0, "No CSVs exported!")
        for file in glob.glob("output/simulation_results/testing*"):
            self.assertTrue(os.path.exists(file) and os.path.getsize(
                file) > 0, "CSV is saved_simulation_objects_go_here!")
            os.remove(file)  # files cleanup

    def test_import_export_objects(self):
        self.modeledWorld1.save('testingsavemw', date_suffix=False)
        self.loaded_mod_world1 = vpm_save_load.load_world_object(
            'testingsavemw')
        self.sim1_from_loaded_world1 = Simulation(self.loaded_mod_world1, 100)
        self.sim1_from_loaded_world1.save('testingsavesim', date_suffix=False)
        self.loaded_sim1 = load_simulation_object('testingsavesim')
        self.simulation1.plot_status_timecourse()
        self.sim1_from_loaded_world1.plot_status_timecourse()
        self.loaded_sim1.plot_status_timecourse()
        for file in glob.glob("saved_objects/testing*"):
            os.remove(file)  # files cleanup

    def test_infection_mechanism(self):
        self.testWorld_2 = ModeledPopulatedWorld(1000, 200, agent_agent_infection=True)
        self.simulation_a_a_inf = Simulation(self.testWorld_2, 100)
        self.simulation_a_a_inf.plot_status_timecourse()
        self.simulation_a_a_inf.plot_flags_timecourse()
        self.simulation_a_a_inf.plot_location_type_occupancy_timecourse()

    def test_r_eff_get_from_obj_and_plot(self):
        self.simulation2 = Simulation(self.modeledWorld1, 500)
        self.simulation2.plot_r_eff(4*24)
        # self.simulation2.export_r_eff_time_course_as_csv(2*24,saved_csv_identifier='testing_stepsize1')
        #self.simulation2.export_r_eff_time_course_as_csv(4*24, saved_csv_identifier='testing_stepsize2')
        # vpm_neta.plot_r_eff_from_csvs_or_sim_object(['testing_stepsize1','testing_stepsize2'])
        for file in glob.glob("output/plots/testing*"):
            os.remove(file)  # files cleanup


if __name__ == '__main__':
    unittest.main()
