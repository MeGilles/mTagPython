#!/usr/bin/env python3

import requests #To send get request to API
import json     #To handle API response
import argparse #For arguments

from datetime import timedelta #To swiftly convert time in sec to time in hh:mm:ss
from datetime import datetime #For current time

### Parsing of parameters
parser = argparse.ArgumentParser(description="Contacts MTAG API to get information")

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument(
        '-n',
        '-stop_name',
        help='Name of the stop to read information from',
        )

group.add_argument(
        '-l',
        '-list_stops',
        help='List the stops of the specified bus ID',
        action='store_true'
        )

group.add_argument(
        '-s',
        '-stop_id',
        help='ID of the stop to read information from, without the prefix "SEM:"',
        )

parser.add_argument(
        '-id',
        '-bus_id',
        help='Bus id of line to be checked',
        default='C1')

parser.add_argument(
        '-simple',
        help='Simplified output print',
        action='store_true'
        )

group.add_argument(
        '-custom',
        help='Custom command for I3',
        action='store_true'
        )

args = parser.parse_args()


#Constants 
API_BASE = "https://data.mobilites-m.fr/api/"
NAME_BASE = "SEM:"

class bcolors:     
    HEADER = "\033[95m"     
    OKBLUE = "\033[94m"     
    OKCYAN = "\033[96m"     
    OKGREEN = "\033[92m"     
    WARNING = "\033[93m"     
    FAIL = "\033[91m"     
    ENDC = "\033[0m"     
    BOLD = "\033[1m"     
    UNDERLINE = "\033[4m" 

def get_time_readable(sec):
    # create timedelta and convert it into string
    td_str = str(timedelta(seconds=sec))

    # split string into individual component
    x = td_str.split(':')
    time_str =  x[0] +  'h:' +  x[1] + 'm:' +  x[2] + ':s'
    return time_str



def get_time_readable_simple(sec):
    # create timedelta and convert it into string
    td_str = str(timedelta(seconds=sec))
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    if ((sec - seconds_since_midnight) < 570):
        time_str ="<"
        temp = str(timedelta(seconds=sec - seconds_since_midnight))
        x = temp.split(':')
        time_str += x[1] + "m" + x[2][:2]
    else:
    # split string into individual component
        x = td_str.split(':')
        time_str =  x[0] +  'h' +  x[1]
    return time_str



def send_get(url, headers={}, data={}):
    #print("Connecting to : ", url)
    reqToSend = requests.Request('GET',url, headers=headers)
    reqPrepared = reqToSend.prepare()
    #print("Message sent : ", reqPrepared)

    s = requests.Session()
    response = s.send(reqPrepared)
    return response



def request_stoptimes(stop_to_check):
    suffix = "routers/default/index/stops/"+str(stop_to_check)+"/stoptimes"
    full_url = API_BASE + suffix
    headers = {"origin": 'naught'}
    return send_get(full_url, headers)

def request_stops(bus_id):
    suffix = "routers/default/index/routes/"+bus_id+"/stops"
    full_url = API_BASE + suffix
    return send_get(full_url)


def request_stops_for_name(bus_id, name):
    json_response = request_stops(bus_id).json()
    stop_list = []
    for stop in json_response:
        if (stop["name"] == name or stop["clusterGtfsId"] == name):
            stop_list.append(stop)
    return stop_list



def print_stoptimes_simple(json_list):
    out_string = ""
    for bus_list in json_list:
        if bus_list["pattern"]:
            out_string += bus_list["pattern"]["shortDesc"][:8]
        if bus_list["times"]:
            out_string += ":["
            for i in range(0,min(2,len(bus_list["times"]))):
                 out_string += get_time_readable_simple(bus_list["times"][i]["realtimeArrival"])
                 out_string += ","
            out_string = out_string[:-1]
            out_string += "]"
    print(out_string)


def print_stoptimes(json_list):
    for bus_list in json_list:
        #print("bus_list",bus_list, end="\n\n")
        if bus_list["pattern"]:
            print("Bus en diréction de",bus_list["pattern"]["desc"], end="\n")
        if bus_list["times"]:
            for bus in bus_list["times"]:
                print("    Arrivée à : ", get_time_readable(bus["realtimeArrival"]))



def handle_response(response):
    try:
        json_response = response.json()
    except:
        print("[mTagPython] API is Broken")
        exit(0)
    return json_response

def print_json(json_object):
    json_prettyfied = json.dumps(json_object, indent=2)
    print("Prettyfied response", json_prettyfied, end="\n\n")



def print_stops(stops):
    temp_stop_name = ""
    last_name_found = False
    largest_name_size = 0
    first_list = []
    second_list = []
    for stop in stops:
        if stop["name"] == temp_stop_name:
            last_name_found = True
        
        temp_stop_name = stop["name"]
   
        if last_name_found:
            second_list.append(stop) 
        else :
            first_list.append(stop)
        
        if len(temp_stop_name) > largest_name_size:
            largest_name_size = len(temp_stop_name)

    print("Direction 1 :")
    for stop in first_list:
        print("    Stop",stop["name"],end=" ")
        for i in range(len(stop["name"]),largest_name_size):
            print(" ",end='')
        print("of id :",stop["gtfsId"])
    print("\nDirection 2 :")
    for stop in second_list:
        print("    Stop",stop["name"],end=" ")
        for i in range(len(stop["name"]),largest_name_size):
            print(" ",end='')
        print("of id :",stop["gtfsId"])


###
def print_custom(json_list, bus_times, to_work):
    out_string = ""
    for bus_list in json_list:
        if bus_list["pattern"]:
            if to_work:
                out_string += "To work"
            else:
                out_string += "To home"
            break;           
    
    out_string += ":["
    for i in range(0,min(2,len(bus_times))):
        out_string += get_time_readable_simple(bus_times[i])
        out_string += ","
    out_string = out_string[:-1]
    out_string += "]"
    return out_string


def get_bus_times(json_list):
    bus_times = []
    for bus_list in json_list:
        if bus_list["times"]:
            for i in range(0,min(2,len(bus_list["times"]))):
                bus_times.append(bus_list["times"][i]["realtimeArrival"])
    bus_times.sort()
    return bus_times



def print_to_home_from_work():
    stop_id_to_home = 'SEM:4527'  #ID OF INRIA STOP TOWARDS MY HOME STOP
    stop_id_to_INRIA = 'SEM:0393' #ID OF MY HOME STOP TOWARDS INRIA STOP
    final_str = ""

    response = request_stoptimes(stop_id_to_home)
    json_response = handle_response(response)
    bus_times_to_home = get_bus_times(json_response)
    #print(json_response)
    if(len(bus_times_to_home) != 0):
        final_str += print_custom(json_response, bus_times_to_home, False) + " - "
    else:
        final_str += "BROKEN_API_TO_HOME"
    response = request_stoptimes(stop_id_to_INRIA)
    json_response = handle_response(response)
    #print(json_response)

    bus_times_to_INRIA = get_bus_times(json_response)

    if(len(bus_times_to_INRIA) != 0):
        final_str += print_custom(json_response, bus_times_to_INRIA, True)
    else:
        final_str += "BROKEN_API_TO_HOME"
    return final_str
###

def main():
    if args.id:
        bus_id = NAME_BASE + args.id

    if args.custom:
        print(print_to_home_from_work()) # Yes, print(print)
    if (args.s and args.id):
        stop_id = NAME_BASE + args.s
        response = request_stoptimes(stop_id)
        json_response = handle_response(response)
        print_stoptimes(json_response)
    elif (args.id and args.l):
        response = request_stops(bus_id)
        json_response = handle_response(response)
        print_stops(json_response)
    elif (args.id and args.n):
        stop_name = args.n
        stops = request_stops_for_name(bus_id, stop_name)
        if (stops == []):
            print("The bus",bus_id,"does not stop at",stop_name,"or name is not spelled correctly (See the -l option)")
        for stop in stops:
            #print("Stop : ",stop)
            stop_id = stop["gtfsId"]
            print(stop)
            response = request_stoptimes(stop_id)
            json_response = handle_response(response)
            if(args.simple):
                print_stoptimes_simple(json_response)
            else:
                print_stoptimes(json_response)
            print("")
    else:
        exit(0)

if __name__ == "__main__":
    main()

