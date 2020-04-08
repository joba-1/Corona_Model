import numpy as np

# Berlin&Brandenburg data - when there is data uploaded i will use that
nperbin_list = [190018,  246820,  74422,  50918,  141626,  180919, 234197,  218033,  182471,  628523,  183213,  660990]
# boundaries of bins where for each consecutive pair a bin exists with [a, b)
bins_list=[0, 6, 15, 18, 20, 25, 30, 35, 40, 45, 60, 65, 100]

binsupperbounds_list = bins_list[1:]
pofbin_list = nperbin_list/np.sum(nperbin_list) # probability of being in given bin

# there are ages from [0, 99]
ages_array = np.arange(0, 100)
pofage_array = np.zeros(100)

# probability of having certain age
for index in range(len(bins_list)-1):
    # bin is [index, index+1)
    binsize_int=bins_list[index+1]-bins_list[index]
    for i in np.arange(bins_list[index], bins_list[index+1]):
        pofage_array[i] = pofbin_list[index]/binsize_int

# ecdf of ages 
cumpofage_list = np.cumsum(pofage_array[:-1])

# function to draw an age from the ecdf
def RandomAge():
    """
    samples from empirical age distribution
    :return: age, an int
    """
    v_float = np.random.random()
    age_int = np.searchsorted(cumpofage_list, v_float, side='right')
    return age_int 