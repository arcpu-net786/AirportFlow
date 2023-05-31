from collections import defaultdict
from random import randint

#parse "flights.txt" for all flights that start & end in the same day.
def gen_eligible_flights(txt = "flights.txt"):
    lines = open(txt, "r")
    ef = [] #list of eligible flights
    i = 0
    
    #iterate through all the lines to parse flight-specific data
    for line in lines:
        flight = [0] * 6
        temp = line
        
        #remove whitespace and format
        temp = temp.replace("\t", " ")
        temp = temp.replace("\n", "")
        temp = temp.split(" ")
        
        #print(temp)
        #store airport data, time data, and capacity data as list elements
        flight[0] = i
        flight[1] = temp[0]
        flight[2] = temp[1]
        flight[3] = (int(temp[2]) - 6) % 24 #shift time by 6 hours to follow 6am - 5:59am convention
        flight[4] = (int(temp[3]) - 6) % 24 #shift time by 6 hours to follow 6am - 5:59am convention
        if temp[4] == '':
        	flight[5] = int(temp[5])
        else:
        	flight[5] = int(temp[4])
        
        #check for all flights that start and end in same 24hr period
        if flight[3] < flight[4]:
            ef.append(flight)
        i += 1
    return ef


# for every pair of cities, this function searches a list of eligible flights to find all flights from source to destination.
def find_duos(ef):
    source_airports = ["LAX", "SFO", "SEA", "PHX", "DEN", "ATL", "ORD", "BOS", "IAD"]
    dest_airports =          ["SFO", "SEA", "PHX", "DEN", "ATL", "ORD", "BOS", "IAD", "JFK"]

    #iterate through all pairs of source -> destination airports and search through eligible flights.
    #append each eligibile flight for each pair.
    flights_per_duo = {}
    for src in source_airports:
        for dst in dest_airports:
            if src != dst:
                route = str(src + " ⟶ " + dst)
                if route not in flights_per_duo:
                    flights_per_duo[route] = []
                for flight in ef:
                    if flight[1] == src and flight[2] == dst:
                        flights_per_duo[route].append(flight)
    return flights_per_duo


#data structure for a queue
class Queue:
    def __init__(self):
        self.data = []
        self.start = -1
        self.end = -1
    
    def push(self, item):
        self.data.append(item)
        
    def pop(self):
        return self.data.pop(0)
    
    def is_empty(self):
        return len(self.data) == 0


#data structure for a node
class Node:
    def __init__(self, level, parent = None, val = None):
        self.level = level
        self.parent = parent
        self.val = val


#input:  1) a single path string ("LAX -> PHX -> ATL -> JFK") and 2) all flights available for eair pair of cities.
#output: the maximum capacity of the flows for all possible combination of flights that can use this path.
def find_max_cap_from_path(path, flights_per_duo, length=True):
    trips = [flights_per_duo[str(path[i] + " ⟶ " + path[i+1])] for i in range(len(path)-1)]
    queue = Queue()
    end_nodes = []
    root = Node(0)

    for trip in trips[root.level]:
        child = Node(root.level + 1, root, trip)
        queue.push(child)

    #while the queue has elements, find all flights originating from source airport node. Set as children node.
    while not queue.is_empty():
        curr = queue.pop()
        if curr.level < len(trips):
            for trip in trips[curr.level]:
                if curr.val[4] <= trip[3]:
                    child = Node(curr.level + 1, curr, trip)
                    queue.push(child)
                    if trip[2] == path[-1]:
                        end_nodes.append(child)
        else:
            break

    #iterate through all nodes that end at JFK, then backtrack through their parent nodes to the root node to find the path.
    ways = []
    for node in end_nodes:
        way = []
        curr = node
        while curr.val != None:
            way.insert(0, curr.val)
            curr = curr.parent
        way.insert(0, min(way[i][5] for i in range(len(way))))
        ways.append(way)
        
    if length:
        return len(ways)
    else:
        return max(ways)


#input: some considered paths ("LAX", "ORD", "ATL", "PHX", "JFK") and all flights for each pair of cities
#output: all possible paths with the remaining flights.
def find_all_permissible_paths(considered_paths, flights_per_duo):
    permissible_paths = []
    for option in considered_paths:
        if find_max_cap_from_path(option, flights_per_duo) > 0:
            permissible_paths.append(option)
    return permissible_paths
    

#given a list of considered permissible paths and the list of flights per pair of cities.
#returns the maximum capacity permissible through all of the permissible paths.
def find_max_of_all_permissible_paths(considered_paths, fpd):
    max_path = considered_paths[0]
    max_cap = 0
    for path in considered_paths:
        opt = find_max_cap_from_path(path, fpd, False)
        if opt[0] > max_cap:
            max_cap = opt[0]
            max_path = opt[1:]
    return max_cap, max_path


#representation of airport codes
atoi = {"LAX":1, "SFO":2, "SEA":3, "DEN":4, "PHX":5, "ATL":6, "ORD":7, "IAD":8, "BOS":9, "JFK":10}
itoa = {1:"LAX", 2:"SFO", 3:"SEA", 4:"DEN", 5:"PHX", 6:"ATL", 7:"ORD", 8:"IAD", 9:"BOS", 10:"JFK"}

# graph representation class
# DFS search algorithm inspired by: https://www.geeksforgeeks.org/find-paths-given-source-destination/
# heavily modified to fit the needs of this problem.
class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = defaultdict(list)
        self.struct = []

    #add the path to the list of paths (struct)
    def addPath(self, p):
        path = [itoa[elem] for elem in p]
        self.struct.append(path)

    #connect source airport to destination airport
    def connect(self, u, v):
        self.graph[atoi[u]].append(atoi[v])

    #recursively searches for all paths from u to d
    def findAllPathsUtil(self, u, d, visited, path):
        visited[u] = 1
        path.append(u)
        if u == d:
            self.addPath(path)
        else:
            for i in self.graph[u]:
                if visited[i] == 0:
                    self.findAllPathsUtil(i, d, visited, path)
        path.pop()
        visited[u] = 0
        
    #initiation function to find all paths; keeps track through visited nodes
    def findAllPaths(self, s, d):
        visited = [0]*(self.V)
        path = []
        self.findAllPathsUtil(atoi[s], atoi[d], visited, path)

#initialize graph of airport cities based on connections between the cities.    
graph = Graph(11)
source_airports = ["LAX", "SFO", "SEA", "PHX", "DEN", "ATL", "ORD", "BOS", "IAD"]
dest_airports =   ["SFO", "SEA", "PHX", "DEN", "ATL", "ORD", "BOS", "IAD", "JFK"]

for src in source_airports:
    for dst in dest_airports:
        if src != dst:
            graph.connect(src, dst)

graph.findAllPaths("LAX", "JFK")


#find the original flight infomation based on the provided index.
def find_flight(flight_list, val):
    for flight in flight_list:
        if flight[0] == val:
            return flight


#calculates the maximum number of passengers that can be transported from LAX to JFK in a 24-hour period, using flight data from flights.txt.
def calculate_max_flow():
    total_cap = 0
    print("...Calculating...")
    
    distinct = set()
    orig_flights = gen_eligible_flights()
    eligible_flights = gen_eligible_flights() #calculated automatically once, then manually
    flights_per_duo = find_duos(eligible_flights)
    permissible_paths = find_all_permissible_paths(graph.struct, flights_per_duo)
    
    #iterate through all permissible paths to find the optimal path available.
    while len(permissible_paths) > 0:
        max_cap, max_path = find_max_of_all_permissible_paths(permissible_paths, flights_per_duo)
        total_cap += max_cap

        orig_path = []
        for elem in max_path:
            flt = find_flight(orig_flights, elem[0])
            distinct.add(flt[0])
            orig_path.append(flt[1:])
        print(str(orig_path), " |  Passengers carried =", max_cap)

        #find the max capacity flight path 
        for flight in max_path:
            if flight in eligible_flights:
                if flight[5] <= max_cap:
                    eligible_flights.remove(flight) #remove the flight if it equals the capacity
                else:
                    eligible_flights[eligible_flights.index(flight)][5] -= max_cap #otherwise subtract from the capacity
        
        #recalculate the permissible paths
        flights_per_duo = find_duos(eligible_flights)
        permissible_paths = find_all_permissible_paths(permissible_paths, flights_per_duo)
        #keep iterating until no more people can reach JFK from LAX.

    print("Maximum Capacity from LAX to JFK = " + str(total_cap))
    print("# of distinct flights: " + str(len(distinct)))
    return total_cap

calculate_max_flow()