import json
# from RouteVar import RouteVarQuery

def geojsonLineStr(listLat, listLng):
    return [(listLng[i], listLat[i]) for i in range(len(listLat))]

class GeojsonObject:
    def __init__(self, _name, objType, coords, color):
        self.__name = _name
        self.__type = objType
        self.__listCoords = coords
        self.__color = color
        
    def getObj(self):
        ans = {
            "type": "Feature",
            "geometry": {
                "type": self.__type,
                "coordinates": self.__listCoords
            },
            "properties": {
                "name": self.__name,
                "marker-color" : self.__color
            }
        }
        if self.__type != 'Point' and self.__type != 'MultiPoint':
            ans['properties']['stroke'] = self.__color
        return ans
    
class GeojsonContainer:
    def __init__(self):
        self.__geojsonData = {
            "type" : "FeatureCollection",
            "features": []
        }
    
    def addPath(self, name, lineStr, color): # yay vector
        tmp = GeojsonObject(name, 'LineString', lineStr, color)
        self.__geojsonData['features'].append(tmp.getObj())
        
    def addPoints(self, name, coord, color):
        tmp = GeojsonObject(name, 'MultiPoint', coord, color)
        self.__geojsonData['features'].append(tmp.getObj())
        
    def addPoint(self, name, coord, color):
        tmp = GeojsonObject(name, 'Point', coord, color)
        self.__geojsonData['features'].append(tmp.getObj())
        
    def outputJSON(self, fileName):
        with open(fileName, 'w') as file_out:
            json.dump(self.__geojsonData, file_out)
    

def convertCoords(listLng, listLat):
    ans = []
    for i in range(0, len(listLng)):
        ans.append([listLng[i], listLat[i]])
    return ans

def pathsGenerator(listPaths):
    geojsonData = {
        "type" : "FeatureCollection", 
        "features": []
    }
    for path in listPaths:
        jsonPath = GeojsonObject(_name=path["Name"],
                                 objType="LineString",
                                 coords = convertCoords(path["lng"], path["lat"]))
        geojsonData["features"].append(jsonPath.getObj())
    
    with open('geojsonFile.json', 'w') as file_out:
        json.dump(geojsonData, file_out)
        
        
if __name__ == "__main__":
    from RouteVar import RouteVarQuery
    listPaths = []
    routeQuery = RouteVarQuery('vars.json')
    with open('paths.json', 'r', encoding='utf-8') as file_in:
        for line in file_in:
            pathData = json.loads(line)
            resQuery = routeQuery.searchByMul(['RouteId', 'RouteVarId'], 
                                                      [int(pathData['RouteId']), int(pathData['RouteVarId'])])
            # resQuery = routeQuery.searchByMul(['RouteId', 'RouteVarId'], 
            #                                           [3, 5])
            # print(resQuery)
            pathData['Name'] = resQuery[0].getAttribute('RouteVarName')
            listPaths.append(pathData)
            break
            
        pathsGenerator(listPaths)
            
        