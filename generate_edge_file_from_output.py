import pandas as pd 
import argparse
import sys

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-if", "--inputfile", type=str, help="Input File (default datafiles/sim.csv)")
    parser.add_argument("-of", "--outputfile", type=str, help="Input File (default edges.csv)")
    #parser.add_argument("-n", "--number", type=int, help="A number.")
    #parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode.")
    options = parser.parse_args(args)
    return options


options = getOptions(sys.argv[1:])

if options.outputfile:
	#try:
	o_f = options.outputfile
	#except:	
else:
	o_f  = 'edges.csv'


if options.outputfile:
	#try:
	i_f = options.inputfile
	#except:	
else:
	i_f  = 'sim.csv'


df =pd.read_csv(i_f)

times = df['time'].unique()
locations = df['loc'].unique()
edges=[]

for t in times:
    for location in locations:   
        loc_at_time=df[(df['time']==t)&(df['loc']==location)]
        humans_in_loc = list(loc_at_time['h_ID'].values)
        df[(df['time']==t)&(df['loc']==200)]
        h_l = humans_in_loc.copy()
        for human in humans_in_loc:
            h_l.remove(human)
            status = loc_at_time[loc_at_time['h_ID']==human]['status'].values[0]
            for human_out in h_l:
                edge={'persID_A': human, 'persID_O': human_out, 'Edge':'pp', 'status_von_A': status, 'time': t}
                edges.append(edge)

try:
	df_out = pd.DataFrame('datafiles/'+o_f)
	print('datafiles/edges.csv saved')
except:
	print('could not save')










