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
    
    #On propose d'abord une version naïve de l'algorithme sans file de priorité :
    def shortest_path_naïve(graphe, dep):
        #Initialisation des deux dictionnaire et de la liste des sommets non visités 
        distance = {}
        precedent = {}
        non_visite = []
        
        for sommet in graphe:
            distance[sommet] = float('inf')
            non_visite.append(sommet)
            
        distance[dep] = 0 
        
        while len(non_visite) != 0:
            #On extrait le sommet de dsitance minimal au sommet de depart 
            # qui n'a pas encore été visité 
            sommet = min(non_visite, key = lambda x: distance[x])
            #On le retire ensuite de la liste des sommets non visité 
            non_visite.remove(sommet)
            
            for voisin in graphe[sommet]:
                #Calcul de la distance du voisin à sommet 
                total = distance[sommet] + graphe[sommet][voisin]
                #Si cette distance est plus courte que la distance actuellement 
                # stocké on la met à jour dans le dictionnaire distance
                if total < distance[voisin]:
                    distance[voisin] = total 
                    precedent[voisin] = sommet 
                
                
    return distance, precedent 
    
    
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
            if current_dist > distances[current_node]:
                continue

            # Exploration des voisins via la méthode interne
            for neighbor, weight in self.neighbours(current_node):
                distance = current_dist + weight

                # Mise à jour si un chemin plus court est découvert
                if distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))
            
        return distances


    def build_extended_graph(self, network):
    
    extended_edges = {}
    
    # Calcul de la fatigue max : somme de toutes les fatigues dans le network
    Fmax = sum(f for voisins in network._roads.values() for (_, _, f) in voisins)
    
    for node in network._roads:
        for F in range(Fmax + 1):
            u = (node, F)
            extended_edges[u] = {}
            #On extrait des voisins de node leur distance ainsi que leur fatigue 
            for neighbor, length, fatigue in network._roads[node]:
                #On calcul la fatigue accumulé 
                new_F = F + fatigue
                #Si cette fatigue dépasse la fatigue max alors on sait que ce 
                #sommet n'existera pas donc on ne le considère pas
                if new_F > Fmax:
                    continue
                v = (neighbor, new_F)
                #On calcule le coût, c'est à dire la distance de node 
                #à neighbor en tenant compte de la fatigue actuelle
                cost = length * (1 + F)  
                extended_edges[u][v] = cost
                
    return Graph(extended_edges)


#Analyse de complexité :
#On note n = |V| le nombre de sommets du graphe original, m = |E| le nombre d’arêtes du graphe original et Fmax la borne maximale de la fatigue considérée dans le graphe étendu.
#Dans la formulation du graphe étendu, on encode l’état du problème sous la forme d’un couple (sommet, fatigue_accumulée). Ainsi, chaque sommet du graphe original peut être associé à Fmax + 1 états possibles correspondant aux différents niveaux de fatigue. Le nombre de sommets du graphe étendu est donc :
#|V'| = n (Fmax + 1)
#Concernant le nombre d’arêtes du graphe étendu, pour chaque état du graphe étendu, on explore les voisins du sommet correspondant. En moyenne, le degré d’un sommet du graphe est proportionnel à m / n. Par conséquent, le nombre total d’arêtes du graphe étendu est de l’ordre :
#|E'| = O(m Fmax)
#La complexité de la méthode de construction du graphe étendu build_extended_graph consiste à parcourir tous les sommets du graphe original, toutes les valeurs possibles de fatigue ainsi que toutes les arêtes sortantes. La complexité de cette étape est donc :
#O(m Fmax)
#Pour la recherche du plus court chemin, on utilise l’algorithme de Dijkstra avec une file de priorité implémentée par un tas binaire. La complexité de Dijkstra dans ce cas est :
#O((|V'| + |E'|) log |V'|)
#En remplaçant par les tailles du graphe étendu, où |V'| = O(n Fmax) et |E'| = O(m Fmax), on obtient la complexité globale suivante :
#O(m Fmax log (n Fmax))

class GraphImplicit(Graph):

    def __init__(self, neighbours_function):
        
        self._neighbours_function = neighbours_function

    def neighbours(self, node):
       #Retourne les voisins du noeud à la volée
        return self._neighbours_function(node)