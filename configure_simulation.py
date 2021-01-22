import pandas

loc_coeff_df = pandas.read_csv('location_coefficients.csv', sep=',')
location_coefficients = dict(zip(list(loc_coeff_df['Location']), list(loc_coeff_df['Coeff'])))

strain_infectivity_df = pandas.read_csv('strain_infectivity_factors.csv', sep=',')
strain_infectivity_factors = dict(
    zip(list(strain_infectivity_df['Strain']), list(strain_infectivity_df['Factor'])))
strain_infectivity_factors.update({'WT': 1})


class Simulation_Configuration(object):
    def __init__(self):
        config_file = pandas.read_csv('simulation_configuration.csv', sep=',', index_col=0)
        self.immunity_loss_df = config_file.loc['immunity_loss_df', 'File']
        self.infectivity_df = config_file.loc['infectivity_df', 'File']
        self.recovery_from_undiagnosed_df = config_file.loc['recovery_from_undiagnosed_df', 'File']
        self.recovery_from_diagnosed_df = config_file.loc['recovery_from_diagnosed_df', 'File']
        self.recovery_from_hospitalized_df = config_file.loc['recovery_from_hospitalized_df', 'File']
        self.recovery_from_icu_df = config_file.loc['recovery_from_icu_df', 'File']
        self.hospitalisation_df = config_file.loc['hospitalisation_df', 'File']
        self.death_from_undiagnosed_df = config_file.loc['death_from_undiagnosed_df', 'File']
        self.death_from_diagnosed_df = config_file.loc['death_from_diagnosed_df', 'File']
        self.death_from_hospitalized_df = config_file.loc['death_from_hospitalized_df', 'File']
        self.death_from_icu_df = config_file.loc['death_from_icu_df', 'File']
        self.to_icu_df = config_file.loc['to_icu_df', 'File']
        #self.icu_to_hospital_df = config_file.loc['icu_to_hospital_df', 'File']
        self.diagnosis_df = config_file.loc['diagnosis_df', 'File']

        self.immunity_loss_dependency = config_file.loc['immunity_loss_df', 'Dependency']
        self.infectivity_dependency = config_file.loc['infectivity_df', 'Dependency']
        self.hospitalisation_dependency = config_file.loc['hospitalisation_df', 'Dependency']
        self.to_icu_dependency = config_file.loc['to_icu_df', 'Dependency']
        #self.icu_to_hospital_dependency = config_file.loc['icu_to_hospital_df', 'Dependency']
        self.diagnosis_dependency = config_file.loc['diagnosis_df', 'Dependency']
        self.death_from_undiagnosed_dependency = config_file.loc['death_from_undiagnosed_df', 'Dependency']
        self.death_from_diagnosed_dependency = config_file.loc['death_from_diagnosed_df', 'Dependency']
        self.death_from_hospitalized_dependency = config_file.loc['death_from_hospitalized_df', 'Dependency']
        self.death_from_icu_dependency = config_file.loc['death_from_icu_df', 'Dependency']
        self.recovery_from_undiagnosed_dependency = config_file.loc['recovery_from_undiagnosed_df', 'Dependency']
        self.recovery_from_diagnosed_dependency = config_file.loc['recovery_from_diagnosed_df', 'Dependency']
        self.recovery_from_hospitalized_dependency = config_file.loc['recovery_from_hospitalized_df', 'Dependency']
        self.recovery_from_icu_dependency = config_file.loc['recovery_from_icu_df', 'Dependency']

        self.immunity_loss_age_dependency = config_file.loc['immunity_loss_df', 'Age_dependent']
        self.infectivity_age_dependency = config_file.loc['infectivity_df', 'Age_dependent']
        self.hospitalisation_age_dependency = config_file.loc['hospitalisation_df', 'Age_dependent']
        self.to_icu_age_dependency = config_file.loc['to_icu_df', 'Age_dependent']
        #self.icu_to_hospital_age_dependency = config_file.loc['icu_to_hospital_df', 'Age_dependent']
        self.diagnosis_age_dependency = config_file.loc['diagnosis_df', 'Age_dependent']
        self.death_from_undiagnosed_age_dependency = config_file.loc['death_from_undiagnosed_df', 'Age_dependent']
        self.death_from_diagnosed_age_dependency = config_file.loc['death_from_diagnosed_df', 'Age_dependent']
        self.death_from_hospitalized_age_dependency = config_file.loc['death_from_hospitalized_df', 'Age_dependent']
        self.death_from_icu_age_dependency = config_file.loc['death_from_icu_df', 'Age_dependent']
        self.recovery_from_undiagnosed_age_dependency = config_file.loc[
            'recovery_from_undiagnosed_df', 'Age_dependent']
        self.recovery_from_diagnosed_age_dependency = config_file.loc['recovery_from_diagnosed_df', 'Age_dependent']
        self.recovery_from_hospitalized_age_dependency = config_file.loc[
            'recovery_from_hospitalized_df', 'Age_dependent']
        self.recovery_from_icu_age_dependency = config_file.loc['recovery_from_icu_df', 'Age_dependent']
