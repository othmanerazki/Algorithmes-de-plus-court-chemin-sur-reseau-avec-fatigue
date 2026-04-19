import heapq

"""
Ce module implémente les structures de graphes et les algorithmes associés.
Il contient deux classes principales : Graph et GraphImplicit.

Classes
-------
Graph :
    Représente un graphe orienté pondéré sous forme de liste d'adjacence.
    Fournit les algorithmes de plus court chemin (Dijkstra naïf et optimisé)
    ainsi que des méthodes avancées (pruning Pareto, A*).

GraphImplicit :
    Hérite de Graph. Représente un graphe dont les voisins sont calculés
    à la volée via une fonction passée en paramètre, sans stocker explicitement
    la liste d'adjacence.
"""


class Graph:
    """
    Classe représentant un graphe orienté pondéré sous forme de liste d'adjacence.

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
        return self._edges.get(node, [])

    def shortest_path_naive(self, dep):
        """
        Version naïve de l'algorithme de Dijkstra sans file de priorité.

        Complexité : O(n² + m) où n est le nombre de sommets et m le nombre d'arêtes.

        Paramètres
        ----------
        dep : sommet
            Le sommet de départ.

        Retourne
        --------
        distance : dict
            Dictionnaire {sommet: distance_minimale_depuis_dep}.
        precedent : dict
            Dictionnaire {sommet: sommet_precedent_sur_le_plus_court_chemin}.
        """
        distance = {sommet: float('inf') for sommet in self._edges}
        precedent = {}
        non_visite = list(self._edges.keys())

        distance[dep] = 0

        while non_visite:
            # Sélection du sommet non visité de distance minimale
            sommet = min(non_visite, key=lambda x: distance.get(x, float('inf')))
            non_visite.remove(sommet)

            if distance.get(sommet, float('inf')) == float('inf'):
                break  # Les sommets restants sont inaccessibles

            for voisin, poids in self.neighbours(sommet):
                total = distance[sommet] + poids
                if total < distance.get(voisin, float('inf')):
                    distance[voisin] = total
                    precedent[voisin] = sommet

        return distance, precedent

    def shortest_path(self, start):
        """
        Implémentation optimisée de l'algorithme de Dijkstra avec file de priorité.

        Complexité : O((n + m) log n).

        Paramètres
        ----------
        start : sommet
            Le sommet de départ.

        Retourne
        --------
        distances : dict
            Dictionnaire {sommet: distance_minimale_depuis_start}.
        """
        distances = {}
        if hasattr(self, '_edges') and self._edges:
            distances = {node: float('inf') for node in self._edges}
        distances[start] = 0

        priority_queue = [(0, start)]

        while priority_queue:
            current_dist, current_node = heapq.heappop(priority_queue)

            if current_dist > distances.get(current_node, float('inf')):
                continue

            for neighbor, weight in self.neighbours(current_node):
                distance = current_dist + weight
                if distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))

        return distances

    def shortest_path_with_pruning(self, start, end_node):
        """
        Dijkstra sur graphe étendu avec pruning des états Pareto-dominés.

        Un état (sommet, fatigue) est Pareto-dominé si on a déjà atteint
        ce sommet avec une fatigue ET un temps tous deux inférieurs.

        Complexité : O((|V'| + |E'|) log |V'|) dans le pire cas,
        meilleure en pratique grâce au pruning.

        Paramètres
        ----------
        start : tuple (sommet, fatigue)
            État initial dans le graphe étendu.
        end_node : sommet
            Sommet d'arrivée (on cherche parmi tous les états (end_node, *)).

        Retourne
        --------
        float
            Temps minimal pour atteindre end_node. float('inf') si non atteignable.
        """
        # best_for_node[sommet] = liste de (fatigue, temps) des états non dominés
        best_for_node = {}

        priority_queue = [(0, start)]
        distances = {start: 0}

        while priority_queue:
            current_time, current_state = heapq.heappop(priority_queue)

            if current_time > distances.get(current_state, float('inf')):
                continue

            node, fatigue = current_state

            # Vérification domination Pareto
            pareto_front = best_for_node.get(node, [])
            dominated = any(f <= fatigue and t <= current_time for f, t in pareto_front)
            if dominated:
                continue

            # Mise à jour du front de Pareto
            best_for_node[node] = [
                (f, t) for f, t in pareto_front
                if not (fatigue <= f and current_time <= t)
            ]
            best_for_node[node].append((fatigue, current_time))

            for neighbor_state, weight in self.neighbours(current_state):
                new_time = current_time + weight
                if new_time < distances.get(neighbor_state, float('inf')):
                    distances[neighbor_state] = new_time
                    heapq.heappush(priority_queue, (new_time, neighbor_state))

        # Meilleur temps parmi tous les états (end_node, *)
        best_time = float('inf')
        for state, time in distances.items():
            if state[0] == end_node:
                best_time = min(best_time, time)
        return best_time

    def shortest_path_with_pruning_from_state(self, start_state, end_node):
        """
        Dijkstra avec pruning Pareto depuis un état initial (sommet, fatigue).

        Utilisé pour le cas multi-missions : l'agent repart avec la fatigue
        accumulée lors des missions précédentes.

        Paramètres
        ----------
        start_state : tuple (sommet, fatigue_accumulée)
            État de départ avec fatigue déjà accumulée.
        end_node : sommet
            Sommet d'arrivée de la mission courante.

        Retourne
        --------
        best_time : float
            Temps minimal pour atteindre end_node.
        best_state : tuple ou None
            État (end_node, fatigue) correspondant au meilleur temps.
            En cas d'égalité de temps, on préfère la fatigue minimale.
        """
        best_for_node = {}
        priority_queue = [(0, start_state)]
        distances = {start_state: 0}

        while priority_queue:
            current_time, current_state = heapq.heappop(priority_queue)

            if current_time > distances.get(current_state, float('inf')):
                continue

            node, fatigue = current_state

            pareto_front = best_for_node.get(node, [])
            dominated = any(f <= fatigue and t <= current_time for f, t in pareto_front)
            if dominated:
                continue

            best_for_node[node] = [
                (f, t) for f, t in pareto_front
                if not (fatigue <= f and current_time <= t)
            ]
            best_for_node[node].append((fatigue, current_time))

            for neighbor_state, weight in self.neighbours(current_state):
                new_time = current_time + weight
                if new_time < distances.get(neighbor_state, float('inf')):
                    distances[neighbor_state] = new_time
                    heapq.heappush(priority_queue, (new_time, neighbor_state))

        # Recherche du meilleur état atteignant end_node
        best_time = float('inf')
        best_state = None

        for state, time in distances.items():
            if state[0] == end_node and time < best_time:
                best_time = time
                best_state = state

        # Départage : parmi les états avec best_time, on préfère la fatigue minimale
        if best_state is not None:
            for state, time in distances.items():
                if (state[0] == end_node
                        and time == best_time
                        and state[1] < best_state[1]):
                    best_state = state

        return best_time, best_state

    def astar(self, start, end_node, heuristic):
        """
        Algorithme A* avec heuristique admissible.

        L'heuristique doit satisfaire h(état) <= coût_réel_restant(état -> but).
        Une heuristique admissible typique : distance sans fatigue depuis le sommet
        courant jusqu'au but (calculée par Dijkstra inversé en pré-traitement).

        Paramètres
        ----------
        start : tuple (sommet, fatigue)
            État initial.
        end_node : sommet
            Sommet d'arrivée.
        heuristic : callable
            Fonction heuristic(état) -> float, admissible.

        Retourne
        --------
        float
            Temps minimal estimé pour atteindre end_node.
            float('inf') si non atteignable.
        """
        g = {start: 0}
        f_score = {start: heuristic(start)}
        priority_queue = [(f_score[start], start)]

        while priority_queue:
            current_f, current_state = heapq.heappop(priority_queue)
            node, fatigue = current_state

            if node == end_node:
                return g[current_state]

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

    def build_extended_graph(self, network):
        """
        Construit le graphe étendu intégrant la fatigue accumulée comme dimension d'état.

        Chaque nœud du graphe étendu est un couple (sommet, fatigue_accumulée).
        Le coût d'une arête est : longueur × (1 + fatigue_courante).

        Analyse de complexité
        ---------------------
        n     = |V| sommets, m = |E| arêtes, Fmax = somme des fatigues.
        - Sommets du graphe étendu : n × (Fmax + 1)
        - Arêtes du graphe étendu  : O(m × Fmax)
        - Construction             : O(m × Fmax)
        - Dijkstra sur le graphe étendu : O(m × Fmax × log(n × Fmax))

        Paramètres
        ----------
        network : Network
            Réseau avec attribut _roads : {sommet: [(voisin, longueur, fatigue), ...]}.

        Retourne
        --------
        Graph
            Instance de Graph représentant le graphe étendu.
        """
        Fmax = sum(f for voisins in network._roads.values() for (_, _, f) in voisins)

        extended_edges = {}
        for node in network._roads:
            for F in range(Fmax + 1):
                u = (node, F)
                extended_edges[u] = []
                for neighbor, length, fatigue in network._roads[node]:
                    new_F = F + fatigue
                    if new_F > Fmax:
                        continue
                    v = (neighbor, new_F)
                    cost = length * (1 + F)
                    extended_edges[u].append((v, cost))

        return Graph(extended_edges)


class GraphImplicit(Graph):
    """
    Graphe implicite dont les voisins sont générés à la volée par une fonction.

    Hérite de Graph mais ne stocke pas de liste d'adjacence explicite.
    Utile pour les graphes de très grande taille : on n'instancie que les nœuds
    effectivement visités lors de l'exploration.

    Attributs
    ---------
    _neighbours_function : callable
        Fonction f(noeud) -> [(voisin, poids), ...].
    """

    def __init__(self, neighbours_function):
        """
        Initialise le graphe implicite.

        Paramètres
        ----------
        neighbours_function : callable
            Fonction f(noeud) -> [(voisin, poids), ...].
        """
        # On n'appelle pas super().__init__ car il n'y a pas de _edges à stocker.
        self._neighbours_function = neighbours_function

    def neighbours(self, node):
        """
        Retourne les voisins du nœud calculés à la volée.

        Paramètres
        ----------
        node : sommet
            Le nœud dont on souhaite les voisins.

        Retourne
        --------
        list
            Liste de tuples (voisin, poids).
        """
        return self._neighbours_function(node)