"""
Module réseau : définit la classe Network représentant un environnement routier
avec des longueurs et des coefficients de fatigue sur les routes.

Format du fichier d'entrée
--------------------------
Première ligne  : <nb_arêtes> <sommet_départ> <sommet_arrivée>
Lignes suivantes: <sommet_i> <sommet_j> <longueur> <fatigue>
"""

from graph import Graph, GraphImplicit


class Network:
    """
    Classe représentant un réseau routier avec longueur et fatigue sur les routes.

    Attributs
    ---------
    _roads : dict
        Liste d'adjacence : roads[sommet] = [(voisin, longueur, fatigue), ...]
    start : sommet
        Sommet de départ.
    end : sommet
        Sommet d'arrivée.
    """

    def __init__(self, roads=None, start=None, end=None):
        self._roads = roads if roads is not None else {}
        self.start = start
        self.end = end

    def __str__(self):
        output = (f"Réseau avec {len(self._roads)} sommets :\n"
                  f"  départ={self.start}, arrivée={self.end}\n")
        for sommet, voisins in self._roads.items():
            output += f"  {sommet} -> {voisins}\n"
        return output

    @classmethod
    def from_file(cls, filename: str):
        """
        Crée une instance de Network depuis un fichier texte.

        Format : première ligne « nb_arêtes départ arrivée »,
        puis une arête par ligne « i j longueur fatigue ».
        """
        roads = {}
        with open(filename, "r") as f:
            nb, start, end = f.readline().strip().split()
            for _ in range(int(nb)):
                i, j, l, fat = f.readline().strip().split()
                l, fat = int(l), int(fat)
                roads.setdefault(i, []).append((j, l, fat))
                roads.setdefault(j, [])
        return cls(roads=roads, start=start, end=end)

    def build_simple_graph(self):
        """
        Construit un Graph en ignorant la fatigue (arêtes = (voisin, longueur)).

        Complexité : O(n + m).

        Retourne
        --------
        Graph
        """
        graph = {}
        for sommet, voisins in self._roads.items():
            graph[sommet] = [(v, l) for v, l, _ in voisins]
        return Graph(graph)

    def build_graph_implicit(self):
        """
        Construit un GraphImplicit tenant compte de la fatigue.

        Chaque état est (sommet, fatigue_accumulée).
        Coût d'une transition : longueur x (1 + fatigue_courante).
        Les états dont la fatigue dépasse Fmax sont ignorés.

        Retourne
        --------
        GraphImplicit
        """
        Fmax = sum(f for voisins in self._roads.values() for (_, _, f) in voisins)
        roads = self._roads

        def neighbours_fn(state):
            node, F = state
            result = []
            for neighbor, length, fatigue in roads.get(node, []):
                new_F = F + fatigue
                if new_F > Fmax:
                    continue
                cost = length * (1 + F)
                result.append(((neighbor, new_F), cost))
            return result

        return GraphImplicit(neighbours_fn)

    def build_reversed_simple_graph(self):
        """
        Construit le graphe simple inversé (arêtes retournées, sans fatigue).

        Utile pour le pré-traitement de A* : Dijkstra depuis vt sur ce graphe
        donne la distance minimale (sans fatigue) de chaque sommet jusqu'à vt.

        Retourne
        --------
        Graph
        """
        reversed_graph = {sommet: [] for sommet in self._roads}
        for sommet, voisins in self._roads.items():
            for voisin, longueur, _ in voisins:
                reversed_graph.setdefault(voisin, []).append((sommet, longueur))
        return Graph(reversed_graph)

    def build_reversed_implicit_graph(self):
        """
        Construit le graphe implicite étendu inversé.

        Une arête (u, Fu) -> (v, Fv) du graphe original devient
        (v, Fv) -> (u, Fu) avec le même coût length x (1 + Fu).

        Utilisé pour find_optimal_rest_point : Dijkstra depuis (vt, 0)
        sur ce graphe donne d_backward(r) = temps minimal de r (fatigue 0) a vt.

        On précalcule la liste d'adjacence inversée pour éviter O(n.m)
        à chaque appel de neighbours.

        Retourne
        --------
        GraphImplicit
        """
        Fmax = sum(f for voisins in self._roads.values() for (_, _, f) in voisins)

        # Précalcul de la liste d'adjacence inversée étendue
        reversed_adj = {}
        for node in self._roads:
            for neighbor, length, fatigue_edge in self._roads[node]:
                for Fu in range(Fmax + 1):
                    Fv = Fu + fatigue_edge
                    if Fv > Fmax:
                        continue
                    cost = length * (1 + Fu)
                    key = (neighbor, Fv)
                    reversed_adj.setdefault(key, []).append(((node, Fu), cost))

        def neighbours_fn_reversed(state):
            return reversed_adj.get(state, [])

        return GraphImplicit(neighbours_fn_reversed)

    def find_optimal_rest_point(self):
        """
        Trouve le sommet optimal où placer un unique lieu de repos.

        Le lieu de repos remet la fatigue a zéro. On cherche le sommet r
        minimisant T(r) = d_forward(r) + d_backward(r), où :
            - d_forward(r)  = temps minimal de (vs, 0) a (r, *) dans le graphe étendu
            - d_backward(r) = temps minimal de (r, 0) a (vt, *)
                            = distance inversée depuis (vt, 0)

        Algorithme : 2 passes de Dijkstra.
        Complexité : O(m . Fmax . log(n . Fmax)).

        Retourne
        --------
        best_rest : sommet
        best_time : float
        time_without_rest : float
        results : list of (sommet, float), triés par temps croissant
        """
        # Passe aller : Dijkstra depuis (vs, 0)
        implicit_graph = self.build_graph_implicit()
        dist_forward_full = implicit_graph.shortest_path((self.start, 0))

        # d_forward[r] = min sur toutes les fatigues
        d_forward = {}
        for (node, f), dist in dist_forward_full.items():
            if dist < d_forward.get(node, float('inf')):
                d_forward[node] = dist

        time_without_rest = d_forward.get(self.end, float('inf'))

        # Passe retour : Dijkstra depuis (vt, 0) sur le graphe inversé
        reversed_graph = self.build_reversed_implicit_graph()
        dist_backward_full = reversed_graph.shortest_path((self.end, 0))

        # d_backward[r] = dist depuis (r, 0) — l'agent repart avec fatigue 0
        d_backward = {}
        for (node, f), dist in dist_backward_full.items():
            if f == 0:
                d_backward[node] = dist

        # T(r) pour chaque candidat
        results = sorted(
            [
                (r, d_forward.get(r, float('inf')) + d_backward.get(r, float('inf')))
                for r in self._roads
            ],
            key=lambda x: x[1]
        )

        best_rest, best_time = results[0] if results else (None, float('inf'))
        return best_rest, best_time, time_without_rest, results