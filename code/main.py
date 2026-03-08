from network import Network
from graph import Graph

# Load the network
network_file = "examples/large-nofatigue.txt"
network = Network.from_file(network_file)

# Construire le graphe simple
graph = network.build_simple_graph()

# Sommet de départ
dep = network.start

# Calculer le plus court chemin
distances = graph.shortest_path(dep)

# Calcul du plus court chemin
distances = graph.shortest_path(dep)

# Afficher le résultat pour small.txt
print("Résultat small.txt :", distances.get(network.end))