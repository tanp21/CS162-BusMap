import csv
import json

class Stop:
    def __init__(self, dataStop):
        self.__StopId = dataStop['StopId']
        self.__Code = dataStop['Code']
        self.__Name = dataStop['Name']
        self.__StopType = dataStop['StopType']
        self.__Zone = dataStop['Zone']
        self.__Ward = dataStop['Ward']
        self.__AddressNo = dataStop['AddressNo']
        self.__Street = dataStop['Street']
        self.__SupportDisability = dataStop['SupportDisability']
        self.__Status = dataStop['Status']
        self.__Lng = dataStop['Lng']
        self.__Lat = dataStop['Lat']
        self.__Search = dataStop['Search']
        self.__Routes = dataStop['Routes']
        
    def getAttribute(self, attribute_name):
        if attribute_name == 'StopId':
            return self.__StopId
        elif attribute_name == 'Code':
            return self.__Code
        elif attribute_name == 'Name':
            return self.__Name
        elif attribute_name == 'StopType':
            return self.__StopType
        elif attribute_name == 'Ward':
            return self.__Ward
        elif attribute_name == 'AddressNo':
            return self.__AddressNo
        elif attribute_name == 'Street':
            return self.__Street
        elif attribute_name == 'SupportDisability':
            return self.__SupportDisability
        elif attribute_name == 'Status':
            return self.__Status
        elif attribute_name == 'Lng':
            return self.__Lng
        elif attribute_name == 'Lat':
            return self.__Lat
        elif attribute_name == 'Search':
            return self.__Search
        elif attribute_name == 'Routes':
            return self.__Routes
        
    def setAttribute(self, attribute_name, newData):
        if attribute_name == 'StopId':
            self.__StopId = newData
        elif attribute_name == 'Code':
            self.__Code = newData
        elif attribute_name == 'Name':
            self.__Name = newData
        elif attribute_name == 'StopType':
            self.__StopType = newData
        elif attribute_name == 'Ward':
            self.__Ward = newData
        elif attribute_name == 'AddressNo':
            self.__AddressNo = newData
        elif attribute_name == 'Street':
            self.__Street = newData
        elif attribute_name == 'SupportDisability':
            self.__SupportDisability = newData
        elif attribute_name == 'Status':
            self.__Status = newData
        elif attribute_name == 'Lng':
            self.__Lng = newData
        elif attribute_name == 'Lat':
            self.__Lat = newData
        elif attribute_name == 'Search':
            self.__Search = newData
        elif attribute_name == 'Routes':
            self.__Routes = newData
        
class StopQuery:
    def __init__(self, filejson):
        data = []
        with open('stops.json', 'r', encoding='utf-8') as f:
            for line in f:
                dataDic = json.loads(line)
                for stop_data in dataDic['Stops']:
                    data.append(Stop(stop_data))
        used_id = set()
        self.__listOfStops = []
        for stop_data in data:
            if stop_data.getAttribute('StopId') not in used_id:
                self.__listOfStops.append(stop_data)
                used_id.add(stop_data.getAttribute('StopId'))
        
    def searchByABC(self, attribute_name, needValue):
        resultList = []
        for element in self.__listOfStops:
            if element.getAttribute(attribute_name) == needValue:
                resultList.append(element)
        return resultList
    
    def searchByMul(self, listAttribs, values):
        resultList = []
        for element in self.__listOfStops:
            ok = True
            for i in range(0, len(listAttribs)):
                if element.getAttribute(listAttribs[i]) != values[i]:
                    ok = False
                    break
            if ok:
                resultList.append(element)
                
        return resultList
    
    def getSize(self):
        return len(self.__listOfStops)

    def outputAsCSV(self, listData, outputFile):
        with open(outputFile, mode = 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            attrib = ["StopId", "Code", "Name", "StopType", "Zone", "Ward", "AddressNo", 
                             "Street", "SupportDisability", "Status", "Lng", "Lat", 
                             "Search", "Routes"]
            #write header row
            writer.writerow(attrib)
            
            for element in listData:
                to_write = [element.getAttribute(name) for name in attrib]
                writer.writerow(to_write)
                
    def outputAsJSON(self, listData, outputFile):
        attrib = ["StopId", "Code", "Name", "StopType", "Zone", "Ward", "AddressNo", 
                             "Street", "SupportDisability", "Status", "Lng", "Lat", 
                             "Search", "Routes"]
                
        with open(outputFile, 'w', encoding='utf-8') as f:
            for element in listData:
                dic = {name : element.getAttribute(name) for name in attrib}
                json.dump(dic, f, ensure_ascii=False, indent=None)
                f.write('\n')
                
class StopRouteQuery:
    def __init__(self, filejson):
        self.__data = []
        with open('stops.json', 'r', encoding='utf-8') as f:
            for line in f:
                dataDic = json.loads(line)
                dataDic['RouteId'] = int(dataDic['RouteId'])
                dataDic['RouteVarId'] = int(dataDic['RouteVarId'])
                self.__data.append(dataDic)
        
    def searchByABC(self, attribute_name, needValue):
        resultList = []
        for element in self.__data:
            if element[attribute_name] == needValue:
                resultList.append(element)
        return resultList
    
    def searchByMul(self, listAttribs, values):
        resultList = []
        for element in self.__data:
            ok = True
            for i in range(0, len(listAttribs)):
                if element[listAttribs[i]] != values[i]:
                    ok = False
                    break
            if ok:
                resultList.append(element)
                
        return resultList
    
    def getSize(self):
        return len(self.__listOfStops)