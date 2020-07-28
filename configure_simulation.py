import pandas


class Simulation_Configuration(object):
    def __init__(self):
        print('init config')
        config_file = pandas.read_csv('simulation_configuration.csv', sep=',')
        self.infectivity_df = config_file.loc['infectivity_df', 'Value']
        self.recovery_df = config_file.loc['recovery_df', 'Value']
        self.hospitalisation_df = config_file.loc['hospitalisation_df', 'Value']
        self.icu_death_risk_df = config_file.loc['icu_death_risk_df', 'Value']
        self.general_death_risk_df = config_file.loc['general_death_risk_df', 'Value']
        self.to_icu_df = config_file.loc['to_icu_df', 'Value']
        self.icu_to_hospital_df = config_file.loc['icu_to_hospital_df', 'Value']
        self.diagnosis_df = config_file.loc['diagnosis_df', 'Value']
