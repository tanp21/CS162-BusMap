import heapq
import queue

class Dijkstra:
    def __init__(self, adj):
        self.__adj = adj
        self.__imp = {v : 0 for v in adj.keys()}
        self.__dist = {v : {} for v in adj.keys()}
        self.__prev = {v : {} for v in adj.keys()}
            
        
    def oneSource(self, src, metric):
        self.__dist[src][src] = 0
        pq = [(0, src)]
        
        vis = {}
        
        while pq:
            d, u = heapq.heappop(pq)
            if(d > self.__dist[src][u]):
                continue
            
            vis[u] = 1
            
            for edgeInfo in self.__adj[u]['adj']:
                v = edgeInfo['vertex']
                w = edgeInfo['time']
                chosenRoute = edgeInfo['route']
                routeid = edgeInfo['routeid']
                if (v not in self.__dist[src]) or self.__dist[src][u] + w < self.__dist[src][v]:
                    self.__dist[src][v] = self.__dist[src][u] + w
                    prevInfo = {
                        'prev_vertex' : u,
                        'route' : chosenRoute,
                        'routeid' : routeid
                    }
                    self.__prev[src][v] = prevInfo
                    heapq.heappush(pq, (self.__dist[src][v], v))
                    
        if not metric:
            return
        
        indeg = {v : 0 for v in vis}
        treeAdj = {v : [] for v in vis}
                    
        for u in vis.keys():
            for edgeInfo in self.__adj[u]['adj']:
                v = edgeInfo['vertex']
                w = edgeInfo['time']
                if self.__dist[src][u] + w == self.__dist[src][v]:
                    treeAdj[v].append(u)
                    indeg[u] += 1
                    
        dp = {u : 1 for u in vis}
            
        q = queue.Queue()
        for i in vis:
            if indeg[i] == 0:
                q.put(i)
        
        while not q.empty():
            u = q.get()
            for v in treeAdj[u]:
                indeg[v] -= 1
                dp[v] += dp[u]
                if indeg[v] == 0:
                    q.put(v)
                    
        for i in vis:
            self.__imp[i] += dp[i]
                    
    def tracePath(self, u, v):
        resultList = []
        while v != u:
            dicStop = {
                'type': 'stop',
                'stopid': v
            }
            resultList.append(dicStop)
            dicPath = {
                'type': 'path',
                'route': self.__prev[u][v]['route'],
                'routeid': self.__prev[u][v]['routeid']
            }
            resultList.append(dicPath)
            v = self.__prev[u][v]['prev_vertex']
        dicStop = {
            'type': 'stop',
            'stopid': u
        }
        resultList.append(dicStop)
        resultList.reverse()
        return resultList
        
    def queryTopK(self, k = 10):
        resultList = []
        tmpList = []
        for i in self.__adj.keys():
            tmpList.append((self.__imp[i], i))
        tmpList.sort()
        tmpList.reverse()
        for i in range(min(k, len(tmpList))):
            resultList.append((tmpList[i][0], tmpList[i][1]))
        return resultList
    
    def getTime(self, u, v):
        if v not in self.__dist[u]:
            return -1
        return self.__dist[u][v]
    
    def getAllPairs(self):
        result = []
        for u in self.__dist:
            for v, dis in self.__dist[u].items():
                result.append((u, v, dis))
        return result
    
    
class SPFA:
    def __init__(self, adj):
        self.__adj = adj
        self.__imp = {v : 0 for v in adj.keys()}
        self.__dist = {v : {} for v in adj.keys()}
        self.__prev = {v : {} for v in adj.keys()}
        self.__inqueue = {u : {v : False for v in adj[u].keys()} for u in adj.keys()}    
        
    def oneSource(self, src, metric):
        self.__dist[src][src] = 0
        q = []
        q.append(src)
        self.__inqueue[src][src] = True
        
        while len(q):
            u = q.pop(0)
            self.__inqueue[src][u] = False
            
            for edgeInfo in self.__adj[u]['adj']:
                v = edgeInfo['vertex']
                w = edgeInfo['time']
                chosenRoute = edgeInfo['route']
                routeid = edgeInfo['routeid']
                if (v not in self.__dist[src]) or self.__dist[src][u] + w < self.__dist[src][v]:
                    self.__dist[src][v] = self.__dist[src][u] + w
                    prevInfo = {
                        'prev_vertex' : u,
                        'route' : chosenRoute,
                        'routeid' : routeid
                    }
                    self.__prev[src][v] = prevInfo
                    if (v not in self.__inqueue[src]) or (not self.__inqueue[src][v]):
                        q.append(v)
                        self.__inqueue[src][v] = True
                    # heapq.heappush(pq, (self.__dist[src][v], v))
        if not metric:
            return
        
        vis = {}
        
        indeg = {v : 0 for v in vis}
        treeAdj = {v : [] for v in vis}
                    
        for u in vis.keys():
            for edgeInfo in self.__adj[u]['adj']:
                v = edgeInfo['vertex']
                w = edgeInfo['time']
                if self.__dist[src][u] + w == self.__dist[src][v]:
                    treeAdj[v].append(u)
                    indeg[u] += 1
                    
        dp = {u : 1 for u in vis}
            
        q = queue.Queue()
        for i in vis:
            if indeg[i] == 0:
                q.put(i)
        
        while not q.empty():
            u = q.get()
            for v in treeAdj[u]:
                indeg[v] -= 1
                dp[v] += dp[u]
                if indeg[v] == 0:
                    q.put(v)
                    
        for i in vis:
            self.__imp[i] += dp[i]
                    
    def tracePath(self, u, v):
        resultList = []
        while v != u:
            dicStop = {
                'type': 'stop',
                'stopid': v
            }
            resultList.append(dicStop)
            dicPath = {
                'type': 'path',
                'route': self.__prev[u][v]['route'],
                'routeid': self.__prev[u][v]['routeid']
            }
            resultList.append(dicPath)
            v = self.__prev[u][v]['prev_vertex']
        dicStop = {
            'type': 'stop',
            'stopid': u
        }
        resultList.append(dicStop)
        resultList.reverse()
        return resultList
        
    def queryTopK(self, k = 10):
        resultList = []
        tmpList = []
        for i in self.__adj.keys():
            tmpList.append((self.__imp[i], i))
        tmpList.sort()
        tmpList.reverse()
        for i in range(min(k, len(tmpList))):
            resultList.append((tmpList[i][0], tmpList[i][1]))
        return resultList
    
    def getTime(self, u, v):
        if v not in self.__dist[u]:
            return -1
        return self.__dist[u][v]
    
    def getAllPairs(self):
        result = []
        for u in self.__dist:
            for v, dis in self.__dist[u].items():
                result.append((u, v, dis))
        return result
    
class FloydWarshall:
    def __init__(self, adj):
        self.__adj = adj
        self.__imp = {v : 0 for v in adj.keys()}
        self.__dist = {v : {} for v in adj.keys()}
        self.__prev = {v : {} for v in adj.keys()}
        self.__inqueue = {u : {v : False for v in adj[u].keys()} for u in adj.keys()}    
        
    def allPair(self, metric):
        for i in self.__adj.keys():
            for edgeInfo in self.__adj[i]['adj']:
                j = edgeInfo['vertex']
                w = edgeInfo['time']
                self.__dist[i][j] = w
                
        for k in self.__adj.keys():
            for i in self.__adj.keys():
                if k in self.__dist[i]:
                    for j in self.__dist[k].keys():
                        if j not in self.__dist[i]:
                            self.__dist[i][j] = self.__dist[i][k] + self.__dist[k][j]
                        else:
                            self.__dist[i][j] = min(self.__dist[i][j], self.__dist[i][k] + self.__dist[k][j])
        
        if not metric:
            return
        
        for src in self.__adj.keys():
            vis = {}
            
            indeg = {v : 0 for v in vis}
            treeAdj = {v : [] for v in vis}
                        
            for u in vis.keys():
                for edgeInfo in self.__adj[u]['adj']:
                    v = edgeInfo['vertex']
                    w = edgeInfo['time']
                    if self.__dist[src][u] + w == self.__dist[src][v]:
                        treeAdj[v].append(u)
                        indeg[u] += 1
                        
            dp = {u : 1 for u in vis}
                
            q = queue.Queue()
            for i in vis:
                if indeg[i] == 0:
                    q.put(i)
            
            while not q.empty():
                u = q.get()
                for v in treeAdj[u]:
                    indeg[v] -= 1
                    dp[v] += dp[u]
                    if indeg[v] == 0:
                        q.put(v)
                        
            for i in vis:
                self.__imp[i] += dp[i]
                    
    def tracePath(self, u, v):
        resultList = []
        while v != u:
            dicStop = {
                'type': 'stop',
                'stopid': v
            }
            resultList.append(dicStop)
            dicPath = {
                'type': 'path',
                'route': self.__prev[u][v]['route'],
                'routeid': self.__prev[u][v]['routeid']
            }
            resultList.append(dicPath)
            v = self.__prev[u][v]['prev_vertex']
        dicStop = {
            'type': 'stop',
            'stopid': u
        }
        resultList.append(dicStop)
        resultList.reverse()
        return resultList
        
    def queryTopK(self, k = 10):
        resultList = []
        tmpList = []
        for i in self.__adj.keys():
            tmpList.append((self.__imp[i], i))
        tmpList.sort()
        tmpList.reverse()
        for i in range(min(k, len(tmpList))):
            resultList.append((tmpList[i][0], tmpList[i][1]))
        return resultList
    
    def getTime(self, u, v):
        if v not in self.__dist[u]:
            return -1
        return self.__dist[u][v]
    
    def getAllPairs(self):
        result = []
        for u in self.__dist:
            for v, dis in self.__dist[u].items():
                result.append((u, v, dis))
        return result