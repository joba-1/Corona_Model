import pandas


class Simulation_Configuration(object):
    def __init__(self):
        config_file = pandas.read_csv('simulation_configuration.csv', sep=',', index_col=0)
        self.infectivity_df = config_file.loc['infectivity_df', 'File']
        self.recovery_df = config_file.loc['recovery_df', 'File']
        self.hospitalisation_df = config_file.loc['hospitalisation_df', 'File']
        self.icu_death_risk_df = config_file.loc['icu_death_risk_df', 'File']
        self.general_death_risk_df = config_file.loc['general_death_risk_df', 'File']
        self.to_icu_df = config_file.loc['to_icu_df', 'File']
        self.icu_to_hospital_df = config_file.loc['icu_to_hospital_df', 'File']
        self.diagnosis_df = config_file.loc['diagnosis_df', 'File']
        self.infectivity_dependency = config_file.loc['infectivity_df', 'Dependency']
        self.recovery_dependency = config_file.loc['recovery_df', 'Dependency']
        self.hospitalisation_dependency = config_file.loc['hospitalisation_df', 'Dependency']
        self.icu_death_risk_dependency = config_file.loc['icu_death_risk_df', 'Dependency']
        self.general_death_risk_dependency = config_file.loc['general_death_risk_df', 'Dependency']
        self.to_icu_dependency = config_file.loc['to_icu_df', 'Dependency']
        self.icu_to_hospital_dependency = config_file.loc['icu_to_hospital_df', 'Dependency']
        self.diagnosis_dependency = config_file.loc['diagnosis_df', 'Dependency']
