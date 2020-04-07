class Location(object):
	def __init__(self, ID_int, coordinates_tuple, location_type_str, people_present_set=set(), location_factor_float=0.001): # runs good with 50 people and 10 infected and 5 location
		self.ID_int = ID_int
		self.people_present_set = people_present_set
		self.location_factor_float = location_factor_float
		self.coordinates_tuple = coordinates_tuple
		self.location_type_str = location_type_str

	def Enter(self, person_hu):
		self.people_present_set.add(person_hu)

	def Leave(self, person_hu):
		self.people_present_set.remove(person_hu)

	def Infection_risk(self):	# this needs improvement, it's simple and preliminary
		infected_int = sum([1 for p in self.people_present_set if p.status_str=='I']) #/float(len(self.people_present)) # get fraction of infected individuals in location
		risk_float = self.location_factor_float*infected_int
		return risk_float
		