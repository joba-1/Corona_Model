import unittest
from virusPropagationModel import ModeledPopulatedWorld, Simulation
import matplotlib.pyplot as plt
import glob
import os


class TestVPM(unittest.TestCase):

    def setUp(self):  # runs automatically before each one of the tests
        self.modeledWorld1 = ModeledPopulatedWorld(1000, 300)
        self.modeledWorld2 = ModeledPopulatedWorld(500, 50)
        self.simulation1 = Simulation(self.modeledWorld1, 100)

    def test_ModeledPopulatedWorld_initialization(self):
        self.assertEqual(1000, self.modeledWorld1.number_of_locs, "not all given amount of locations was initialized."
                                                                " # initialized: " +
                         str(self.modeledWorld1.number_of_locs))

        self.assertEqual(500, self.modeledWorld2.number_of_locs, "not all given amount of locations was initialized."
                                                                 " # initialized: " +
                         str(self.modeledWorld2.number_of_locs))

    def test_multiple_sims(self):
        self.simulation2 = Simulation(self.modeledWorld1, 100)
        self.simulation3 = Simulation(self.modeledWorld1, 50)
        self.simulation4 = Simulation(self.modeledWorld2, 10)

    def test_simulation_plotting_no_errors(self):
        self.simulation1.plot_status_timecourse()
        self.simulation1.plot_flags_timecourse()
        self.simulation1.plot_location_type_occupancy_timecourse()
        self.simulation1.plot_distributions_of_durations()

    def test_export_simulation_csvs(self):
        self.simulation1.export_time_courses_as_csvs(identifier='testing')
        self.assertTrue(len(glob.glob("outputs/testing*")) != 0, "No CSVs exported!")
        for file in glob.glob("outputs/testing*"):
            self.assertTrue(os.path.exists(file) and os.path.getsize(file) > 0, "CSV is empty!")
            os.remove(file)  # files cleanup

    def test_infection_mechanism(self):
        self.testWorld_1 = self.modeledWorld1
        self.testWorld_2 = ModeledPopulatedWorld(1000, 200, agent_agent_infection=True)
        self.simulation_a_a_inf = Simulation(self.testWorld_2, 100)
        self.simulation_a_a_inf.plot_status_timecourse()
        self.simulation_a_a_inf.plot_flags_timecourse()
        self.simulation_a_a_inf.plot_location_type_occupancy_timecourse()


if __name__ == '__main__':
    unittest.main()
