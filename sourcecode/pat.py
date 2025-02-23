import json
import geojson
import time
import mpu
import numpy as np
from sub_modules import dijkstra
from sub_modules import path_query
from sub_modules import path
from sub_modules import bin_file_handler
from rtree import index
from shapely.geometry import Point, Polygon, LineString
from sub_modules import cord_convert

class edge():
    def __init__(self, u, v, distance, time, idx_u, idx_v, pathId):
        self.u = u
        self.v = v
        self.distance = distance
        self.time = time
        self.startPathId = idx_u
        self.endPathId = idx_v
        self.pathId = pathId

def extractEdgesAndVertices(pathList, routeList, routeVarList):
    converter = cord_convert.converter()
    edges = []
    print(len(pathList), len(routeList), len(routeVarList))
    for i in range(len(pathList)):
        idx = index.Index()
        pointInLine = []
        runningTime = routeVarList[i].runningTime
        distance = routeVarList[i].distance
        if pathList[i].routeVarId != routeList[i].routeVarId or pathList[i].routeId != routeList[i].routeId:
            print("Error: routeVarId/routeId not match")
            return

        xs = []
        ys = []
        dist = [0]

        for j in range(len(pathList[i].lat)):
            x, y = converter.convert(pathList[i].lat[j], pathList[i].lng[j])
            xs.append(x)
            ys.append(y)
            pointInLine.append([x, y])
            idx.insert(j, (x, y, x, y))

            curDist = mpu.haversine_distance((pathList[i].lat[j], pathList[i].lng[j]), (pathList[i].lat[j-1], pathList[i].lng[j-1])) * 1000
            if curDist < 0:
                curDist = -curDist
                print("found negative dist")
            if j > 0:
                dist.append(dist[j-1] + curDist)

        lineString = LineString(pointInLine)

        idOfRtree = 0

        for j in range(1, len(routeList[i].stops)):
            u = routeList[i].stops[j-1]
            v = routeList[i].stops[j]
            xu, yu = converter.convert(u.lat, u.lng)
            xv, yv = converter.convert(v.lat, v.lng)

            # ls_u = idx.nearest((xu, yu, xu, yu), 1)

            idx_u = int(list(idx.nearest((xu, yu, xu, yu), 1))[0])
            idx_v = int(list(idx.nearest((xv, yv, xv, yv), 1))[0])


            if idx_u > idx_v:
                for x in list(idx.nearest((xv, yv, xv, yv), 5)):
                    if int(x) > idx_u:
                        idx_v = int(x)
                        break


            _dist = dist[idx_v] - dist[idx_u]
            time = _dist / distance * runningTime
            if (_dist < 0):
                print("found negative dist")

            edges.append(edge(u.stopId, v.stopId, _dist, time, idx_u, idx_v, i))
            # print([u.stopId, v.stopId, dist])

    return edges


def checkValidity(routeOfStops, paths):
    if (len(routeOfStops) != len(paths)):
        print("Error: routeOfStops and paths have different length")
        return False
    for i in range(len(routeOfStops)):

        # print(routeOfStops[i].routeVarId, routeOfStops[i].routeId, paths[i].routeVarId, paths[i].routeId)

        if routeOfStops[i].routeVarId != paths[i].routeVarId or routeOfStops[i].routeId != paths[i].routeId:
            print("Error: routeVarId/routeId not match")
            return False

    return True

def outputEdges(edges, filename):
    # write as csv

    with open(filename, "w") as file:
        file.write("u,v,distance,time,startPathId,endPathId,pathId\n")
        for edge in edges:
            file.write(str(edge.u) + "," + str(edge.v) + "," + str(edge.distance) + "," + str(edge.time) + "," +  str(edge.startPathId) + "," +  str(edge.endPathId) + "," + str(edge.pathId) + "\n")
        file.close()

def extractVertices(edges):
    nodes = []
    for edge in edges:
        nodes.append(edge.u)
        nodes.append(edge.v)
    nodes.sort()
    nodes = list(set(nodes))
    with open("../data/nodes.csv", "w") as file:
        file.write("id\n")
        for node in nodes:
            file.write(str(node) + "\n")
        file.close()
    return nodes

def findIndex(nodes, x):
    l = 0
    r = len(nodes) - 1
    while l <= r:
        mid = (l + r) // 2
        if nodes[mid] == x:
            return mid
        elif nodes[mid] < x:
            l = mid + 1
        else:
            r = mid - 1
    return -1

class graph():
    def __init__(self, stops, routeOfStops, paths, routeVars): # stops: list, routeOfStops: list
        self.edges = []
        self.num_edges = 0
        self.num_nodes = 0
        self.nodes = []
        self.labels = []
        self.adjList = []
        self.traceList = []
        self.stops = stops
        self.usefullness = []
        self.rank = []

        self.shortestPathProcessed = False

        if not checkValidity(routeOfStops, paths):
            return
        else:
            print("Data is valid")

        self.edges = extractEdgesAndVertices(paths, routeOfStops, routeVars)
        self.num_edges = len(self.edges)
        # print(self.edges[0].u, self.edges[0].v, self.edges[0].distance, self.edges[0].time, self.edges[0].startPathId, self.edges[0].endPathId, self.edges[0].routeId, self.edges[0].routeVarId)
        outputEdges(self.edges, "../data/edges.csv")
        print("output to edges.csv")

        self.nodes = extractVertices(self.edges)
        self.stops.sort(key=lambda x: x.stopId)

        self.adjList = [[] for i in range(len(self.nodes))]
        self.traceList = [[] for i in range(len(self.nodes))]
        self.labels = [0 for i in range(len(self.nodes))]
        self.usefullness = [0 for i in range(len(self.nodes))]

        print(len(self.nodes))
        print(len(self.stops))

        for i in range(len(self.nodes)):
            if (self.stops[i].stopId != self.nodes[i]):
                print("Error: stops not match", self.stops[i].stopId, self.nodes[i])
                return

        for i in range(len(self.edges)): # reassigned the id of the nodes
            edge = self.edges[i]
            id_u = findIndex(self.nodes, edge.u)
            id_v = findIndex(self.nodes, edge.v)

            self.labels[id_u] = edge.u
            self.labels[id_v] = edge.v

            edge.u = id_u
            edge.v = id_v

            # print(id_u, id_v, edge[3])

            self.adjList[id_u].append([id_v, edge.time])
            self.traceList[id_v].append([id_u, edge.time, i])

        print(len(self.edges))

    def shortestPathAllPairs(self, dest):
        start_time = time.time()
        print("Calculating with dijkstra, please wait....")

        with open(dest, "wb") as file:
            n = len(self.nodes)

            # write the number of node to the beginning of the file - 4 bytes
            bin_file_handler.writeInt(n, file)

            for i in range(n):
                f = dijkstra.dijkstra(self.adjList, i)
                # write list to bin file - each is 8 bytes
                # dijkstra.calc_rank(i, self.adjList, f, self.usefullness)
                bin_file_handler.writeFloat(f, file)

            file.close()

            print("file written at " + dest)
        end_time = time.time()

        print(f"Caculate all pair: {end_time-start_time}")

    def calcRank(self, dest):

        if self.shortestPathProcessed == True:
            print("Rank already processed")
            return False

        print("Calculating with rank shortest path DAG, please wait....")
        start_time = time.time()
        file = open(dest, "rb")
        if file is None:
            print("Error: file not found")
            return False

        n = bin_file_handler.readIntFrom(file, 0, 1)[0]
        for i in range(n):
            f = bin_file_handler.readFloatFrom(file, 4 + 8 * i * n, n)
            dijkstra.calc_rank(i, self.adjList, f, self.usefullness)

        for i in range(len(self.nodes)):
            if (self.stops[i].stopId == self.nodes[i]):
                self.rank.append([self.stops[i], self.usefullness[i]])
            else:
                print("Error: stops not match")
                return False

        self.rank.sort(key=lambda x: x[1], reverse=True)

        end_time = time.time()
        print(f"Time to calculate rank: {end_time-start_time}")

        return True

    def getTime(self, u, v, dest):

        u = findIndex(self.nodes, u)
        v = findIndex(self.nodes, v)
        with open(dest, "rb") as file:
            n = bin_file_handler.readIntFrom(file, 0, 1)
            if len(n) == 0 or n[0] != len(self.nodes):
                print("Error: number of nodes not match")
                return None

            f = bin_file_handler.readFloatFrom(file, 4 + 8 * (u * n[0] + v), 1)
            file.close()
            return f[0]

    def getShortestPathFrom(self, u, dest):
        u = findIndex(self.nodes, u)
        with open(dest, "rb") as file:
            n = bin_file_handler.readIntFrom(file, 0, 1)
            if len(n) == 0 or n[0] != len(self.nodes):
                print("Error: number of nodes not match")
                return None

            f = bin_file_handler.readFloatFrom(file, 4 + 8 * u * n[0], n[0])
            file.close()
            return f

    def getTrace(self, st, en, destFile, outFileName, pathList):
        u = findIndex(self.nodes, st)
        v = findIndex(self.nodes, en)

        paths = []

        with open(destFile, "rb") as file:
            n = bin_file_handler.readIntFrom(file, 0, 1)
            if len(n) == 0 or n[0] != len(self.nodes):
                print("Error: number of nodes not match")
                return None

            f = bin_file_handler.readFloatFrom(file, 4 + 8 * u * n[0], n[0])
            file.close()
            paths = dijkstra.trace(self.traceList, u, v, f)

        with open(outFileName + ".geojson", "w") as file:
            lineWithColor = []
            color = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF", "#C0C0C0", "#808080", "#800000", "#808000", "#008000", "#800080", "#008080", "#000080", "#FFA07A", "#20B2AA", "#FF6347", "#FF4500", "#FFD700", "#FF8C00", "#FF1493", "#FF00FF", "#FF69B4", "#FFB6C1", "#FFA07A", "#FFA500", "#FFD700", "#FF8C00", "#FF1493", "#FF00FF", "#FF69B4", "#FFB6C1", "#FFA07A", "#FFA500", "#FFD700", "#FF8C00", "#FF1493", "#FF00FF", "#FF69B4", "#FFB6C1", "#FFA07A", "#FFA500", "#FFD700", "#FF8C00", "#FF1493", "#FF00FF", "#FF69B4", "#FFB6C1", "#FFA07A", "#FFA500", "#FFD700", "#FF8C00", "#FF1493", "#FF00FF", "#FF69B4", "#FFB6C1", "#FFA07A", "#FFA500", "#FFD700", "#FF8C00", "#FF1493", "#FF00FF", "#FF69B4", "#FFB6C1", "#FFA07A", "#FFA500", "#FFD700", "#FF8C00", "#FF1493", "#FF00FF", "#FF69B4", "#FFB6C1", "#FFA07A", "#FFA500", "#FFD700", "#FF8C00", "#FF1493", "#FF00FF", "#FF69B4", "#FFB6C1", "#FFA07A", "#FFA500", "#FFD700", "#FF8C00", "#FF1493", "#FF00FF", "#FF69B4", "#FFB6C1", "#FFA07A", "#FFA500", "#FFD700"]

            lineWithColor.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        self.stops[u].lat,
                        self.stops[u].lng
                    ]
                },
                "properties": {}
            })

            for i in paths:
                startPathId = self.edges[i].startPathId
                endPathId = self.edges[i].endPathId
                pathId = self.edges[i].pathId

                for j in range(startPathId, endPathId):

                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [
                                [pathList[pathId].lng[j], pathList[pathId].lat[j]],
                                [pathList[pathId].lng[j+1], pathList[pathId].lat[j+1]]
                            ]
                        },
                        "properties": {
                            "stroke": color[pathId % len(color)],
                            "stroke-width": 2
                        }
                    }

                    lineWithColor.append(feature)


            lineWithColor.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        self.stops[v].lat,
                        self.stops[v].lng
                    ]
                },
                "properties": {
                    "marker-color": "#FF0000",
                    "marker-size": "medium",
                    "marker-symbol": "circle"
                }
            })

            feature_collection = {
                "type": "FeatureCollection",
                "features": lineWithColor
            }

            json.dump(feature_collection, file)
            file.close()
        print("output to " + outFileName + ".geojson")
