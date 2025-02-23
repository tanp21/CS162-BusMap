import csv
import json

class RouteVar:
    def __init__(self, data):
        self.__RouteId = data["RouteId"]
        self.__RouteVarId = data["RouteVarId"]
        self.__RouteVarName = data["RouteVarName"]
        self.__RouteVarShortName = data["RouteVarShortName"]
        self.__RouteNo = data["RouteNo"]
        self.__StartStop = data["StartStop"]
        self.__EndStop = data["EndStop"]
        self.__Distance = data["Distance"]
        self.__Outbound = data["Outbound"]
        self.__RunningTime = data['RunningTime']
        
    def getAttribute(self, attribute_name):
        if attribute_name == 'RouteId':
            return self.__RouteId
        elif attribute_name == 'RouteVarId':
            return self.__RouteVarId
        elif attribute_name == 'RouteVarName':
            return self.__RouteVarName
        elif attribute_name == 'RouteVarShortName':
            return self.__RouteVarShortName
        elif attribute_name == 'RouteNo':
            return self.__RouteNo
        elif attribute_name == 'StartStop':
            return self.__StartStop
        elif attribute_name == 'EndStop':
            return self.__EndStop
        elif attribute_name == 'Distance':
            return self.__Distance
        elif attribute_name == 'Outbound':
            return self.__Outbound
        elif attribute_name == 'RunningTime':
            return self.__RunningTime
        
    def setAttribute(self, attribute_name, newData):
        if attribute_name == 'RouteId':
            self.__RouteId = newData
        elif attribute_name == 'RouteVarId':
            self.__RouteVarId = newData
        elif attribute_name == 'RouteVarName':
            self.__RouteVarName = newData
        elif attribute_name == 'RouteVarShortName':
            self.__RouteVarShortName = newData
        elif attribute_name == 'RouteNo':
            self.__RouteNo = newData
        elif attribute_name == 'StartStop':
            self.__StartStop = newData
        elif attribute_name == 'EndStop':
            self.__EndStop = newData
        elif attribute_name == 'Distance':
            self.__Distance = newData
        elif attribute_name == 'Outbound':
            self.__Outbound = newData
        elif attribute_name == 'RunningTime':
            self.__RunningTime = newData
        
        
class RouteVarQuery:
    
    def __init__(self, filejson):
        self.__listOfRouteVar = []
        with open(filejson, 'r', encoding='utf-8') as f:
            for each_line in f:
                dataList = json.loads(each_line)
                for element in dataList:
                    self.__listOfRouteVar.append(RouteVar(element))
            
    def searchByABC(self, attribute_name, needValue):
        resultList = []
        for element in self.__listOfRouteVar:
            if element.getAttribute(attribute_name) == needValue:
                resultList.append(element)
        return resultList
    
    def searchByMul(self, listAttribs, values):
        resultList = []
        for element in self.__listOfRouteVar:
            ok = True
            for i in range(0, len(listAttribs)):
                if element.getAttribute(listAttribs[i]) != values[i]:
                    ok = False
                    break
            if ok:
                resultList.append(element)
                
        return resultList
        
    def outputAsCSV(self, listData, outputFile):
        with open(outputFile,mode = 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            #write header row
            attrib = ["RouteId", "RouteVarId", "RouteVarName", "RouteVarShortName", "RouteNo", "StartStop", "EndStop", "Distance", "Outbound"]
            writer.writerow(attrib)
            
            for element in listData:
                writer.writerow([element.getAttribute(name) for name in attrib])
                
    def outputAsJSON(self, listData, outputFile):
        attrib = ["RouteId", "RouteVarId", "RouteVarName", "RouteVarShortName", "RouteNo", "StartStop", "EndStop", "Distance", "Outbound"]
        with open(outputFile, 'w', encoding='utf-8') as f:
            for element in listData:
                dic = {name : element.getAttribute(name) for name in attrib}
                json.dump(dic, f, ensure_ascii=False, indent=None)
                f.write('\n')
                
        