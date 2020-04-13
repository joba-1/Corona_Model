import unittest
from virusPropagationModel import ModeledPopulatedWorld,Simulation
import matplotlib.pyplot as plt
import glob
import os

class TestvPM(unittest.TestCase):

    def setUp(self):
        self.modeledWorld1 = ModeledPopulatedWorld(40, 800, 50)
        self.modeledWorld2 = ModeledPopulatedWorld(100, 400, 5)
        self.simulation1 = Simulation(self.modeledWorld1, 100)
        self.simulation2 = Simulation(self.modeledWorld2, 10)

    def test_ModeledPopulatedWorld_initialization(self):
        self.assertEqual(40, self.modeledWorld1.number_of_locs, "not all given amount of locations was initialized."
                                                                " # initialized: " +
                                                                str(self.modeledWorld1.number_of_locs))

        self.assertEqual(100, self.modeledWorld2.number_of_locs, "not all given amount of locations was initialized."
                                                                 " # initialized: " +
                                                                 str(self.modeledWorld2.number_of_locs))
        self.assertEqual(800, self.modeledWorld1.number_of_people, "not all given amount of people was initialized."
                                                                   " # initialized: " +
                                                                   str(self.modeledWorld1.number_of_people))
        self.assertEqual(400, self.modeledWorld2.number_of_people, "not all given amount of people was initialized."
                                                                   "# initialized: " +
                                                                   str(self.modeledWorld2.number_of_people))
    def test_simulation_class_methods_no_errors(self):
        self.simulation1.plot_status_timecourse()
        self.simulation1.plot_flags_timecourse()
        self.simulation1.plot_location_type_occupancy_timecourse()

    def test_export_simulation_csvs(self):
        self.simulation1.export_time_courses_as_csvs(identifier='testing')
        for file in glob.glob("outputs/testing*"): # files cleanup
            os.remove(file)

if __name__ == '__main__':
    unittest.main()
