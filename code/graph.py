import heapq
"""
Ce module implémente les structures de graphes et les algorithmes associés.
Il contient deux classes principales : Graph et GraphImplicit.

Classes
-------
Graph :
    Représente un graphe orienté pondéré sous forme de liste d'adjacence.
    Fournit les algorithmes de plus court chemin (Dijkstra naïf et optimisé)
    ainsi qu'une méthode de construction de graphe étendu tenant compte de la fatigue.

GraphImplicit :
    Hérite de Graph. Représente un graphe dont les voisins sont calculés
    à la volée via une fonction passée en paramètre, sans stocker explicitement
    la liste d'adjacence.
"""


class Graph:
    """
    Classe minimale représentant un graphe orienté pondéré sous forme de liste d'adjacence.

    Attributs
    ---------
    _edges : dict
        Dictionnaire associant à chaque sommet la liste de ses voisins avec le poids
        de l'arête correspondante.
        Exemple :
            edges = {
                sommet_0: [(sommet_1, 21), (sommet_2, 12)],
                sommet_1: [(sommet_0, 74), (sommet_2, 32)],
                ...
            }

    Méthodes
    --------
    neighbours(noeud) :
        Retourne la liste des voisins (et leurs poids) d'un sommet donné.
    shortest_path_naïve(depart) :
        Implémentation naïve de l'algorithme de Dijkstra (sans file de priorité).
    shortest_path(depart) :
        Implémentation optimisée de l'algorithme de Dijkstra (avec tas binaire).
    build_extended_graph(reseau) :
        Construit le graphe étendu intégrant la fatigue accumulée comme dimension d'état.
    """

    def __init__(self, edges):
        """
        Initialise le graphe avec une liste d'adjacence.

        Paramètres
        ----------
        edges : dict
            Dictionnaire de la forme {sommet: [(voisin, poids), ...]}.
        """
        self._edges = edges

    def neighbours(self, node):
        """
        Retourne la liste des voisins d'un sommet avec leurs poids.

        Paramètres
        ----------
        node : sommet
            Le sommet dont on veut connaître les voisins.

        Retourne
        --------
        list
            Liste de tuples (voisin, poids). Retourne une liste vide si le sommet
            n'existe pas dans le graphe.
        """
        if node not in self._edges:
            return []
        return self._edges[node]
    
    def shortest_path_naïve(self, dep):
        """
        Version naïve de l'algorithme de Dijkstra sans file de priorité.

        À chaque itération, le sommet non visité de distance minimale est sélectionné
        par un parcours linéaire (complexité O(n) par itération), ce qui donne une
        complexité globale de O(n² + m) où n est le nombre de sommets et m le nombre
        d'arêtes.

        Paramètres
        ----------
        dep : sommet
            Le sommet de départ depuis lequel calculer les plus courts chemins.

        Retourne
        --------
        distance : dict
            Dictionnaire {sommet: distance_minimale_depuis_dep}.
        precedent : dict
            Dictionnaire {sommet: sommet_precedent_sur_le_plus_court_chemin}.
        """
        # Initialisation des deux dictionnaires et de la liste des sommets non visités
        distance = {}
        precedent = {}
        non_visite = []
        
        for sommet in self._edges:
            distance[sommet] = float('inf')
            non_visite.append(sommet)
            
        distance[dep] = 0 
        
        while len(non_visite) != 0:
            # On extrait le sommet de distance minimale au sommet de départ
            # qui n'a pas encore été visité
            sommet = min(non_visite, key = lambda x: distance[x])
            # On le retire ensuite de la liste des sommets non visités
            non_visite.remove(sommet)
            
            for voisin, poids in self._edges[sommet]:
                # Calcul de la distance du voisin depuis sommet
                total = distance[sommet] + poids
                # Si cette distance est plus courte que la distance actuellement
                # stockée, on la met à jour dans le dictionnaire distance
                if total < distance[voisin]:
                    distance[voisin] = total 
                    precedent[voisin] = sommet 
                
        return distance, precedent 
    
    
    def shortest_path(self, start):
        """
        Implémentation optimisée de l'algorithme de Dijkstra avec file de priorité (tas binaire).

        Utilise le module heapq pour extraire en O(log n) le sommet de distance minimale
        à chaque étape. La complexité globale est O((n + m) log n) où n est le nombre
        de sommets et m le nombre d'arêtes.

        Paramètres
        ----------
        start : sommet
            Le sommet de départ depuis lequel calculer les plus courts chemins.

        Retourne
        --------
        distances : dict
            Dictionnaire {sommet: distance_minimale_depuis_start}.
            Les sommets non atteignables conservent la valeur float('inf').
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
        """
        Construit un graphe étendu intégrant la fatigue accumulée comme dimension d'état.

        Chaque nœud du graphe étendu est un couple (sommet, fatigue_accumulée).
        Le coût d'une arête dans le graphe étendu est : longueur × (1 + fatigue_courante),
        ce qui pénalise les chemins où la fatigue est élevée.

        La fatigue maximale (Fmax) est calculée comme la somme de toutes les fatigues
        présentes dans le réseau. Tout état dont la fatigue dépasse Fmax est ignoré.

        Analyse de complexité
        ---------------------
        Soit :
            n     = |V|    nombre de sommets du graphe original
            m     = |E|    nombre d'arêtes du graphe original
            Fmax  =        borne maximale de fatigue considérée

        - Nombre de sommets du graphe étendu : |V'| = n × (Fmax + 1)
        - Nombre d'arêtes du graphe étendu   : |E'| = O(m × Fmax)
        - Complexité de construction          : O(m × Fmax)
        - Complexité de Dijkstra sur le graphe étendu :
            O((|V'| + |E'|) × log|V'|) = O(m × Fmax × log(n × Fmax))

        Paramètres
        ----------
        network : objet réseau
            Objet possédant un attribut `_roads` de la forme :
            {sommet: [(voisin, longueur, fatigue), ...]}.

        Retourne
        --------
        Graph
            Une instance de Graph représentant le graphe étendu, dont les sommets
            sont des tuples (sommet_original, fatigue_accumulée).
        """
        extended_edges = {}
        
        # Calcul de la fatigue max : somme de toutes les fatigues dans le network
        Fmax = sum(f for voisins in network._roads.values() for (_, _, f) in voisins)
        
        for node in network._roads:
            for F in range(Fmax + 1):
                u = (node, F)
                extended_edges[u] = {}
                # On extrait des voisins de node leur distance ainsi que leur fatigue
                for neighbor, length, fatigue in network._roads[node]:
                    # On calcule la fatigue accumulée
                    new_F = F + fatigue
                    # Si cette fatigue dépasse la fatigue max alors on sait que ce
                    # sommet n'existera pas, donc on ne le considère pas
                    if new_F > Fmax:
                        continue
                    v = (neighbor, new_F)
                    # On calcule le coût, c'est-à-dire la distance de node
                    # à neighbor en tenant compte de la fatigue actuelle
                    cost = length * (1 + F)  
                    extended_edges[u][v] = cost             
        return Graph(extended_edges)


class GraphImplicit(Graph):
    """
    Graphe implicite dont les voisins sont générés à la volée par une fonction.

    Hérite de Graph mais ne stocke pas de liste d'adjacence explicite.
    Les voisins de chaque nœud sont calculés dynamiquement lors de l'exploration,
    ce qui est utile pour les graphes de très grande taille ou infinis.

    Attributs
    ---------
    _neighbours_function : callable
        Fonction prenant un nœud en paramètre et retournant la liste de ses voisins
        sous la forme [(voisin, poids), ...].

    Méthodes
    --------
    neighbours(noeud) :
        Retourne les voisins du nœud calculés à la volée par _neighbours_function.
    """

    def __init__(self, neighbours_function):
        """
        Initialise le graphe implicite avec une fonction de voisinage.

        Paramètres
        ----------
        neighbours_function : callable
            Fonction de la forme f(noeud) -> [(voisin, poids), ...].
            Elle sera appelée dynamiquement lors de chaque exploration de voisins.
        """
        self._neighbours_function = neighbours_function

    def neighbours(self, node):
        """
        Retourne les voisins du nœud calculés à la volée.

        Paramètres
        ----------
        node : sommet
            Le nœud dont on souhaite obtenir les voisins.

        Retourne
        --------
        list
            Liste de tuples (voisin, poids) générée dynamiquement
            par la fonction _neighbours_function.
        """
        # Retourne les voisins du noeud à la volée
        return self._neighbours_function(node)


def shortest_path_with_pruning(self, start, end_node):
    """
    Idée : Dijkstra sur graphe étendu avec pruning des états Pareto-dominés.

    Un état (sommet, fatigue) est Pareto-dominé si on a déjà visité ce sommet
    avec une fatigue inférieure et un temps inférieur. On élimine alors cet état
    car il ne peut pas mener à une solution optimale.
    
    Dans le pire cas (pas de pruning), on retrouve la complexité de Dijkstra
    standard sur le graphe étendu : O((|V'| + |E'|) log |V'|).
    En pratique, le pruning réduit significativement le nombre d'états explorés.

    """
    # best_for_node[sommet] = liste de (fatigue, temps) des états non dominés
    # Un état (f2, t2) est dominé s'il existe (f1, t1) avec f1<=f2 et t1<=t2
    best_for_node = {}

    # File de priorité : (temps_cumulé, état)
    priority_queue = [(0, start)]
    distances = {start: 0}

    while priority_queue:
        current_time, current_state = heapq.heappop(priority_queue)

        # Ignorer si on a trouvé mieux entre-temps
        if current_time > distances.get(current_state, float('inf')):
            continue

        node, fatigue = current_state

        # On vérifie si cet état est dominé par un état déjà connu pour ce sommet
        pareto_front = best_for_node.get(node, [])
        dominated = any(f <= fatigue and t <= current_time for f, t in pareto_front)
        if dominated:
            continue  # Cet état est Pareto-dominé, on l'élague

        # Cet état n'est pas dominé : on l'ajoute au front de Pareto
        # On retire aussi les anciens états que cet état domine
        best_for_node[node] = [
            (f, t) for f, t in pareto_front
            if not (fatigue <= f and current_time <= t)
        ]
        best_for_node[node].append((fatigue, current_time))

        # Exploration des voisins
        for neighbor_state, weight in self.neighbours(current_state):
            new_time = current_time + weight
            if new_time < distances.get(neighbor_state, float('inf')):
                distances[neighbor_state] = new_time
                heapq.heappush(priority_queue, (new_time, neighbor_state))

    # On cherche le meilleur temps parmi tous les états (end_node, *) atteints
    best_time = float('inf')
    for state, time in distances.items():
        if state[0] == end_node:
            best_time = min(best_time, time)
    return best_time


def astar(self, start, end_node, heuristic):
    """

    Idée : Combiner Dijkstra avec une heuristique admissible pour guider la recherche
    vers le but, réduisant le nombre d'états explorés.

    L'heuristique doit être admissible : h(état) <= coût_réel_restant(état -> but).
    Une heuristique typique est la distance minimale sans fatigue depuis le sommet
    courant jusqu'au but (calculée en pré-traitement par Dijkstra inversé).

    """
    # g[état] = meilleur temps connu depuis start jusqu'à état
    g = {start: 0}
    # f[état] = g[état] + h(état) : score total estimé
    f_score = {start: heuristic(start)}

    # File de priorité : (f_score, état)
    priority_queue = [(f_score[start], start)]

    while priority_queue:
        current_f, current_state = heapq.heappop(priority_queue)

        node, fatigue = current_state

        # Si on atteint le sommet but, on retourne le temps réel (g, pas f)
        if node == end_node:
            return g[current_state]

        # Ignorer les entrées obsolètes dans la file
        if current_f > f_score.get(current_state, float('inf')):
            continue

        for neighbor_state, weight in self.neighbours(current_state):
            tentative_g = g[current_state] + weight

            if tentative_g < g.get(neighbor_state, float('inf')):
                g[neighbor_state] = tentative_g
                f_new = tentative_g + heuristic(neighbor_state)
                f_score[neighbor_state] = f_new
                heapq.heappush(priority_queue, (f_new, neighbor_state))

    return float('inf')