import unittest
from virusPropagationModel import ModeledPopulatedWorld,Simulation
import matplotlib.pyplot as plt


class MyTestCase(unittest.TestCase):
    def test_ModeledPopulatedWorld_initialization(self):
        modeledWorld1 = ModeledPopulatedWorld(100, 400, 5)
        self.assertEqual(100, modeledWorld1.number_of_locs, "not all given amount of locations was initialized. # "
                                                               "initialized: " + str(modeledWorld1.number_of_locs))
        self.assertEqual(400, modeledWorld1.number_of_people, "not all given amount of people was initialized. # "
                                                               "initialized: " + str(modeledWorld1.number_of_people))

    def test_ModeledPopulatedWorld_functions_no_errors(self):
        modeledWorld1 = ModeledPopulatedWorld(100, 400, 5)
        simulation1 = Simulation(modeledWorld1, 100)
        simulation1.plot_status_timecourse()
        simulation1.plot_flags_timecourse()
        simulation1.plot_location_type_occupancy_timecourse()

if __name__ == '__main__':
    unittest.main()
