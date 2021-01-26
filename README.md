# TBP HU-Berlin SARS-CoV-2 infection transmission ABM

## General Information
The information regarding the data used in this model as well as its documentation and developer information can be found in this repository's [wiki](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/wikis/home).

This model is maintained by the [Klipp lab for theoretical biophysics](https://rumo.biologie.hu-berlin.de/tbp/index.php/en/) at the Humboldt Universität zu Berlin.

Terminal commands are shown in separate boxes.

## Setup
The code in this repository was implemented using python 3.7.\
Only this version or newer versions of python are supported. However, if you run an older python version, the GERDA code might still work.\
For code checkout, you need git.
We are developing on linux and on mac, currently we are working on windows compatibility as well.

### Quick setup using conda
Follow these three steps to make use of the virtual environment provided in the repository for a quick and optimal setup.
1. First, clone this repository to your local machine if you have not done so yet.
    ```
    git clone https://ford.biologie.hu-berlin.de/jwodke/corona_model.git
    ```

2. Then, make sure you have Anaconda/Miniconda3 installed by running the following code in your terminal
    ```
    conda --v
    ```
    This should return something like `conda 4.X.X`. If it doesn't, [install the latest Miniconda3](https://docs.conda.io/en/latest/miniconda.html). \
    To make sure you have the latest version, run
    ```
    conda update conda
    ```
    If you don't want to permanently activate the conda base environment,
    run following command (after opening a new shell/relogin):
    ```
    conda config --set auto_activate_base false
    ```
    This has no effect to the work with conda, (the "conda" command is available), but after the login you have the "normal" python environment.

3. Then run the following pieces of code to set up the local environment:
    ```
    cd /path/to/this/repository
    ```
    ```
    conda env create --file gerdaenv.yml
    ```
    ```
    conda activate gerdaenv
    ```

### pip installation of gerda package
To allow running of the different notebooks (compare section 'Usage') and other parts of the GERDA code, please install the gerda package via pip by going to the main folder of your cloned repository and using the following command in the terminal/command line:
```
pip install .
```

### Testing the successful cloning of the repository and the setup of environment and installation of the gerda package
In case you want to test if the environment setup worked correctly, you can run our test suite and see if you get any errors with the following command
```
python3 testrunner.py
```
Note: this could take a few minutes and might result in figures popping up, which have to be closed manually after inspection.

That was it. You can now proceed to the 'Usage' part. Make sure to activate the 'gerdaenv' environment again if it is no longer activated before moving on.

### Usage
## Demo jupyter notebook
For personal demo purposes we provide a jupyter notebook [Demo.ipynb](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/blob/master/Demo.ipynb) for single runs (i.e. running one simulation on a personal desktop computer but not running each simulation 100 times in parallel on a high end memory server). This notebook contains the commands required to initialize a modeled world (using a small version (10%) of Gangelt -> modeledWorld_small) and to run GERDA simulations, including possibilities for manual adjustment of parameters 'time_steps' and 'general_infectivity'. 

This notebook contains the following code blocks:
1. importing required libraries and initializing a dictionary for the real world communities that can be used)\
2. "Initiate world" - initialize small or large world for Gangelt (small = 10% of population and buildings, large = 100% of population and buildings)\
3. "Info on world" - plot of age distribution + information on infected agents\
4. "Sample simulation" - the first cell of this code block runs the baseline scenario for Gangelt (by default using small Gangelt); furthermore 'time_steps' and 'general_infectivity' can be adjusted by the user. The subsequent cells provide example result plots (health (sub)states over time, heat maps for interaction and infection patterns; overrepresentation and underrepresentation of schedule types or location types, respectively, for infection transmissions)

To use it, start jupyter notebook (e.g. in the terminal with the activated gerdaenv type "jupyter notebook"), navigate to the corona_model directory and select "Demo.ipynb". To run the full simulation, click on "Cell --> Run All" or run cells individually.

For parallel computing on high end memory servers, we provide different other scripts, simulate_scenarios*.py (* = wildcard character) in directory './sim_parallel/'. We use AMD-based servers with 96 cores and 512 GB RAM. In general, you need a lot of RAM, depending on your input data files and other settings. As the bottleneck is the RAM, for longer simulations (>10000 agents for >=2000 time steps) we can use just 24 cores.

For advanced simulations please refer to our repository's [wiki](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/wikis/home).

## Demo_Vaccination jupyter notebook
In order to demonstrate the simulations, which were performed to evaluate the different vaccination-strategies in our manuscript, we generated a jupyter notebook. We suggest to get familiar with the Demo notebook first, in order to get an intuition for our model and its basic application and characteristics. 
This notebook contains the following code blocks:
1. importing required libraries and initializing a dictionary for the real world communities that can be used) "Initiate world" - initialize small or large world for Gangelt (small = 10% of population and buildings, large = 100% of population and buildings)
2. Running an initial infection-wave to be used in defining one of the tested strategies
	—> Be aware that here exists a checkpoint for the user 
3. Derivation of ordered list of agents, to be vaccinated, according to different vaccination-strategies.
4. Running simulations with different vaccination-fractions of the population, for the different strategies.
5. Generating a plot, resembling figure 3 in our manuscript.

Please be aware, that we set the default world to be used to the small version, in order to avoid excessive runtimes for this demonstration. 
Since this world is not fully representative to the large world, we used for the manuscript; the infection-dynamics differ and thus the results of the vaccintion-screens do too.
Furthermore we have set the vaccination-fraction increments to 20% (where we used 5%-steps in the manuscript), also to reduce runtime.

The (default) reduced version of the vaccination screens has a runtime of around 1-2 hours, but there exists the possibility to use the non-reduced version (as we did in the manuscript); however be aware, that we expect a runtime of 1-2 days for this.

## Demo_new_strain jupyter notebook


### Technical details
## Expected run time
Simulating large Gangelt (100% of population and buildings) takes about 30 minutes on a personal desktop computer (core I7, 16GB RAM) for one simulation run. For Demo purposes, we recommend the small Gangelt (10% of population and buildings), which takes about 10 minutes on a personal desktop computer.

## Integration of external data
Transition probabilities and time-dependent infectiousness:\
Hourly transition probabilities between agent states and hourly infection-emission rates are defined in distinct csv-files. The file simulation_configuration.csv (located at ./input_data/) defines the path to the source-file for each transition, the dependency on the duration in specific states and whether the transition rates are to be considered age-specific.

Location factors:\
File with relative infectivities for different location-types (Currently default-factor 1 for all location-types).

Geodata:\
Files with geo-information on each world to be modelled to initiate world are found as csv-files in the directory './input_data/geo/'.

Schedule Definition:\
The schedules, which define agent-routines are provided as csv-files in the directory './input_data/schedules/'.

## Disclaimer
Files not mentioned in this README are required but can be ignored by any non-developer. We still have to update our folder structure and apologize for any resulting confusion.
