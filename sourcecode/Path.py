import json
import csv

class Path:
    def __init__(self, data):
        self.__lat = data['lat']
        self.__lng = data['lng']
        self.__RouteId = int(data['RouteId'])
        self.__RouteVarId = int(data['RouteVarId'])
        
    def getAttribute(self, attribute_name):
        if attribute_name == 'lat':
            return self.__lat
        elif attribute_name == 'lng':
            return self.__lng
        elif attribute_name == 'RouteId':
            return self.__RouteId
        elif attribute_name == 'RouteVarId':
            return self.__RouteVarId
        
    def setAttribute(self, attribute_name, newData):
        if attribute_name == 'lat':
            self.__lat = newData
        elif attribute_name == 'lng':
            self.__lng = newData
        elif attribute_name == 'RouteId':
            self.__RouteId = newData
        elif attribute_name == 'RouteVarId':
            self.__RouteVarId = newData
        
class PathQuery:
    def __init__(self, filejson):
        import json
        self.__listOfPaths = []
        with open(filejson, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                self.__listOfPaths.append(Path(data))
                
    def searchByABC(self, attribute_name, needValue):
        resultList = []
        for element in self.__listOfPaths:
            if element.getAttribute(attribute_name) == needValue:
                resultList.append(element)
        return resultList
    
    def searchByMul(self, listAttribs, values):
        resultList = []
        for element in self.__listOfPaths:
            ok = True
            for i in range(0, len(listAttribs)):
                if element.getAttribute(listAttribs[i]) != values[i]:
                    ok = False
                    break
            if ok:
                resultList.append(element)
                
        return resultList
    
    def outputAsCSV(self, listData, outputFile):
        with open(outputFile, mode = 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            attrib = ["lat", "lng", "RouteId", "RouteVarId"]
            #write header row
            writer.writerow(attrib)
            
            for element in listData:
                to_write = [element.getAttribute(name) for name in attrib]
                writer.writerow(to_write)
                
    def outputAsJSON(self, listData, outputFile):
        attrib = ["lat", "lng", "RouteId", "RouteVarId"]
                
        with open(outputFile, 'w', encoding='utf-8') as f:
            for element in listData:
                dic = {name : element.getAttribute(name) for name in attrib}
                json.dump(dic, f, ensure_ascii=False, indent=None)
                f.write('\n')
        

        