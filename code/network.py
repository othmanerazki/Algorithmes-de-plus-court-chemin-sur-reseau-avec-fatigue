"""
Module réseau : définit la classe Network représentant un environnement routier
avec des longueurs et des coefficients de fatigue sur les routes.

La classe Network permet de :
    - Charger un réseau depuis un fichier texte structuré.
    - Construire un graphe simple (sans fatigue) via Graph.
    - Construire un graphe implicite (avec fatigue) via GraphImplicit.

Format du fichier d'entrée
--------------------------
Première ligne : <nb_arêtes> <sommet_départ> <sommet_arrivée>
Lignes suivantes (une par arête) : <sommet_i> <sommet_j> <longueur> <fatigue>
"""

from graph import *


class Network:
    """
    Classe représentant un réseau routier avec longueur et fatigue sur les routes.

    Attributs
    ---------
    _roads : dict
        Liste d'adjacence du réseau, de la forme :
            roads[sommet] = [(voisin, longueur, fatigue), ...]
        Exemple :
            roads = {
                sommet_0: [(sommet_1, 21, 2), (sommet_2, 12, 4)],
                sommet_1: [(sommet_0, 74, 2), (sommet_2, 32, 1)],
                ...
            }
    start : sommet
        Sommet de départ du réseau.
    end : sommet
        Sommet d'arrivée du réseau.
    """

    def __init__(self, roads={}, start=None, end=None):
        """
        Initialise le réseau depuis un dictionnaire de routes.

        Paramètres
        ----------
        roads : dict, optionnel
            Liste d'adjacence de la forme {sommet: [(voisin, longueur, fatigue), ...]}.
            Par défaut, dictionnaire vide.
        start : sommet, optionnel
            Sommet de départ. Par défaut None.
        end : sommet, optionnel
            Sommet d'arrivée. Par défaut None.
        """
        self._roads = roads
        self.start = start
        self.end = end

    def __str__(self):
        """
        Retourne une représentation textuelle du réseau.

        Retourne
        --------
        str
            Chaîne décrivant le nombre de sommets et la liste d'adjacence complète.
        """
        output = f"A network with {len(self._roads)} nodes and the following adjacency list:\n"
        return output + self._roads.__str__()

    @classmethod
    def from_file(cls, filename: str):
        """
        Crée une instance de Network depuis un fichier de description de réseau.

        Format du fichier : une arête par ligne (départ arrivée longueur fatigue).
        Le graphe est construit comme non orienté : chaque arête est ajoutée
        dans le sens i → j uniquement (le sens j → i doit être explicitement
        présent dans le fichier si nécessaire).

        Paramètres
        ----------
        filename : str
            Chemin vers le fichier texte décrivant le réseau.

        Retourne
        --------
        Network
            Instance de Network chargée depuis le fichier.
        """
        # Initialisation de la liste d'adjacence
        roads = {}
        with open(filename, "r") as testcase:
            # Lecture de la première ligne : nombre d'arêtes, départ, arrivée
            nb, start, end = testcase.readline().strip().split()
            for _ in range(int(nb)):
                # Lecture de chaque arête : sommet i, sommet j, longueur, fatigue
                i, j, l, f = testcase.readline().strip().split()
                l, f = int(l), int(f)
                # Ajout de l'arête i → j avec longueur et fatigue
                roads.setdefault(i, []).append((j, l, f))
                # Ajout de j comme sommet sans voisins s'il n'existe pas encore
                roads.setdefault(j, [])
        return cls(roads=roads, start=start, end=end)

    def build_simple_graph(self):
        """
        Construit un objet Graph depuis le réseau en ignorant le coefficient de fatigue.

        Pour chaque sommet, seules la destination et la longueur sont conservées ;
        la fatigue est écartée. Le graphe retourné est compatible avec les algorithmes
        de plus court chemin standards (Dijkstra).

        Retourne
        --------
        Graph
            Instance de Graph dont les arêtes sont de la forme (voisin, longueur).
        """
        graph = {}
        for sommet, voisins in self._roads.items():
            # On ignore le troisième élément (fatigue) de chaque tuple
            graph[sommet] = [(a, b) for a, b, c in voisins]
        return Graph(graph)

    def build_graph_implicit(network):
        """
        Construit un GraphImplicit pour le réseau donné, en tenant compte de la fatigue.

        Chaque état du graphe implicite est un couple (sommet, fatigue_accumulée).
        Le coût d'une transition est : longueur × (1 + fatigue_courante),
        ce qui pénalise les chemins parcourus avec une fatigue élevée.

        Les états dont la fatigue dépasse Fmax (somme de toutes les fatigues du réseau)
        sont ignorés, ce qui garantit la finitude de l'espace d'exploration.

        Paramètres
        ----------
        network : Network
            Le réseau routier depuis lequel construire le graphe implicite.

        Retourne
        --------
        GraphImplicit
            Instance de GraphImplicit dont les voisins sont calculés à la volée.
        """
        # Calcul de la fatigue maximale théorique : somme de toutes les fatigues du réseau
        Fmax = sum(f for voisins in network._roads.values() for (_, _, f) in voisins)

        # Fonction de voisinage : retourne les voisins accessibles depuis un état (sommet, fatigue)
        def neighbours_fn(state):
            """
            Calcule les voisins d'un état (sommet, fatigue_accumulée).

            Paramètres
            ----------
            state : tuple (sommet, fatigue_accumulée)
                L'état courant dans le graphe étendu.

            Retourne
            --------
            list
                Liste de tuples ((voisin, nouvelle_fatigue), coût) représentant
                les transitions accessibles depuis l'état courant.
            """
            node, F = state
            resultat = []
            for neighbor, length, fatigue in network._roads.get(node, []):
                # Calcul de la fatigue accumulée après emprunt de cette route
                new_F = F + fatigue
                # On ignore les états dont la fatigue dépasse la borne maximale
                if new_F > Fmax:
                    continue
                etat_voisin = (neighbor, new_F)
                # Coût de la transition : longueur pénalisée par la fatigue courante
                cost = length * (1 + F)
                resultat.append((etat_voisin, cost))
            return resultat

        # Retourne l'objet GraphImplicit utilisant la fonction de voisinage définie ci-dessus
        return GraphImplicit(neighbours_fn)

    def build_reversed_simple_graph(self):
    """
    Construit le graphe simple inversé (arêtes retournées, sans fatigue).

    Utile pour le pré-traitement de l'heuristique A* : en faisant tourner
    Dijkstra depuis vt sur ce graphe inversé, on obtient pour chaque sommet
    sa distance minimale (sans fatigue) jusqu'à vt.

    Retourne
    --------
    Graph
        Graphe simple dont les arêtes sont retournées (j → i au lieu de i → j).
    """
    reversed_graph = {}
    for sommet, voisins in self._roads.items():
        reversed_graph.setdefault(sommet, [])
        for voisin, longueur, fatigue in voisins:
            reversed_graph.setdefault(voisin, []).append((sommet, longueur))
    return Graph(reversed_graph)


def build_reversed_implicit_graph(self):
    """
    Construit le graphe implicite étendu inversé du réseau.

    Dans le graphe inversé étendu, une arête (u, Fu) → (v, Fv) du graphe
    original devient (v, Fv) → (u, Fu) avec le même coût length × (1 + Fu).

    Utile pour le calcul du point de repos optimal : un Dijkstra depuis
    (vt, 0) sur ce graphe donne, pour chaque état (r, 0), le temps minimal
    pour aller de r (fatigue 0) jusqu'à vt dans le graphe original.

    Retourne
    --------
    GraphImplicit
        Graphe implicite inversé étendu.
    """
    Fmax = sum(f for voisins in self._roads.values() for (_, _, f) in voisins)

    def neighbours_fn_reversed(state):
        node, F_node = state
        result = []
        for predecessor, voisins in self._roads.items():
            for neighbor, length, fatigue_edge in voisins:
                if neighbor != node:
                    continue
                F_pred = F_node - fatigue_edge
                if F_pred < 0 or F_pred > Fmax:
                    continue
                cost = length * (1 + F_pred)
                result.append(((predecessor, F_pred), cost))
        return result

    return GraphImplicit(neighbours_fn_reversed)


    def find_optimal_rest_point(self):
    """
    Trouve le sommet optimal où placer un unique lieu de repos.

    Le lieu de repos remet la fatigue de l'agent à zéro. On cherche le
    sommet r minimisant T(r) = d_forward(r) + d_backward(r), où :
        - d_forward(r)  = temps minimal de (vs, 0) à (r, *) dans le graphe étendu
        - d_backward(r) = temps minimal de (r, 0) à (vt, *) = dist inversé depuis (vt, 0)

    Complexité : O(m · Fmax · log(n · Fmax)) — deux passes de Dijkstra.

    Retourne
    --------
    best_rest : sommet
        Sommet optimal pour le lieu de repos.
    best_time : float
        Temps minimal avec lieu de repos.
    time_without_rest : float
        Temps minimal sans lieu de repos (référence).
    results : list of (sommet, float)
        Tous les candidats triés par temps total croissant.
    """
    # Passe aller : Dijkstra depuis (vs, 0)
    implicit_graph = Network.build_graph_implicit(self)
    dist_forward = implicit_graph.shortest_path((self.start, 0))

    # Pour chaque sommet, temps minimal toutes fatigues confondues
    d_forward = {}
    for (node, f), dist in dist_forward.items():
        if dist < d_forward.get(node, float('inf')):
            d_forward[node] = dist

    time_without_rest = d_forward.get(self.end, float('inf'))

    # Passe retour : Dijkstra depuis (vt, 0) sur le graphe inversé
    reversed_graph = self.build_reversed_implicit_graph()
    dist_backward = reversed_graph.shortest_path((self.end, 0))

    # d_backward(r) = dist_backward[(r, 0)] : l'agent repart de r avec fatigue 0
    d_backward = {node: dist
                  for (node, f), dist in dist_backward.items()
                  if f == 0}

    # Calcul de T(r) pour chaque candidat
    results = sorted(
        [(r, d_forward.get(r, float('inf')) + d_backward.get(r, float('inf')))
         for r in self._roads],
        key=lambda x: x[1]
    )

    best_rest, best_time = results[0] if results else (None, float('inf'))
    return best_rest, best_time, time_without_rest, results