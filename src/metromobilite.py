#!/usr/bin/env python3

import requests #To send get request to API
import json     #To handle API response

from datetime import datetime

#Constants 
API_URL = "https://data.mobilites-m.fr/api"
HEADERS = {"origin": 'mtagPython'}
NUMBER_OF_SECONDS_PER_DAY = 24*60*60

def get_routes():
    # get all the lines
    r = requests.get(API_URL+'/routers/default/index/routes', headers=HEADERS)
    return r.json()

def get_stops(route_id):
    # get all the stops of a line
    r = requests.get(API_URL+'/routers/default/index/routes/'+route_id+'/clusters', headers=HEADERS)
    
    stops = []
    for stop in r.json():
        stops.append({"id" : stop["code"], 'name' : stop["name"]})

    return stops
    
def get_realtime_arrivals(route_id, stop_id, include_theoric_arrivals = False):
    # per stop_id (stop id is one direction)
    r = requests.get(API_URL+'/routers/default/index/clusters/'+stop_id+'/stoptimes?route='+route_id, headers=HEADERS)
    arrivals = []
    for directions in r.json():
        direction = directions["pattern"]["desc"]
        for arrival in directions["times"]:
            if arrival["realtime"] or include_theoric_arrivals:
                arrivals.append({'direction' : direction, 'arrival' : seconds_to_date_realtime(arrival["realtimeArrival"]), 'realtime' : arrival["realtime"]})
    return arrivals

def get_theoric_arrivals(route_id, stop_id, date):
    # get the theoric arrivals for a given day
    r = requests.get(API_URL+'/routers/default/index/clusters/'+stop_id+'/stoptimes/'+date.strftime("%Y%m%d")+'?route='+route_id, headers=HEADERS)
    arrivals = []
    for directions in r.json():
        direction = directions["pattern"]["desc"]
        for arrival in directions["times"]:
            arrivals.append({'direction' : direction, 'arrival' : seconds_to_date_theoric(arrival["realtimeArrival"], date), 'realtime' : arrival["realtime"]})
    return arrivals

def seconds_to_date_realtime(seconds):
    #the date is guessed, works only with realtime arrivals
    now = datetime.now()
    midnight_epoch_reference = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if(now.hour < 4): #for transports running after midnight seconds are counted since previous day
        midnight_epoch_reference = now.replace(day=-1, hour=0, minute=0, second=0, microsecond=0)
    return datetime.fromtimestamp(midnight_epoch_reference.timestamp() +seconds)

def seconds_to_date_theoric(seconds, date):
    #it is assumed that the seconds were returned from the theorical arrivals
    midnight_epoch_reference = date.replace(hour=0, minute=0, second=0, microsecond=0)
    return datetime.fromtimestamp(midnight_epoch_reference.timestamp() +seconds)


def main():
    routes = get_routes()
    for s in routes:
        print(s["id"]+"\t"+ s["shortName"] + "\t" + s["longName"])

    stops = get_stops("SEM:A")
    for s in stops:
        print(s["id"]+"\t"+ s["name"] )
    
    realtime_arrivals = get_realtime_arrivals("SEM:C1",'SEM:GENCHAVANT')
    for r in realtime_arrivals : 
        print(r["direction"]+'\t'+str(r['arrival'])+'\t'+str(r['realtime']))
    
    
    theoric_arrivals = get_theoric_arrivals("SEM:A",'SEM:GENCHAVANT', datetime.now())
    for r in theoric_arrivals : 
        print(r["direction"]+'\t'+str(r['arrival'])+'\t'+str(r['realtime']))

if __name__ == "__main__":
    main()