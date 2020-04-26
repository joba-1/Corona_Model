import pandas as pd
import numpy.random as npr


"""
SYNOPSIS:
This script samples households from given distributions of age, household type
and household size. It returns a list containing the household type, household
size and the ages of the household members. 

INPUT DATA: 
- distribution of households per type (not the of people per household type)
- household size distributions per household type
- age distributions per household type

This data was calculated based on data by the Federal Office for Statistics
(Statistisches Bundesamt, DESTATIS). ### REFER TO NOTEBOOK OR WIKI HERE

OUTPUT: 

household type (a string)
household size (an integer value)
ages of household members (a sorted list of integer values)

e.g.: ['Paare ohne Kind(er)', 2, [43, 48]]
"""

## Define constants ----------------------------------------------------------

age_to_become_a_parent = 30 ## Average age to become a parent (for women)
std_dev_parents = 5 ## Std. dev for age difference between parents TODO Source this

median_age_diff_kids = 3.5 ## Median age difference between siblings TODO: add source to wiki
std_dev_age_diff_kids = median_age_diff_kids/2 ## ASSUMPTION

## Import data ---------------------------------------------------------------

directory = './datafiles/demographics/'

hhds_per_type = pd.read_csv(directory + 'household_type_relative_share.csv', index_col=0)
hhd_size_dist_per_hhd_type = pd.read_csv(directory + 'household_size_distributions_per_household_type.csv', index_col=0)
age_dist_per_hhd_type = pd.read_csv(directory + 'age_distribution_germany_per_household_type_and_year.csv', index_col=0)

## Check data import
#print(hhds_per_type)
#print(hhd_size_dist_per_hhd_type)
#print(age_dist_per_hhd_type)

## Parse data ----------------------------------------------------------------

## Relative share of households per type
hhd_types_list = list(hhds_per_type.T)
hhd_types_probabilities = [p for p in hhds_per_type['%']]

## Household size distributions per household type
hhd_size_dist_per_hhd_type_dict = {}
size_range = [int(size) for size in list(hhd_size_dist_per_hhd_type)] # Extract hhd sizes

for hhd_type in list(hhd_size_dist_per_hhd_type.T):
    
    ## Extract size distribution
    dist = [p for p in hhd_size_dist_per_hhd_type.loc[hhd_type]]

    ## Clean list (npr.choice will otherwise sample even if weights are zero)
    keeplist = [i for i in range(len(dist)) if dist[i] != 0.0] ## Get indices of elements that are non-zero
    dist = [dist[i] for i in keeplist] ## Drop zeroes, overwrite list
    sizes = [size_range[i] for i in keeplist] ##  Drop corresponding sizes

    ## Update dictionary
    hhd_size_dist_per_hhd_type_dict[hhd_type] = [sizes, dist]

## Age distributions per household type
age_dist_per_hhd_type_dict = {}

for hhd_type in list(age_dist_per_hhd_type):
    
    ## Get age distribution
    dist = [float(p) for p in age_dist_per_hhd_type[hhd_type]]
    
    ## Age range: get lower bound, upper bound
    lower_bound = (age_dist_per_hhd_type[hhd_type] != 0).idxmax(1)
    
    upper_bound = len(dist)
    
    if upper_bound > 100:
        #print('99')
        upper_bound = 100
    
    ## Update dictionary
    age_range = [age for age in range(lower_bound, upper_bound)]
    age_dist_per_hhd_type_dict[hhd_type] = [age_range, dist[lower_bound:upper_bound]]

## Check data parsing
#print(hhd_types_list)
#print(hhd_types_probabilities,sum(hhd_types_probabilities))   ## 0.002 missing...
hhd_types_probabilities = [x/sum(hhd_types_probabilities) for x in hhd_types_probabilities]
#print(hhd_size_dist_per_hhd_type_dict)
#print(age_dist_per_hhd_type_dict)

def get_tables():
    return [hhd_types_list, hhd_types_probabilities, hhd_size_dist_per_hhd_type_dict, age_dist_per_hhd_type_dict]

## Function definition -------------------------------------------------------

def initialize_household():
    """TODO: describe what this function does"""

    ## Randomly pick household type
    hhd_type = npr.choice(hhd_types_list, p=hhd_types_probabilities)

    ## Extract age distribution, age range
    ages_to_sample = age_dist_per_hhd_type_dict[hhd_type][0]
    age_dist = age_dist_per_hhd_type_dict[hhd_type][1]
    age_dist = [x/sum(age_dist) for x in age_dist]

    ## Extract household size distribution, household sizes to sample
    hhd_sizes_to_sample = hhd_size_dist_per_hhd_type_dict[hhd_type][0]
    hhd_size_probabilities = hhd_size_dist_per_hhd_type_dict[hhd_type][1]
    hhd_size_probabilities = [x/sum(hhd_size_probabilities) for x in hhd_size_probabilities]
    ## Randomly pick number of household members
    hhd_mmbrs = npr.choice(hhd_sizes_to_sample, p=hhd_size_probabilities)

    ## Sample ages according to household type, then return household
    if hhd_type == 'Einpersonenhaushalte (Singlehaushalte)':
    
        age = npr.choice(ages_to_sample, p=age_dist)
        return [hhd_type, hhd_mmbrs, [age]]

    elif hhd_type == 'Paare ohne Kind(er)':
    
        ## Sample first age from distribution specific to that household type
        age1 = npr.choice(ages_to_sample, p=age_dist) 
        #age2 = npr.choice(ages_to_sample, p=age_dist) 
        
        ## Sample age2 from normal distribution around age1
        age2 = int(npr.normal(age1, age1/10)) # Increase standard deviation as a function of age1 (NOTE THIS IN WIKI)
        ## To avoid under-age members: conditionally repeat sampling
        while age2 not in ages_to_sample:
            age2 = int(npr.normal(age1, age1/10))
        
        return [hhd_type, hhd_mmbrs, [age1, age2]]

    elif hhd_type == 'Paare mit Kind(ern)':

        kids_cutoff = 30

        age_dist_children = [x/sum(age_dist[0:kids_cutoff]) for x in age_dist[0:kids_cutoff]]
        #age_dist_adults = [x/sum(age_dist[18:]) for x in age_dist[18:]]
    
        ## Sample age of first kid age:
        #print(ages_to_sample[0:18], age_dist_children)
        ages = [npr.choice(ages_to_sample[0:kids_cutoff], p=age_dist_children)]
        ## Flip a coin if the next kids are younger or older
        #next_kid_younger = npr.choice([-1, 1], p=[0.5, 0.5])
    
        ## Sample ages for the next kids
        for i in range(1, hhd_mmbrs - 2): ## -2 because of parents
            #mean = i * next_kid_younger * median_age_diff_kids + ages[0]
            ## NOTE: Use of abs() function here to aoid negative ages, but falsifies distribution, necessary because of the coin flip above...
            #ages.append(int(abs(npr.normal(mean, std_dev_age_diff_kids))))
            age = npr.choice(ages_to_sample[0:kids_cutoff], p=age_dist_children)
            while (age > 2*median_age_diff_kids+max(ages)) or (age < min(ages)-2*median_age_diff_kids):
                age = npr.choice(ages_to_sample[0:kids_cutoff], p=age_dist_children)
            ages.append(age)
        
        ages = sorted(ages) ## Sort ages
        oldest_kid = ages[-1] ## (This is used to sample parent age)
        #for i in range(2):
        #    ages.append(npr.choice(ages_to_sample[18:], p=age_dist_adults))
    
        # Sample two parents
        ages.append(int(npr.normal(oldest_kid + age_to_become_a_parent, std_dev_parents)))
        ages.append(int(npr.normal(oldest_kid + age_to_become_a_parent, std_dev_parents)))
     
        # TODO: NOTE IN WIKI: ignore seniors (grandparents living with families 
        # -> assume they live as couples, alone or in flatshares)

        #ages = list(npr.choice(ages_to_sample, hhd_mmbrs, p=age_dist)) 
        
        return [hhd_type, hhd_mmbrs, ages]

    elif hhd_type == 'Alleinerziehende Elternteile':
    
        kids_cutoff = 30

        age_dist_children = [x/sum(age_dist[0:kids_cutoff]) for x in age_dist[0:kids_cutoff]]
        #age_dist_adults = [x/sum(age_dist[18:]) for x in age_dist[18:]]
    
        ## Sample age of first kid age:
        #print(ages_to_sample[0:18], age_dist_children)
        ages = [npr.choice(ages_to_sample[0:kids_cutoff], p=age_dist_children)]
        ## Flip a coin if the next kids are younger or older
        #next_kid_younger = npr.choice([-1, 1], p=[0.5, 0.5])
    
        ## Sample ages for the next kids
        for i in range(1, hhd_mmbrs - 1): ## -1 because of parent
            #mean = i * next_kid_younger * median_age_diff_kids + ages[0]
            ## NOTE: Use of abs() function here to aoid negative ages, but falsifies distribution, necessary because of the coin flip above...
            #ages.append(int(abs(npr.normal(mean, std_dev_age_diff_kids))))
            age = npr.choice(ages_to_sample[0:kids_cutoff], p=age_dist_children)
            while (age > 2*median_age_diff_kids+max(ages)) or (age < min(ages)-2*median_age_diff_kids):
                age = npr.choice(ages_to_sample[0:kids_cutoff], p=age_dist_children)
            ages.append(age)
        
        ages = sorted(ages) ## Sort ages
        oldest_kid = ages[-1] ## (This is used to sample parent age)
        #for i in range(2):
        #    ages.append(npr.choice(ages_to_sample[18:], p=age_dist_adults))
    
        # Sample two parents
        ages.append(int(npr.normal(oldest_kid + age_to_become_a_parent, std_dev_parents)))
        ages.append(int(npr.normal(oldest_kid + age_to_become_a_parent, std_dev_parents)))

        #ages = list(npr.choice(ages_to_sample, hhd_mmbrs, p=age_dist)) 

        return [hhd_type, hhd_mmbrs, ages]

    elif hhd_type == 'Mehrpersonenhaushalte ohne Kernfamilie':

        ## Just sample ages at random
        ages = list(npr.choice(ages_to_sample, hhd_mmbrs, p=age_dist)) 
        ## TODO: note this in wiki (unrealistic, accounts for 2.5 % of all hhds & difficult to make simplifying assumptions
        
        return [hhd_type, hhd_mmbrs, ages]

    else: 
        
        print('Household type not found.')
        print('Please check input data and data parsing for errors.')
        return None

## MAIN ----------------------------------------------------------------------

if __name__ == '__main__':
    
    print(initialize_household())

