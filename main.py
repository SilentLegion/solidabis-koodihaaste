import json
from flask import Flask, jsonify, render_template, request

class Stop:
	"""A class containing details for each stop."""
	def __init__(self, name):
		self.name = name
		self.connection_names = []
		self.connection_durations = []
	
	def add_connection(self, connection_name, duration): #When a connection is added it records the stop name and the duration
		"""Stores a connection for a class"""
		self.connection_names.append(connection_name) #These are seperate lists but they are ordered so the index of a connection is the index of it's duration
		self.connection_durations.append(duration)
	
	def check_connections_for_stop(self, stop_name, stops_used = [], duration_sum = 0):
		"""Checks if this stop connects to a specific stop or if not it recursively checks if stops connected to this stop contain it."""
		best_route = []
		best_time = 0
		used = stops_used.copy()
		used.append(self.name)
		for i in range(len(self.connection_names)): #For each connection this stop has
			if stop_name == self.connection_names[i]: #If the connecting stop is the final stop
				best_route = used
				best_route.append(self.connection_names[i])
				best_time = duration_sum + self.connection_durations[i] #If the final stop is found the best route and time are recorded
				return best_route, best_time #No need to further check for routes so the best route and time are returned
			elif self.connection_names[i] not in used: #If next stop hasn't been used yet
				a = get_stop_by_name(self.connection_names[i])
				route, time = a.check_connections_for_stop(stop_name, used, duration_sum + self.connection_durations[i]) #ask the next stop whether it is connected to the final stop, used stops are sent so it doesn't loop
				if time > 0 and best_time == 0: #The first time a connection is found the returned time must be greater than 0 and the best time will be 0
					best_time = time
					best_route = route #Set the current time and route to be best
				elif time < best_time and time > 0 and best_time != 0: #if a second route is found then the time must be less than the best time to be recorded
					best_time = time
					best_route = route
		return best_route, best_time
				
def get_route(first, last):
	"""Finds a route between two stops by calling the Stop class function checkConnectionForStop() and then calling get_route_between_stops() to get the name of the route."""
	s = get_stop_by_name(first)
	route, time = s.check_connections_for_stop(last)
	route_names = []
	for i in range(len(route)-1):
		route_names.append(get_route_between_stops(route[i], route[i+1]))
	
	return route, time, route_names

def get_route_between_stops(a, b):
	"""Gets the name of the route between two stops"""
	routes = list(data['linjastot'].keys()) #Create list of route names
	for r in range(len(routes)): #For each route "r"
		for n in range(len(data['linjastot'][routes[r]])-1): #For each stop "n" in the route except the last
			if a == data['linjastot'][routes[r]][n] and b == data['linjastot'][routes[r]][n+1]:
				return routes[r]
			elif b == data['linjastot'][routes[r]][n] and a == data['linjastot'][routes[r]][n+1]:
				return routes[r]
	
def get_stop_by_name(stop):
	"""Searches the list of stops for a stop with a specific name."""
	global stops
	for s in stops:
		if s.name == stop:
			return s

def initialise_stop_list():
	"""Sets up a list of Stop classes, one for each stop."""
	global data
	global stops
	stops = []
	for x in data['pysakit']:
		stops.append(Stop(x))

def populate_stops_with_connections():
	"""Creates a list of connections for each stop based on the possible routes."""
	routes = list(data['linjastot'].keys()) #Create list of route names
	for r in range(len(routes)): #For each route "r"
		for n in range(len(data['linjastot'][routes[r]])-1): #For each stop "n" in the route except the last
			s = get_stop_by_name(data['linjastot'][routes[r]][n]) #"s" is stop "n"
			s2 = get_stop_by_name(data['linjastot'][routes[r]][n+1]) #"s2" is stop "n+1"
			for t in range(len(data['tiet'])): #For each road connection
				if data['tiet'][t]['mista'] == s.name and data['tiet'][t]['mihin'] == s2.name: #If "s" equals mista and "s2" equals mihin
					s.add_connection(s2.name, data['tiet'][t]['kesto']) #Add the connection to the list of possible connections for the stop "s"
					s2.add_connection(s.name, data['tiet'][t]['kesto']) #Also add the reverse connection to the stop "s2"
					break #if the road connection is found no need to continue looking through the connections
				elif data['tiet'][t]['mihin'] == s.name and data['tiet'][t]['mista'] == s2.name: #same as previous but if they are reversed
					s.add_connection(s2.name, data['tiet'][t]['kesto'])
					s2.add_connection(s.name, data['tiet'][t]['kesto'])
					break

def open_data():
	with open('reittiopas.json', 'r', encoding='utf-8') as a: #Opens the .json file containing data for the stops and routes
		global data
		data = a.read()
		data = json.loads(data) #Uses the json module to format the file so python can directly read it

open_data()
initialise_stop_list()
populate_stops_with_connections() #Unpack and interpret the .json file once when the site is opened

app = Flask(__name__)
@app.route("/", methods = ['POST', 'GET'])
def home(): #Main page for website
	start = ''
	finish = ''
	if request.method == 'POST':
		result = request.form #Attempt to retrieve the input from the html text boxes
	try: #Check if inputs are valid
		start = result['start'].upper()
		finish = result['end'].upper()
		if (not start.isalpha()) or  len(start) != 1:
			raise
		if (not finish.isalpha()) or len(finish) != 1:
			raise
		if start not in data['pysakit']:
			raise
		if finish not in data['pysakit']:
			raise
	except: #If input is not valid the html page is rendered with an error message
		if len(start) == 0 or len(finish) == 0:
			response = 'Täytä kentät'
			return render_template("home.html", output=response)
		response = 'Huonot pysäkit, kuuluu olla oikeita pysäkkejä.'
		return render_template("home.html", output=response, colour='Red')
	try: #attempt to get the route data for the inputed stops and output it
		route, time, route_names = get_route(start, finish)
		if time == 0 or route == []: #If there is an issue with generating an output this raises an error
			raise Exception('')
		response = 'Reitti alkaa pysäkistä {} linjalla {}, '.format(route[0], route_names[0])
		for i in range(len(route_names)): #If the output seems to be correct this starts to generate a response string based on it, we only need to write when a route changes instead of the writing from A to B with green to C with green
			if i == 0 and len(route_names) > 1: #This gets around the edge case of having only 1 route so it never changes
				pass
			elif i == len(route_names)-1: #If it's the last stop we end the response
				response = response + 'pysäkille {} asti. '.format(route[i+1])
			elif route_names[i] != route_names[i-1]: #Modifiy the response if you have to change routes
				response = response + 'pysäkille {} asti. Matka jatkuu linjalla {} '.format(route[i], route_names[i])
		response = response + 'Matkan kesto on {}. '.format(time) #Not needed but it's nice to know the time for the trip
		return render_template("home.html", output = response) #Render the html page with the response
	except:
		response='Virhe reittin hakemisessa.'
		return render_template("home.html", output=response, colour='Red') #Rendering the page with an error message if something went wrong

@app.route("/kartta")
def kartta():
	return render_template("kartta.html") #Load the map of the region

if __name__ == "__main__": 
	import os  
	port = int(os.environ.get('PORT', 33507)) 
	app.run(host='0.0.0.0', port=port)
