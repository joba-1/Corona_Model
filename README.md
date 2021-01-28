# GEospacially Referenced Demographic Agent-based (*GERDA*)
## A model for virus (SARS-CoV-2) transmission and disease (COVID-19) progression
(c) Theretical Biophysics, Humboldt-Universität zu Berlin

## General Information
The information regarding the data used in this model as well as its documentation and developer information can be found in this repository's [wiki](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/wikis/home).

This model is maintained by the [Klipp lab for theoretical biophysics](https://rumo.biologie.hu-berlin.de/tbp/index.php/en/) at the Humboldt Universität zu Berlin. For questions and feedback, please contact us [:email:](mailto:bjoern.goldenbogen.1@biologie.hu-berlin.de)

The code in this repository was implemented and tested using python 3.7 on linux and mac operating systems. If you do not have Python installed, please checkout [Python webpage](https://www.python.org/downloads/) for installation information.

## Setup
For code checkout, you need gitlab. To download the repository information onto your local machine, navigate to the directory of your choice and clone this repository to your local machine if you have not done so yet (using terminal/command line):

    git clone https://ford.biologie.hu-berlin.de/jwodke/corona_model.git

There exist two options to setup GERDA. We recommend installing Gerda in a [Conda environment](#installing-in-conda-environment-recommended). Alternatively, you can only apply [Quick install](#quick-install).

### Installing in Conda environment (recommended)
If you do not have Conda installed, go to [Conda webpage](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).\
To make sure you have the latest version, run:

    conda update conda

Note: If you don't want to permanently activate the conda base environment, run following command (after opening a new shell/relogin):

    conda config --set auto_activate_base false

However, this is not required and it has no effect to the ability to work with conda (the "conda" command is available), just not started by default.

Then run the following commands in your local GERDA directory (you can replace 'gerdaenv' by your name of choice):    
    
    conda create -n gerdaenv python=3.8
    
    conda activate gerdaenv

Now, please proceed as described in [Quick install](#quick-install)

### Quick install
If you are not already there, please navigate to your GERDA repository directory on your local machine, e.g. ``` mypath/GERDA/```. To assure the correct package dependencies (required!), please install the gerda package via pip:
    
    pip install -e .

Note: If you did not install in a Conda environment, you require adjusted commands (full paths) to run the scripts (compare section [Executable scripts](#executable-scripts)).

<!--- 
### Testing the successful cloning of the repository and the setup of environment and installation of the gerda package
In case you want to test if the environment setup worked correctly, you can run our test suite and see if you get any errors with the following command
    
    python3 -m testing.testrunner
    
Note: this could take a few minutes and might result in figures popping up, which have to be closed manually after inspection.\
Also, make sure to activate the 'gerdaenv' environment again if it is no longer activated before moving on.
--->
# Usage
GERDA is a stochastic modeling approach, thus relevant conclusions can only be drawn from repeated simulation of the same scenario.

To check out the model functionalities and to simulate virus propagation throughout defined communities, please refer to the following subsections [Demo jupyter notebooks](#demo-jupyter-notebooks) and [Executable scripts](#executable-scripts) below).\
For parallel computing on high end memory servers, we provide a directly executable script ```sim_parallel.py``` in directory './scripts/' ([compare below](#sim_parallelpy)).

For advanced simulations please refer to our repository's [wiki](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/wikis/home).

## Demo jupyter notebooks
For testing different features of gerda models in single runs, i.e. running one simulation on a personal desktop computer but not running each simulation 100 times in parallel on a high end memory server, we provide different interactive jupyter notebooks (ipynb-files).\
To use a jupyter notebook, start the jupyter notebook application (e.g. in the terminal with the activated gerdaenv type ```jupyter notebook``` or ```jupyter-notebook```), navigate to the corona_model directory and select the desired notebook (ipynb-file). To run the full simulation, click on "Cell --> Run All" or run cells individually.

### [Demo.ipynb](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/blob/master/Demo.ipynb)
This notebook contains the commands required to initialize a modeled world (using a small version (10%) of Gangelt -> modeledWorld_small) and to run GERDA simulations, including possibilities for manual adjustment of parameters 'time_steps' and 'general_infectivity'.

This notebook contains the following code blocks:
1. importing required libraries and initializing a dictionary for the real world communities that can be used)
2. "Initiate world" - initialize small or large world for Gangelt (small = 10% of population and buildings, large = 100% of population and buildings)
3. "Info on world" - plot of age distribution + information on infected agents
4. "Sample simulation" - the first cell of this code block runs the baseline scenario for Gangelt (by default using small Gangelt); furthermore 'time_steps' and 'general_infectivity' can be adjusted by the user. The subsequent cells provide example result plots (health (sub)states over time, heat maps for interaction and infection patterns; overrepresentation and underrepresentation of schedule types or location types, respectively, for infection transmissions)

### [Demo_Vaccination.ipynb](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/blob/master/Demo_Vaccination.ipynb)
In order to demonstrate the simulations, which were performed to evaluate the different vaccination-strategies in our manuscript, we generated a jupyter notebook. We suggest to first get familiar with the Demo.ipynb (compare above), in order to get an intuition for our model and its basic application and characteristics.

This notebook contains the following code blocks:
1. importing required libraries and initializing a dictionary for the real world communities that can be used: "Initiate world" - initialize small or large world for Gangelt (small = 10% of population and buildings, large = 100% of population and buildings)
2. Running an initial infection-wave to be used in defining one of the tested strategies
	—> Be aware that here exists a checkpoint for the user 
3. Derivation of ordered list of agents, to be vaccinated, according to different vaccination-strategies
4. Running simulations with different vaccination-fractions of the population, for the different strategies
5. Generating a plot, resembling figure 3 in our manuscript

Please be aware, that we set the default world to be used to the small version, in order to avoid excessive runtimes for this demonstration. 
Since this world is not fully representative to the large world, we used for the manuscript; the infection-dynamics differ and thus the results of the vaccintion-screens do too.
Furthermore we have set the vaccination-fraction increments to 20% (where we used 5%-steps in the manuscript), also to reduce runtime.

The (default) reduced version of the vaccination screens has a runtime of around 1-2 hours, but there exists the possibility to use the non-reduced version (as we did in the manuscript); however be aware, that we expect a runtime of 1-2 days for this.

<!---
### [Demo_new_strain.ipynb](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/blob/master/Demo_new_strain.ipynb)
This notebook allows to consider not only the propagation of the original SARS-CoV-2 virus but also of the recently found (end of 2020) mutated variant originating from Great Britain. We suggest to first get familiar with the Demo.ipynb (compare above), in order to get an intuition for our model and its basic application and characteristics.

 DESCRIPTION OF NOTEBOOK STILL REQUIRED.

--->
## Executable scripts
The reporsitory provides the following directly executable scripts in direction './scripts/'. Help functionality (--help or -h) is enabled for all of those scripts.\
If installed in [Conda](#installing-in-conda-environment-recommended) environment, those scripts can be directly executed from the main directory (e.g. ```generate_worlds.py -h```), in case of the [Quick install](#quick-install), the path starting from the repository main directory is required (e.g. ```scripts/generate_worlds.py -h```).

### read_geodata.py
This script creates the georeferenced input data files (.geojson, .csv files) required to rebuild a georeferenced gerda world with ```generate_worlds.py```. Geodata files are stored in ```./input_data/geo``` by default.

### generate_worlds.py
This script generates gerda worlds, required for repeated simulation of virus propagation throughout a defined community with the same initial conditions (seed), i.e. for getting meaningful conclusions from stochastic simulations. Generated world files are stored in ```./models/worlds/``` by default.

### sim_parallel.py
This script runs several parallel simulations (using the same world and the same input parameters) on a multi-core computer. This allows to account for the inherent stochasticity of gerda models and provides a more reliable simulation output than a single run.
Note: Simulations are memory expensive. We use AMD-based servers with 96 cores and 512 GB RAM for most simulations. As the bottleneck is the RAM, for larger/longer simulations (e.g. >10000 agents for >=2000 time steps) we can use just 24 cores.

# Technical details
## Expected run time
Simulating Gangelt (100% of population and buildings, [input file](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/blob/Cleaned_up_development/input_data/geo/Buildings_Gangelt_MA_1.csv) takes about 30 minutes on a personal desktop computer (core I7, 16GB RAM) for one simulation run. For Demo purpose, we recommend to simulate the reduced Gangelt (10% of population and buildings, [input file](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/blob/Cleaned_up_development/input_data/geo/Buildings_Gangelt_MA_3.csv)), which takes about 10 minutes on a personal desktop computer.

## Integration of external data
Transition probabilities and time-dependent infectiousness:\
Hourly transition probabilities between agent states and hourly infection-emission rates are defined in distinct csv-files. The file [```simulation_configuration.csv```](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/blob/Cleaned_up_development/input_data/simulation_configuration.csv) defines the path to the source-file for each transition, the dependency on the duration in specific states and whether the transition rates are to be considered age-specific.

<!---
Location factors:\
File with relative infectivities for different location-types (Currently default-factor 1 for all location-types).

CHECK BACK IF THIS REFERS TO ./input_data/coefficients/location_coefficients.csv
--->
Geodata:\
Files with geo-information for each modelled world which are required to initiate the respective world are found as csv-files in the directory ```./input_data/geo/```.

Schedule Definition:\
The schedules which define agent-routines are provided as csv-files in the directory ```./input_data/schedules/```.
