class Location(object):
	def __init__(self, ID, coordinates, location_type, people_present=set(), location_factor=0.001): # runs good with 50 people and 10 infected and 5 location
		self.ID = ID
		self.people_present = people_present
		self.location_factor = location_factor
		self.coordinates = coordinates
		self.location_type = location_type

	def enter(self, person):
		self.people_present.add(person)

	def leave(self, person):
		self.people_present.remove(person)

	def infection_risk(self):	# this needs improvement, it's simple and preliminary
		infected = sum([1 for p in self.people_present if p.status=='I']) #/float(len(self.people_present)) # get fraction of infected individuals in location
		risk = self.location_factor*infected
		return risk
		