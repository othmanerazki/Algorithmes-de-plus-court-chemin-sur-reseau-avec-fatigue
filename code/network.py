from graph import *

class Network:
    """
    Class for a network that represents the environment (with length and fatigue on roads). 
    """

    def __init__(self, roads={}, start=None, end=None):
        """
        Initializes the network from a dictionary roads. 

        Parameters: 
        -----------
        roads: dict
            A dictionary of the roads as an adjacency list, that is 
            roads[u] = list of (v, length, fatigue)
            Ex: roads = {v0: [(v1, 21, 2), (v2, 12, 4)], 
                        v1: [(v0, 74, 2), (v2, 32, 1)], 
                        ...}
        start, end: 
            Start and end nodes added as attributes
        """
        self._roads = roads
        self.start = start
        self.end = end

    def __str__(self): 
        """
        Prints the network as text.
        """
        output = f"A network with {len(self._roads)} nodes and the following adjacency list:\n"
        return output+self._roads.__str__()

    @classmethod
    def from_file(cls, filename: str):
        """
        Creates a Network from an environment file.

        File format: one edge per line (start end length fatigue).
        """
        # Initialize adjacency list
        roads = {}

        with open(filename, "r") as testcase:
            nb, start, end = testcase.readline().strip().split()
            for _ in range(int(nb)):
                i, j, l, f = testcase.readline().strip().split()
                l, f = int(l), int(f)
                roads.setdefault(i, []).append((j, l, f))
                roads.setdefault(j, [])

        return cls(roads=roads, start=start, end=end)

    def build_simple_graph(self):
        """
        Builds an object of type Graph from the network, by ignoring the fatigue coefficient. 
        """
        graph = {}
        for sommet, voisins in self._roads.items():
            graph[sommet] = [(a,b) for a,b,c in voisins]
        return Graph(graph)


    def build_graph_implicit(network):
        """
        Construit un GraphImplicit pour le network donné.
        """
        # Calcul de la fatigue max théorique
        Fmax = sum(f for voisins in network._roads.values() for (_, _, f) in voisins)

        # Fonction qui retourne les voisins d'un état (node, fatigue)
        def neighbours_fn(state):
            node, F = state
            result = []
            for neighbor, length, fatigue in network._roads.get(node, []):
                new_F = F + fatigue
                if new_F > Fmax:
                    continue
                neighbor_state = (neighbor, new_F)
                cost = length * (1 + F)
                result.append((neighbor_state, cost))
            return result  

        # On retourne l'objet GraphImplicit
        return GraphImplicit(neighbours_fn)