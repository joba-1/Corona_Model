from virusPropagationModel import *
import glob
import os

modeledWorld = load_simulation_object('gangelt_full_schedules_v1_worldObj_22-04-2020_20-50-52')

def simulate_scenario(max_time, start_2, start_3, closed_locs, infectivity, name='scenario_output/default'):   # times: 3 durations for simulations; closed_locs: list of forbidden locations

    simulation1 = Simulation(modeledWorld, start_2, run_immediately=False)
    simulation1.change_agent_attributes({'all':{'behaviour_as_infected':{'value':infectivity,'type':'replacement'}}})
    simulation1.simulate()

    simulation2 = Simulation(simulation1, start_3-start_2, run_immediately=False)
    for p in simulation2.people:
        for loc in closed_locs:
            p.stay_home_instead_of_going_to(loc)
    simulation2.simulate()

    simulation3 = Simulation(simulation2, max_time-start_3, run_immediately=False)
    for p in simulation3.people:
        p.reset_schedule()
    simulation3.simulate()

    simulation3.save(name)

scenarios = [[max_time, start_2, start_3, closed_locs, infectivity, '']
            [max_time, start_2, start_3, closed_locs, infectivity, name],
            [max_time, start_2, start_3, closed_locs, infectivity, name],
            [max_time, start_2, start_3, closed_locs, infectivity, name],
            [max_time, start_2, start_3, closed_locs, infectivity, name]]