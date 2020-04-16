import pickle
import time

timestr = time.strftime("%Y%m%d-%H:%M:%S")
def save_simulation_object(saving_object, filename, date_suffix=True):
    """
    pickles passed object to saved_objects/filename+date+time+'.pkl'
    :param saving_object: object(modeledPopulatedWorld or Simulation) to be saved
    :param filename: string, file to which it should be saved - date and time will be added
    :param date_suffix: bool, whether to add date and time to filename
    """

    if date_suffix == True:
        timestr = time.strftime("%Y%m%d-%H:%M:%S")
        filename = filename+timestr
    with open('saved_objects/'+filename+'.pkl', 'wb') as f:
        pickle.dump(saving_object, f)

def load_simulation_object(filename):
    """
    :param filename: string of filename in saved_objects directory
    :return: object deserialised from pickle
    """
    with open('saved_objects/'+filename, 'rb') as f:
        loaded_object = pickle.load(f)
    return loaded_object