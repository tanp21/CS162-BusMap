import pyproj

src = pyproj.CRS.from_epsg(4326)
tar = pyproj.CRS.from_epsg(3405)
transformer = pyproj.Transformer.from_crs(src, tar, always_xy=True)

def latlng_to_xy(lat, lng):
    x, y = transformer.transform(lng, lat)
    return x, y




# import json
# from RouteVar import RouteVar, RouteVarQuery

# listRouteVar = []

# with open('vars.json', 'r', encoding='utf-8') as f:
#     for each_line in f:
#         dataList = json.loads(each_line)
#         for element in dataList:
#             listRouteVar.append(RouteVar(element))
            
# query = RouteVarQuery(dataList)
# query.outputAsCSV(listRouteVar)
# query.outputAsJSON(listRouteVar)


# import json
# from Stop import Stop, StopQuery

# listStops = set()

# with open('stops.json', 'r', encoding='utf-8') as f:
#     for line in f:
#         data = json.loads(line)
#         for stop_data in data['Stops']:
#             listStops.add(Stop(stop_data))
        
# listStops = list(listStops)
# query = StopQuery(listStops)
# query.outputAsCSV(query.searchByName("Nam Kỳ Khởi Nghĩa"))
# query.outputAsJSON(query.searchByName("Nam Kỳ Khởi Nghĩa"))

# from Path import Path, PathQuery

# query = PathQuery('paths.json')
# result = query.searchByRouteId(6)
# print(result)
# query.outputAsCSV(result, 'pathResult.csv')
# query.outputAsJSON(result, 'pathResult.json')

