import copy, yaml, os, sys

#================OPEN CONFIGURATIONS FILE================

if os.path.isfile("input.yml"):
	configurations = open("input.yml", "r")
	config= yaml.load(configurations)
else:
	text ="No configuration file for script to run"
	files = []
	sys.exit()
	
nodes = config["nodes"]
srlg_values = config["srlg_values"]

distances = config["distances"]
srlg = config["srlg"]

def get_shortest_path(weighted_graph, start, end):
    """
    Calculate the shortest path for a directed weighted graph.

    Node can be virtually any hashable datatype.

    :param start: starting node
    :param end: ending node
    :param weighted_graph: {"node1": {"node2": "weight", ...}, ...}
    :return: ["START", ... nodes between ..., "END"] or None, if there is no
             path
    """

    # We always need to visit the start
    nodes_to_visit = {start}
    visited_nodes = set()
    # Distance from start to start is 0
    distance_from_start = {start: 0}
    tentative_parents = {}

    while nodes_to_visit:
        # The next node should be the one with the smallest weight
        current = min(
            [(distance_from_start[node], node) for node in nodes_to_visit]
        )[1]

        # The end was reached
        if current == end:
            break

        nodes_to_visit.discard(current)
        visited_nodes.add(current)

        edges = weighted_graph[current]
        unvisited_neighbours = set(edges).difference(visited_nodes)
        for neighbour in unvisited_neighbours:
            neighbour_distance = distance_from_start[current] + \
                                 edges[neighbour]
            if neighbour_distance < distance_from_start.get(neighbour,
                                                            float('inf')):
                distance_from_start[neighbour] = neighbour_distance
                tentative_parents[neighbour] = current
                nodes_to_visit.add(neighbour)

    return _deconstruct_path(tentative_parents, end)


def _deconstruct_path(tentative_parents, end):
    if end not in tentative_parents:
        return None
    cursor = end
    path = []
    while cursor:
        path.append(cursor)
        cursor = tentative_parents.get(cursor)
    return list(reversed(path))
"""
for source in nodes:
	for destination in distances:
		print "-----   "+source+" to "+destination+"   ------"
		print "primary:"+ str (get_shortest_path(distances, source, destination))
		print "SRLG secondary:"	
		print
		print
"""
def remove_srlg_paths(srlg, shortest_path, distances):
	path_length=0
	start_node = 0
	loop = 1
	srlg_over_shortest_path =[]
	while loop < len(shortest_path):
		if shortest_path[start_node] in srlg:
			end_node = start_node+1
			if shortest_path[end_node] in srlg[shortest_path[start_node]]:
				srlg_value = srlg[shortest_path[start_node]][shortest_path[end_node]]
				srlg_over_shortest_path.extend(srlg_value) 
		start_node = start_node+1
		loop = loop+1
	global distances_srlg_removed
	distances_srlg_removed = {}
	distances_srlg_removed = copy.deepcopy(distances)
	for source in srlg:
		for destination in srlg[source]:
			if any(x in srlg_over_shortest_path for x in srlg[source][destination]):
				if source in distances_srlg_removed and destination in distances_srlg_removed[source]:
					del distances_srlg_removed[source][destination]
		
i=0
m=0	
L=0		
for sources in nodes:
	for destinations in nodes:
		if not destinations == sources:
			print "--------------------"
			i=i+1
			primary_path = get_shortest_path(distances, sources, destinations)
			print "tunnel "+sources+"_to_"+destinations
			print "primary path:"+ str(primary_path)
			print
			j=0
			z=1
			while z < len(primary_path):
				m=m+1
				path_for_frr_calculation=[]
				path_for_frr_calculation.append(primary_path[j])
				path_for_frr_calculation.append(primary_path[z])
				print "frr calculation for: "+str(path_for_frr_calculation)
				if path_for_frr_calculation[0] in srlg and path_for_frr_calculation [1] in srlg[path_for_frr_calculation [0]]:
					print "srlg values: "+str( srlg[path_for_frr_calculation [0]][path_for_frr_calculation[1]])
					remove_srlg_paths(srlg, path_for_frr_calculation, distances)

					frr_path =  get_shortest_path(distances_srlg_removed, path_for_frr_calculation[0], path_for_frr_calculation[1])
					print "srlg avoided shortest path: "+str(frr_path)
					print
					if frr_path== None:
						L=L+1
				else: 
					print "no srlg, frr could follow any path"
					print
				j=j+1
				z=z+1
print "---------------RESULT-------------------"
print "total tunnel count:"+str(i) 
print "total frr count sayisi:"+str(m)
print "total unsuccesfull frr count: "+str(L)