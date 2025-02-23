import json

with open("draw.json", "w") as file_draw:
    to_draw = {"type": "FeatureCollection", "features": []}
    with open("paths.json", "r") as jsonfile:
        for line in jsonfile:
            path = []
            data = json.loads(line)
            lat = data['lat']
            lng = data['lng']
            for i in range(0, len(lat)):
                path.append([lng[i], lat[i]])
                
            tmp = {"type": "Feature", "geometry": {"type": "LineString", "coordinates" : path},
                   "properties": {"name": data['RouteId']}}
            to_draw['features'].append(tmp)
            
    json.dump(to_draw, file_draw)