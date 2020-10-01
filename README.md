# TBP HU-Berlin SARS-CoV-2 infection transmission ABM 

## General Information
The information regarding the data used in this model as well as its documentation and developer information can be found in this repository's [wiki](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/wikis/home).

This model is maintained by the [Klipp lab for theoretical biophysics](https://rumo.biologie.hu-berlin.de/tbp/index.php/en/) at the Humboldt Universität zu Berlin.

Python commands are highlighted by green color throughout this document.

## Setup
The code in this repository was implemented using python 3.7 \
Only this version or newer versions of python are supported.

### Quick setup using conda
Follow these three steps to make use of the virtual environment provided in the repository for a quick and optimal setup. 
1. First, clone this repository to your local machine if you have not done so yet. 

2. Then, make sure you have Anaconda/Miniconda3 installed by running the following code in your terminal
    ```
    conda --v
    ```
    This should return something like `conda 4.X.X`. If it doesn't, [install the latest Miniconda3](https://docs.conda.io/en/latest/miniconda.html). \
    To make sure you have the latest version, run
    ```
    conda update conda
    ```
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


## Usage
To run the model, the jupyter notebook [RUN_CoronaABM.ipynb](https://ford.biologie.hu-berlin.de/jwodke/corona_model/-/blob/development/RUN_CoronaABM.ipynb) is provided.

This notebook contains the commands required to initialize a modeled world (using a small version (10%) of Gangelt) and to run GERDA simulations, including manual adjustment of parameters for 'infectivity', 'mean interaction frequency', and 'non-compliance probability'.

General commands:
\textbullet a world is initialized by:
\textcolor{blue}{COMMAND}
\textbullet a simulation is run by:
COMMAND

For comparative simulations, the same initialized world has to be used for the initial simulations. If non-pharmaceutical interventions shall be testet, the simulation has to be split into consecutive runs. The first simulation, simulation1, (using the modeled world as input and starting at time T=0) is run until the time point the intervention starts. For the consecutive simulation, the intervention has to be defined, e.g. for 'close all locations' (to represent a full lockdown) the location closure has to be incorporated by the following loop:
for loc in simulation1.locations:
    loc.close()
The second simulation, simulation2, (using simulation1 as input and starting at T=finalTime of simulation1) sebsequently is run until the end time of the tested intervention. For the third simulation, simulation3, (using simulation2 as input and starting at T=finalTime of simulation2) the closure of locations has to be reset:
for loc in simulation2. locations:
    loc.reset()

An example for comparative simulations (close all, reopen all) is already shown in cells XXX.
See the RUN_CoronaABM.ipynb for the most recent visualization options.

More options are currently continuously added on a daily basis. Please contact us (coronaModel@hu-berlin.de), if the notebook is not working or if the information is oudated.
