import pickle
import time
import glob
import os


def get_file_size(file_path):
    """
    get size of file at filename location
    :param file_path: string, path to file
    :return: size of file int or -1 if file not found
    """
    if os.path.isfile(file_path):
        return os.stat(file_path).st_size
    else:
        raise FileNotFoundError('The file {} could not be found'.format(file_path))


def wait_for_write(file_path):
    """
    wait for file to be written by checking no size change after 1 second
    :param file_path: string, realtive path to file
    """
    current_size = get_file_size(file_path)
    time.sleep(1)
    while current_size != get_file_size(file_path) or get_file_size(file_path) == 0:
        current_size = get_file_size(file_path)
        time.sleep(1)


def save_simulation_object(saving_object, filename, date_suffix=False, folder='models/simulations/'):
    """
    pickles passed object to saved_objects/filename+date+time+'.pkl'
    :param saving_object: object(modeledPopulatedWorld or Simulation) to be saved
    :param filename: string, file to which it should be saved - date and time will be added
    :param date_suffix: bool, whether to add date and time to filename
    """

    if date_suffix:
        timestr = '_' + time.strftime("%d-%m-%Y_%H-%M-%S")
    else:
        timestr = ''
    with open(folder + filename + timestr + '.pkl', 'wb') as f:
        pickle.dump(saving_object, f)


def load_simulation_object(filename, folder='models/simulations/'):
    """
    :param filename: string of filename in saved_objects directory
    :return: object deserialised from pickle
    """

    filepath = glob.glob(folder + filename + '*')
    assert len(filepath) <= 1, 'More than one pickle file found for the given filename \'{}\''.format(filename)
    if len(filepath) == 1:
        filepath = filepath[0]
    else:
        print('The specified .pkl is file not yet available or could not be found. Waiting shortly before retrying...')
        time.sleep(10)
        filepath = glob.glob(folder + filename + '*')
        assert len(filepath) == 1, 'The file {} could not be found'.format(filename)
    wait_for_write(filepath)
    with open(filepath, 'rb') as f:
        loaded_object = pickle.load(f)
    return loaded_object
