import numpy as np
import pandas as pd

berlin_df = pd.read_csv('datafiles/berlinbrandenburgpopulation.csv')
germany_df = pd.read_csv('datafiles/germanypopulation.csv')
heinsberg_df = pd.read_csv('datafiles/heinsbergpopulation.csv')


def empirical_cumulative_distribution(df):
    """
    generate list of cumulative probabilities for random_age
    :param df: pandas dataframe of age categories andd people per age category
    :return: list with boundaries between probabilities eg [0.1, 0.7, 0.79]
    """

    n_per_bin = df['number_ppl_of_bin']
    # boundaries of bins where for each consecutive pair a bin exists with [a, b)
    bins = [0] + list(df['upper_bounds_of_bins_not_incl'])

    binsupperbounds_list = bins[1:]
    p_of_bin = n_per_bin / np.sum(n_per_bin)  # probability of being in given bin

    # there are ages from [0, 99]
    ages = np.arange(0, 100)
    p_of_age = np.zeros(100)

    # probability of having certain age
    for index in range(len(bins) - 1):
        # bin is [index, index+1)
        bin_size = bins[index + 1] - bins[index]
        for i in np.arange(bins[index], bins[index + 1]):
            p_of_age[i] = p_of_bin[index] / bin_size

    # ecdf of ages 
    cum_p_of_age = np.cumsum(p_of_age[:-1])
    return cum_p_of_age


ecd_berlin = empirical_cumulative_distribution(berlin_df)
ecd_germany = empirical_cumulative_distribution(germany_df)
ecd_heinsberg = empirical_cumulative_distribution(heinsberg_df)


# function to draw an age from the ecdf
def random_age(loc_string='Heinsberg'):
    """
    samples from empirical age distribution
    :param loc_string: string for which population, choose 'Berlin' or 'Germany'
    :return: age, an int
    """
    locations = ['Germany', 'Berlin', 'Heinsberg']
    assert loc_string in locations, f'population from which age drawn not set. choose from {locations}'

    if loc_string == 'Berlin':
        cumulative_p = ecd_berlin
    elif loc_string == 'Germany':
        cumulative_p = ecd_germany
    elif loc_string == 'Heinsberg':
        cumulative_p = ecd_heinsberg

    value = np.random.random()
    age = np.searchsorted(cumulative_p, value, side='right')
    return age
