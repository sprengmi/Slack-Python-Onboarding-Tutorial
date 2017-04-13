import json
import time
import requests

"""
	sprengmi 2017-04-10:
	This code connects to the Chicago CTA Bus Tracker API to receive 
		bus arrival predictions times and also will retrieve direction
		and stop lists to assist users with finding their desired stop ID
"""

_KEY = 'wJywQ5bPi2t5mpNBnkj6kf7UX'



# GetDirections: Retrieves the valid directions for a given bus route
# Input: Route#
# Returns json with Directions for given Route
''' ie:
	{"dir": "Eastbound"},
	{"dir": "Westbound"}
'''
def getdirections(rt):
	url = ('http://www.ctabustracker.com/bustime/api/v2/getdirections?key=' + _KEY 
		+ '&rt=' + str(rt) + '&format=json')
	r = requests.get(url).json()
	directions = r["bustime-response"]["directions"]
	return directions

# GetStops: Retrieves all Stops for a given Route & Direction 
#				(Both Route & Direction are needed, bustracker API will not return stops w/out a Direction)
# Input: Route#, Direction
# Returns: json with all stop info
'''	ie:
	{	"stpid": "741",
		"stpnm": "530 W Grand",
		"lat": 41.891228406371,
		"lon": -87.643132209778	}, ...
'''
def getstops(rt, dir):
	url = ('http://www.ctabustracker.com/bustime/api/v2/getstops?key=' + _KEY 
		+ '&rt=' + str(rt) + '&dir=' + str(dir) + '&format=json')
	r = requests.get(url).json()
	stops = r["bustime-response"]["stops"]
	
	return stops

# Predictions: Returns a formatted message with the predicted upcoming bus arrival times for a given stop ID
# Input: StopID
# Returns: string formatted to list given Route, Direction, Stop Name and the upcoming arrivals
def predictions(stpid):
	route1 = ''
	url = ('http://www.ctabustracker.com/bustime/api/v2/getpredictions?key=' + _KEY + '&stpid=' + stpid + '&format=json')
	r = requests.get(url).json()
	prd = r["bustime-response"]
	i=0
	l = len(prd["prd"])
	for bus in prd["prd"]:
		if l == 1:
			route1 = bus["prdctdn"] + ' minutes.'
		
		elif i < l - 1:
			route1 = route1 + bus["prdctdn"] + ', '
			i=i+1
		else:
			route1 = route1 + 'and ' + bus["prdctdn"] + ' minutes.'
		rtdir = bus["rtdir"]
		rt = bus["rt"]
		des = bus["des"]
		stpnm = bus["stpnm"]
	msg = ( rtdir + ' Route ' + rt + ' toward ' + des + ' will arrive at ' + stpnm + ' in: ' + 	route1)
	#print(msg)
	return msg

	
	
# ========= python command line interface ========= #	
def main():
	print('Welcome to the CTA BusTracker API interface please select from the following options: ')
	print('1) I know my stop ID, give me the predictions')
	print('2) Find my stop ID')
	type = input('Selection: ')
	if type == 1:
		stpid = str(input('Enter your stop ID: '))
		predictions(stpid)
	if type == 2:
		rt = str(input('Enter your Route Number: '))
		dir = directions(rt)
		stpid = stops(rt, dir)
		predictions(stpid)
		
	return type
	
#python command line interface for stops
def stops(rt, dir):
	url = ('http://www.ctabustracker.com/bustime/api/v2/getstops?key=' + _KEY 
		+ '&rt=' + rt + '&dir=' + dir + '&format=json')
	r = requests.get(url).json()
	stops = r["bustime-response"]["stops"]
	i=1
	for s in stops:
		print(str(i)+") " + s["stpnm"])
		i=i+1
	selection = input("Selections: ")-1
	stpid = stops[selection]["stpid"]
	print("You selected " + stops[selection]["stpnm"] + " | StopID: " + stpid)
	return stpid
	
#python command line interface for directions
def directions(rt):
	url = ('http://www.ctabustracker.com/bustime/api/v2/getdirections?key=' + _KEY 
		+ '&rt=' + str(rt) + '&format=json')
	r = requests.get(url).json()
	directions = r["bustime-response"]["directions"]
	print("Select the Route Direction of the stop you'd like to find by typing the corresponding number: ")
	i=1
	for d in directions:
		print(str(i)+") " + d["dir"])
		i=i+1
	selection = input("Selection: ")-1
	dir = directions[selection]["dir"]
	#print("DIRECTION: "+ dir)
	return dir
