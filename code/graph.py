"""
This is the graph module. It contains the classes Graph and GraphImplicit
"""


class Graph:
    """
    A minimal class for directed weighted graph represented as adjacency list. 
    
    Attributes: 
    -----------
    edges: dict
        A dictionary that contains the list of neighbors of each node with its weight.
        Ex: edges = {v0: [(v1, 21), (v2, 12)], 
                     v1: [(v0, 74), (v2, 32)], 
                     ...}

    Methods: 
    --------
    neighbours(self, node): 
        Returns the list of all neighbors of a node
    """

    def __init__(self, edges):
        self._edges = edges

    def neighbours(self, node):
        if node not in self._edges:
            return []
        return self._edges[node]
    
    def shortest_path(self, start):
        """    
        Dijkstra's algorithm as a method of the Graph class.
        Returns a dictionary of shortest distances from 'start'.
        """
        # Initialisation : distance 0 pour le départ, l'infini pour le reste
        # On utilise un dictionnaire par défaut pour gérer les nœuds inconnus
        distances = {node: float('inf') for node in self._edges}
        distances[start] = 0
            
        # File de priorité : (poids_cumulé, sommet)
        priority_queue = [(0, start)]
            
        while priority_queue:
            current_dist, current_node = heapq.heappop(priority_queue)

            # Si on a déjà trouvé un chemin plus court pour ce nœud, on ignore
            if current_dist > distances.get(current_node, float('inf')):
                continue

            # Exploration des voisins via la méthode interne
            for neighbor, weight in self.neighbours(current_node):
                distance = current_dist + weight

                # Mise à jour si un chemin plus court est découvert
                if distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))
            
        return distances


    def build_extended_graph(self, graphe):
    graphe_etendue = {}
    #majorer Fmax
    Fmax = sum(sommet.fatigue for sommet in self.graphe)
    for sommet in self.graphe:
        for F in range(Fmax + 1):
            u = (sommet, F)
            graphe_etendue[u] = []
        
    for sommet in self.graphe:
        for F in range(Fmax + 1):
            u = (sommet, F)
                
            for neighbor, length, fatigue_increase in self.graphe[sommet]:
                new_F = F + fatigue_increase
                if new_F > Fmax:
                    continue
                v = (neighbor, new_F)
                cost = length * (1 + F)
                graphe_etendue[u].append((v,cost))
    return Graph(graphe_etendue)
