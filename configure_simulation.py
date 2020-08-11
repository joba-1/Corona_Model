import pandas


class Simulation_Configuration(object):
    def __init__(self):
        config_file = pandas.read_csv('simulation_configuration.csv', sep=',', index_col=0)
        self.infectivity_df = config_file.loc['infectivity_df', 'File']
        self.recovery_from_undiagnosed_df = config_file.loc['recovery_from_undiagnosed_df', 'File']
        self.recovery_from_diagnosed_df = config_file.loc['recovery_from_diagnosed_df', 'File']
        self.recovery_from_hospitalized_df = config_file.loc['recovery_from_hospitalized_df', 'File']
        self.hospitalisation_df = config_file.loc['hospitalisation_df', 'File']
        self.death_from_undiagnosed_df = config_file.loc['death_from_undiagnosed_df', 'File']
        self.death_from_diagnosed_df = config_file.loc['death_from_diagnosed_df', 'File']
        self.death_from_hospitalized_df = config_file.loc['death_from_hospitalized_df', 'File']
        self.death_from_icu_df = config_file.loc['death_from_icu_df', 'File']
        self.to_icu_df = config_file.loc['to_icu_df', 'File']
        self.icu_to_hospital_df = config_file.loc['icu_to_hospital_df', 'File']
        self.diagnosis_df = config_file.loc['diagnosis_df', 'File']

        self.infectivity_dependency = config_file.loc['infectivity_df', 'Dependency']
        self.hospitalisation_dependency = config_file.loc['hospitalisation_df', 'Dependency']
        self.to_icu_dependency = config_file.loc['to_icu_df', 'Dependency']
        self.icu_to_hospital_dependency = config_file.loc['icu_to_hospital_df', 'Dependency']
        self.diagnosis_dependency = config_file.loc['diagnosis_df', 'Dependency']
        self.death_from_undiagnosed_dependency = config_file.loc['death_from_undiagnosed_df', 'Dependency']
        self.death_from_diagnosed_dependency = config_file.loc['death_from_diagnosed_df', 'Dependency']
        self.death_from_hospitalized_dependency = config_file.loc['death_from_hospitalized_df', 'Dependency']
        self.death_from_icu_dependency = config_file.loc['death_from_icu_df', 'Dependency']
        self.recovery_from_undiagnosed_dependency = config_file.loc['recovery_from_undiagnosed_df', 'Dependency']
        self.recovery_from_diagnosed_dependency = config_file.loc['recovery_from_diagnosed_df', 'Dependency']
        self.recovery_from_hospitalized_dependency = config_file.loc['recovery_from_hospitalized_df', 'Dependency']
