from network import Network
from graph import Graph

# Load the network
network_file = "../examples/small.txt"
network = Network.from_file(network_file)

# Construire le graphe simple
graph = network.build_simple_graph()

# Calculer le plus court chemin
distances, precedent = graph.shortest_path(dep)

