import unittest
from virusPropagationModel import ModeledPopulatedWorld, Simulation
import matplotlib.pyplot as plt
import glob
import os


class TestVPM(unittest.TestCase):

    def setUp(self):  # runs automatically before each one of the tests
        self.modeledWorld1 = ModeledPopulatedWorld(1000, 200)
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

    def test_export_simulation_csvs(self):
        self.simulation1.export_time_courses_as_csvs(identifier='testing')
        print()
        self.assertTrue(len(glob.glob("outputs/testing*")) != 0, "No CSVs exported!")
        for file in glob.glob("outputs/testing*"):
            self.assertTrue(os.path.exists(file) and os.path.getsize(file) > 0, "CSV is empty!")
            os.remove(file)  # files cleanup

    def test_infection_mechanism(self):
        testWorld_1 = self.modeledWorld1
        testWorld_2 = ModeledPopulatedWorld(700, 150, agent_agent_infection=False)
        testWorld_3 = ModeledPopulatedWorld(1200, 150, agent_agent_infection=True)
        test_simulation1 = Simulation(testWorld_1, 50)
        test_simulation2 = Simulation(testWorld_2, 50)
        test_simulation3 = Simulation(testWorld_3, 50)


if __name__ == '__main__':
    unittest.main()
