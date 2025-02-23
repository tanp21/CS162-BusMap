from shapely import Point, LineString, LinearRing
from RouteVar import RouteVar, RouteVarQuery
from Stop import Stop, StopQuery, StopRouteQuery
from Path import Path, PathQuery 
from changeCoord import latlng_to_xy
from geojson_generator import pathsGenerator, GeojsonContainer, geojsonLineStr
import json

# used to print the path with specific color to GeoJSON
colorPalette = ['#FF204E', '#A0153E', '#5D0E41', '#00224D'] 
stopRouteQueryInfo = StopRouteQuery('stops.json')
stopQueryInfo = StopQuery('stops.json')
routeVarQueryInfo = RouteVarQuery('vars.json')
stopQueryData = StopQuery("stops.json")

geojsonObj = GeojsonContainer()

adj = {} # adjacency list



with open('graph.json', 'r') as json_file:
    adj = json.load(json_file)
    
new_adj = {}
for key, value in adj.items():
    new_adj[int(key)] = value
adj = new_adj

# LLM

import requests

# define list of functions and their informations
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stopid",
            "description": "Get the infomation from a stop with a provided ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "stopid": {
                        "type": "int",
                        "description": "The ID of the stop that the user want to get the information",
                    },
                },
                "required": ["stopid"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stopname",
            "description": "Get the infomation from a stop with a provided Name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The Name of the stop that the user want to get the information",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_route",
            "description": "Get all the stops name that a particular bus pass through, based on their RouteId and RouteVarId",
            "parameters": {
                "type": "object",
                "properties": {
                    "RouteId": {
                        "type": "int",
                        "description": "The RouteId of the bus that the user want to get the information",
                    },
                    "RouteVarId": {
                        "type": "int",
                        "description": "The RouteVarId of the bus that the user want to get the information",
                    },
                },
                "required": ["RouteId", "RouteVarId"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_shortest",
            "description": "Get the fastest time for user to travel from source stop to destination stop",
            "parameters": {
                "type": "object",
                "properties": {
                    "srcName": {
                        "type": "string",
                        "description": "The name of the stop that user is currently at or want to travel from",
                    },
                    "desName": {
                        "type": "string",
                        "description": "The name of the stop that user wish to travel to",
                    },
                },
                "required": ["srcName", "desName"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top",
            "description": "Get K most important stops, here importance of the stops means that the number of shortest paths that must pass through this stop",
            "parameters": {
                "type": "object",
                "properties": {
                    "K": {
                        "type": "int",
                        "description": "The number of most important stops that the user want to get",
                    },
                },
                "required": ["K"],
            },
        },
    }
]

# Schema is to ensure LLMs return with the specified key names.
schema = {
    "function_name": {
        "type": "string",
        "description": "the function that should be used based on the provided information is either ID or Code",
        "enums": ["get_stopid", "get_stopname", "get_route", "get_shortest", "get_top"]
    },
    "stopid": {
        "type": "int",
        "description": "The ID of the stop, if no stop ID is provided the value of code will be -1"
    },
    "name": {
        "type": "string",
        "description": "The name of the stop, empty string if name is not provided"
    },
    "RouteId": {
        "type": "string",
        "description": "The RouteId of the bus that the user want to get the information, which is a number but take as a string, -1 if not provided",
    },
    "RouteVarId": {
        "type": "string",
        "description": "The RouteVarId of the bus that the user want to get the information, which is a number but take as a string, -1 if not provided",
    },
    "srcName": {
        "type": "string",
        "description": "The name of the stop that user is currently at or want to travel from, empty string if not provided",
    },
    "desName": {
        "type": "string",
        "description": "The name of the stop that user wish to travel to, empty string if not provided",
    },
    "K": {
        "type": "int",
        "description": "The number of most important stops that the user want to get, -1 if not provided",
    },
}

# Take user's prompt
prompt = input("Please enter a prompt:\n")

# model information and prompts, examples
payload = {
    "model": "mistral",
    "messages": [
        {
            "role": "system",
            "content": f"You are a helpful AI assistant. The user will enter a request which is to retrieve information from a bus stop. You need to decide which function must be used to extract information based on whether the user specified the ID or the Code. Then you extract the parameters to pass into the function. The informations about the functions are {tools}. Output as JSON file follows the following schema: {schema}"
        },
        {
            "role": "user",
            "content": "Tell me the information about the stop with ID 35"
        },
        {
            "role": "assistant",
            "content": "{\"function_name\": \"get_stopid\", \"stopid\": 35, \"name\": \"\", \"RouteId\": -1, \"RouteVarId\": -1, \"srcName\": \"\", \"desName\": \"\", \"K\": \"-1\"}"
        },
        {
            "role": "user",
            "content": "Please provide the information about the stop named Công Trường Mê Linh"
        },
        {
            "role": "assistant",
            "content": "{\"function_name\": \"get_stopname\", \"stopid\": -1, \"name\": \"Công Trường Mê Linh\", \"RouteId\": -1, \"RouteVarId\": -1, \"srcName\": \"\", \"desName\": \"\", \"K\": \"-1\"}"
        },
        {
            "role": "user",
            "content": "Can you give me the stops which is passed by the bus which have routeid 3 and routevarid 5"
        },
        {
            "role": "assistant",
            "content": "{\"function_name\": \"get_route\", \"stopid\": -1, \"name\": \"\", \"RouteId\": 3, \"RouteVarId\": 5, \"srcName\": \"\", \"desName\": \"\", \"K\": \"-1\"}"
        },
        {
            "role": "user",
            "content": "What is the least time required to travel from Bệnh Viện 175 to Công an Quận Phú Nhuận"
        },
        {
            "role": "assistant",
            "content": "{\"function_name\": \"get_shortest\", \"stopid\": -1, \"name\": \"\", \"RouteId\": -1, \"RouteVarId\": -1, \"srcName\": \"Bệnh Viện 175\", \"desName\": \"Công an Quận Phú Nhuận\", \"K\": \"-1\"}"
        },
        {
            "role": "user",
            "content": "List out 6 stops which is passed by the most shortest paths of the buses"
        },
        {
            "role": "assistant",
            "content": "{\"function_name\": \"get_top\", \"stopid\": -1, \"name\": \"\", \"RouteId\": -1, \"RouteVarId\": -1, \"srcName\": \"\", \"desName\": \"\", \"K\": \"6\"}"
        },
        {
            "role": "user",
            "content": prompt
        },
        
    ],
    "format": "json",
    "stream": False
}

response = requests.post("http://localhost:11434/api/chat", json=payload)
resp = json.loads(response.json()["message"]["content"])

from graphModule import Dijkstra

shortestPath = Dijkstra(adj)

for i in adj.keys():
    shortestPath.oneSource(i, metric=True)
    
def get_stopid(stopid):
    needStop = stopQueryData.searchByABC('StopId', stopid)
    if len(needStop) == 0:
        print("No stop found.")
        return
    needStop = needStop[0]
    attrib = ["StopId", "Code", "Name", "StopType", "Zone", "Ward", "AddressNo", "Street", "SupportDisability", "Status", "Lng", "Lat", "Search", "Routes"]
    ans = {attrib[i]: needStop.getAttribute(attrib[i]) for i in range(len(attrib))}
    for key, value in ans.items():
        print(f"{key}: {value}")

def get_stopname(name):
    needStop = stopQueryData.searchByABC('Name', name)
    if len(needStop) == 0:
        print("No stop found.")
        return
    needStop = needStop[0]
    attrib = ["StopId", "Code", "Name", "StopType", "Zone", "Ward", "AddressNo", "Street", "SupportDisability", "Status", "Lng", "Lat", "Search", "Routes"]
    ans = {attrib[i]: needStop.getAttribute(attrib[i]) for i in range(len(attrib))}
    for key, value in ans.items():
        print(f"{key}: {value}")
        
def get_route(routeid, routevarid):
    needRoute = stopRouteQueryInfo.searchByMul(['RouteId', 'RouteVarId'], [routeid, routevarid])
    if len(needRoute) == 0:
        print("No route found.")
        return
    print(len(needRoute))
    needRoute = needRoute[0]
    print("The stops which are passed by this bus is:")
    for stop in needRoute['Stops']:
        print(stop['Name'])
        
def get_shortest(name1, name2):
    src = stopQueryData.searchByABC('Name', name1)
    des = stopQueryData.searchByABC('Name', name2)
    if len(src) == 0 or len(des) == 0:
        print("Error")
        return
    src = src[0].getAttribute('StopId')
    des = des[0].getAttribute('StopId')
    print(f"The shortest time is: {shortestPath.getTime(src, des)}")
    
def get_top(k):
    res = shortestPath.queryTopK(k)
    for i in range(0, len(res)):
        print(f"Top {i + 1}: StopID = {res[i][1]}")
        
if resp['function_name'] == 'get_stopid':
    get_stopid(resp['stopid'])
elif resp['function_name'] == 'get_stopname':
    get_stopname(resp['name'])
elif resp['function_name'] == 'get_route':
    get_route(resp['RouteId'], resp['RouteVarId'])
elif resp['function_name'] == 'get_shortest':
    get_shortest(resp['srcName'], resp['desName'])
elif resp['function_name'] == 'get_top':
    get_top(resp['K'])

