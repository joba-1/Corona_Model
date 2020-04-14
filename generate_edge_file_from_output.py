#############################################################################################
## This file takes an input file that is a simulation output from a virusPropagationModel  ##
## and sums up the number of occurences for each unique connection between two people.     ##
## Input arguments:                                                                        ##
## - input file (optional, by default set to sim.csv)                                      ##
## - output file (optional, by default set to edges.csv)                                   ##
## Output:                                                                                 ##
## - input file for cytoscape (defining unique connections between people) and their count ##
## For teh moment this is limited to 24 hours, since daily schedules for people do not     ##
## change.                                                                                 ##
## (c) Björn Goldenbogen, Judith Wodke                                                     ##
#############################################################################################

## import libraries
import pandas as pd 
import argparse
import sys

## GetOptions parses the given input arguments and gives back a list of options
def GetOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-if", "--inputfile", type=str, help="Input File (default datafiles/sim.csv)")
    parser.add_argument("-of", "--outputfile", type=str, help="Input File (default edges.csv)")
    #parser.add_argument("-n", "--number", type=int, help="A number.")
    #parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode.")
    options = parser.parse_args(args)
    return options

## run function getOptions
options = GetOptions(sys.argv[1:])

## define input and output files
if options.inputfile:
    i_f = options.inputfile
else:
    i_f  = 'sim.csv'

if options.outputfile:
	o_f = options.outputfile
else:
	o_f  = 'edges.csv'

## read in the input file
df =pd.read_csv(i_f)

## extract list of timepoints
times = df['time'].unique()
times = times[:24] ## limit time points to first 24 (NOTE: think about if we want this per day simulated at a certain point in time)
## extract list of locations
locations = df['loc'].unique()
## initialize dicts and lists
counted_connections = {}
status_at_final_time = {}
edges=[]

## iterate over times and locations to identify connections between pairs of people and count them
for t in times:
    for location in locations:
        loc_at_time=df[(df['time']==t)&(df['loc']==location)] ## extract location at time
        humans_in_loc = list(sorted(loc_at_time['h_ID'].values)) ## extract sorted list of humans in location
        df[(df['time']==t)&(df['loc']==length(times))] ## what do we do this for???
        h_l = humans_in_loc[:] ## get real copy of humans in loc list
        for human in humans_in_loc:
            h_l.remove(human) ## remove human from humnas in loc list copy to only count pairs once
            status_at_final_time[human] = loc_at_time[loc_at_time['h_ID']==human]['status'].values[0] ## extract the status of human at time t
            ## get all people connected to human in loc at t
            for human_out in h_l:
                status_at_final_time[human_out] = loc_at_time[loc_at_time['h_ID']==human_out]['status'].values[0]
                if (human, human_out) in counted_connections.keys():
                    counted_connections[(human, human_out)] += 1 ## if pair is already counted at least once, increase
                else:
                    counted_connections[(human, human_out)] = 1 ## otherwise set to 1

## for each unique pair define the connection (edge in cytoscape)
for pair in counted_connections.keys():
    persA = pair[0] ## entry node
    persB = pair[1] ## exit node
    statusA = status_at_final_time[persA] ## status at t=final of entry node
    statusB = status_at_final_time[persB] ## status at t=final of exit node
    edge={'persID_A': persA, 'persID_B': persB, 'Edge_type':'pp', 'status_persA': statusA, 'status_persB': statusB,
          'time': t, 'number_connections': counted_connections[pair]} ## define edge
    edges.append(edge) ## append edge to edges list

## print cytoscape input file
try:
    df_out = pd.DataFrame(edges)
    df_out.to_csv('datafiles/'+o_f, sep='\t', na_rep='', header=True, index=True, mode='w', quotechar='"', decimal='.')
    print('datafiles/' + o_f + ' saved')
except:
    print('could not save')
