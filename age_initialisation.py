import numpy as np
import pandas as pd

berlindf = pd.read_csv('datafiles/berlinbrandenburgpopulation.csv')
germanydf = pd.read_csv('datafiles/germanypopulation.csv')
heinsbergdf = pd.read_csv('datafiles/heinsbergpopulation.csv')


def EmpCumDist(df):
    """
    take df with bin sizes and number per bin
    return list of probabilities per age (0:99)
    """

    nperbin_list = df['number_ppl_of_bin']
    # boundaries of bins where for each consecutive pair a bin exists with [a, b)
    bins_list = [0] + list(df['upper_bounds_of_bins_not_incl'])

    binsupperbounds_list = bins_list[1:]
    pofbin_list = nperbin_list / np.sum(nperbin_list)  # probability of being in given bin

    # there are ages from [0, 99]
    ages_array = np.arange(0, 100)
    pofage_array = np.zeros(100)

    # probability of having certain age
    for index in range(len(bins_list) - 1):
        # bin is [index, index+1)
        binsize_int = bins_list[index + 1] - bins_list[index]
        for i in np.arange(bins_list[index], bins_list[index + 1]):
            pofage_array[i] = pofbin_list[index] / binsize_int

    # ecdf of ages 
    cumpofage_list = np.cumsum(pofage_array[:-1])
    return cumpofage_list

ecdberlin_list = EmpCumDist(berlindf)
ecdgermany_list = EmpCumDist(germanydf)
ecdheinsberg_list = EmpCumDist(heinsbergdf)

# function to draw an age from the ecdf
def RandomAge(loc_string='Heinsberg'):
    """
    samples from empirical age distribution
    :param loc_string: string for which population, choose 'Berlin' or 'Germany'
    :return: age, an int
    """
    locs_list = ['Germany', 'Berlin', 'Heinsberg']
    assert loc_string in locs_list, f'population from which age drawn not set. choose from {locs_list}'

    if loc_string == 'Berlin':
        cump_list = ecdberlin_list
    elif loc_string == 'Germany':
        cump_list = ecdgermany_list
    elif loc_string == 'Heinsberg':
        cump_list = ecdheinsberg_list


    v_float = np.random.random()
    age_int = np.searchsorted(cump_list, v_float, side='right')
    return age_int
