# TBP HU-Berlin SARS-CoV-2 infection transmission ABM

## General Information
The information regarding the data used in this model as well as its documentation and developer information can be found in this repository's [wiki](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/wikis/home).

This model is maintained by the [Klipp lab for theoretical biophysics](https://rumo.biologie.hu-berlin.de/tbp/index.php/en/) at the Humboldt Universität zu Berlin.

Terminal commands are shown in separate boxes.

## Setup
The code in this repository was implemented using python 3.7.\
Only this version or newer versions of python are supported.\
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

In case you want to test if the environment setup worked correctly, you can run our test suite and see if you get any errors with the following command
```
python3 testrunner.py
```
Note: this could take a few minutes and might result in figures popping up, which have to be closed after inspection.

That was it. You can now proceed to the 'Usage' part. Make sure to activate the 'gerdaenv' environment again if it is no longer activated before moving on.


## Demo jupyter notebook
For personal demo purposes we provide a jupyter notebook [Demo.ipynb](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/blob/master/Demo.ipynb) for single runs (i.e. running one simulation on a personal desktop computer but not running each simulation 100 times in parallel on a high end memory server). This notebook contains the commands required to initialize a modeled world (using a small version (10%) of Gangelt -> modeledWorld_small) and to run GERDA simulations, including possibilities for manual adjustment of parameters 'time_steps' and 'general_infectivity'. 

This notebook contains the following code blocks:
1. importing required libraries and initializing a dictionary for the real world communities that can be used)\
"Initiate world" - initialize small or large world for Gangelt (small = 10% of population and buildings, large = 100% of population and buildings)\
"Info on world" - plot of age distribution + information on infected agents\
"Sample simulation" - the first cell of this code block runs the baseline scenario for Gangelt (by default using small Gangelt); furthermore 'time_steps' and 'general_infectivity' can be adjusted by the user. The subsequent cells provide example result plots (health (sub)states over time, heat maps for interaction and infection patterns; overrepresentation and underrepresentation of schedule types or location types, respectively, for infection transmissions)

To use it, start jupyter notebook (e.g. in the terminal with the activated gerdaenv type "jupyter notebook"), navigate to the corona_model directory and select "Demo.ipynb". To run the full simulation, click on "Cell --> Run All".

For parallel computing on high end memory servers, we provide different other scripts, simulate_scenarios*.py (* = wildcard character). In general, you need a lot of RAM, depending on your input data files and other settings. We use AMD-based servers with 96 cores and 512 GB RAM, but the bottleneck is the RAM. That's why we can use just 24 cores.

For advanced simulations please refer to our repository's [wiki](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/wikis/home).

## Expected run time
Simulating large Gangelt (100% of population and buildings) takes about 30 minutes on a personal desktop computer (core I7, 16GB RAM) for one simulation run. For Demo purposes, we recommend the small Gangelt (10% of population and buildings), which takes about 10 minutes on a personal desktop computer.

## Integration of external data
Transition probabilities and time-dependent infectiousness:\
Hourly transition probabilities between agent states and hourly infection-emission rates are defined in distinct csv-files. The file simulation_configuration.csv defines the path to the source-file for each transition, the dependency on the duration in specific states and whether the transition rates are to be considered age-specific.

Location factors:\
File with relative infectivities for different location-types (Currently default-factor 1 for all location-types).

Geodata:\
Files with geo-information on each world to be modelled to initiate world is found as csv-files in the directory 'datafiles'.

Schedule Definition:\
The schedules, which define agent-routines are provided as csv in the directory 'inputs'.

## Disclaimer
Files not mentioned in this README are required but can be ignored by any non-developer. We still have to update our folder structure and apologize for any resulting confusion.