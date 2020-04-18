import unittest
from virusPropagationModel import ModeledPopulatedWorld, Simulation
import matplotlib.pyplot as plt
import glob
import os


class TestVPM(unittest.TestCase):

    def setUp(self):  # runs automatically before each one of the tests
        self.modeledWorld1 = ModeledPopulatedWorld(1000, 300)
        self.simulation1 = Simulation(self.modeledWorld1, 100)

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

    def test_multiple_subsequent_sims_and_plot(self):
        self.sim_1_1 = Simulation(self.simulation1, 50)
        self.sim_1_2 = Simulation(self.sim_1_1, 50)
        self.sim_1_2.plot_status_timecourse()
        self.sim_1_2.plot_flags_timecourse()
        self.sim_1_2.plot_location_type_occupancy_timecourse()
        self.sim_1_2.plot_distributions_of_durations()

    def test_export_simulation_csvs(self):
        self.simulation1.export_time_courses_as_csvs(identifier='testing')
        self.assertTrue(len(glob.glob("outputs/testing*")) != 0, "No CSVs exported!")
        for file in glob.glob("outputs/testing*"):
            self.assertTrue(os.path.exists(file) and os.path.getsize(file) > 0, "CSV is empty!")
            os.remove(file)  # files cleanup

    def test_infection_mechanism(self):
        self.testWorld_2 = ModeledPopulatedWorld(1000, 200, agent_agent_infection=True)
        self.simulation_a_a_inf = Simulation(self.testWorld_2, 100)
        self.simulation_a_a_inf.plot_status_timecourse()
        self.simulation_a_a_inf.plot_flags_timecourse()
        self.simulation_a_a_inf.plot_location_type_occupancy_timecourse()

    def test_infection_network(self):
        self.testWorld_1 = ModeledPopulatedWorld(1000, 200, agent_agent_infection=False)
        self.testWorld_2 = ModeledPopulatedWorld(1000, 200, agent_agent_infection=True)
        self.sim1 = Simulation(self.testWorld_1, 100)
        self.sim2 = Simulation(self.testWorld_2, 100)
        self.notAA_infectionNW = self.sim1.get_infection_event_information()
        self.AA_infectionNW = self.sim2.get_infection_event_information()
        ## Testing whether the location-based infection-mechanism records finite infected_by_attributes##
        ## This should not be the case ##
        no_associated_infector_in_locationbased_infectionmechanism = True
        if list(set(list(self.notAA_infectionNW['got_infected_by']))) != 1:
            no_associated_infector_in_locationbased_infectionmechanism = False
        else:
            if list(set(list(self.notAA_infectionNW['got_infected_by'])))[0] != 'nan':
                no_associated_infector_in_locationbased_infectionmechanism = False
        self.assertTrue(no_associated_infector_in_locationbased_infectionmechanism,
                        "Finite got_infected_by-attributes in location-based infection-mechanism")


if __name__ == '__main__':
    unittest.main()
