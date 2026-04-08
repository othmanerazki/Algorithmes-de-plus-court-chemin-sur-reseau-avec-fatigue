"""
Script principal de résolution du plus court chemin sur un réseau routier.

Ce script charge un réseau depuis un fichier texte, construit le graphe
associé, puis calcule la distance minimale entre le sommet de départ et
le sommet d'arrivée en utilisant l'algorithme de Dijkstra.

Modules utilisés
----------------
network : module contenant la classe Network
    Permet de charger et représenter un réseau routier depuis un fichier.
graph : module contenant la classe Graph
    Fournit les structures de graphe et les algorithmes de plus court chemin.

Fichier d'entrée
----------------
Le fichier réseau (ex. "examples/large-nofatigue.txt") décrit les sommets,
les arêtes et leurs poids. Le format attendu est défini dans la classe Network.

Résultat
--------
Affiche la distance minimale entre le sommet de départ (network.start)
et le sommet d'arrivée (network.end).
"""

from network import Network
from graph import Graph

# Chemin vers le fichier décrivant le réseau routier à analyser
fichier_reseau = "examples/large-nofatigue.txt"

# Chargement du réseau depuis le fichier : parse les sommets, arêtes et poids
reseau = Network.from_file(fichier_reseau)

# Construction du graphe simple à partir du réseau
# (sans prise en compte de la fatigue)
graphe = reseau.build_simple_graph()

# Récupération du sommet de départ défini dans le fichier réseau
sommet_depart = reseau.start

# Calcul des distances minimales depuis le sommet de départ vers tous les autres sommets
# via l'algorithme de Dijkstra optimisé (file de priorité / tas binaire)
distances = graphe.shortest_path(sommet_depart)

# Récupération et affichage de la distance minimale jusqu'au sommet d'arrivée
# Retourne None si le sommet d'arrivée n'est pas atteignable depuis le départ
print("Résultat large-nofatigue.txt :", distances.get(reseau.end))

# Partie 2.1 : Pruning Pareto 
graphe_implicite = Network.build_graph_implicit(reseau)
start_state = (reseau.start, 0)

temps_pruning = graphe_implicite.shortest_path_with_pruning(start_state, reseau.end)
print("Temps minimal (avec pruning Pareto) :", temps_pruning)

# Partie 2.2 : A* 
# Pré-traitement : Dijkstra inversé depuis vt sur le graphe simple
graphe_inverse = reseau.build_reversed_simple_graph()
h_values = graphe_inverse.shortest_path(reseau.end)  # distances brutes jusqu'à vt

# Heuristique admissible : distance sans fatigue depuis le sommet courant jusqu'à vt
def heuristic(state):
    node, fatigue = state
    # Si le sommet n'est pas atteignable dans le graphe inverse, heuristique = infini
    return h_values.get(node, float('inf'))

temps_astar = graphe_implicite.astar(start_state, reseau.end, heuristic)
print("Temps minimal (A*) :", temps_astar)

def solve_multimission(network, missions):
    """
    Résout le problème de plusieurs missions enchaînées pour un seul agent.
 
    L'agent démarre au point de départ de la première mission avec fatigue 0.
    Il enchaîne les missions dans l'ordre imposé. La fatigue s'accumule sur
    l'ensemble du trajet (y compris les déplacements entre missions).
 
    Le temps total est la somme des temps de chaque segment :
        - déplacement de v(i)_t à v(i+1)_s  (segment inter-mission)
        - mission v(i+1)_s -> v(i+1)_t
 
    Paramètres
    ----------
    network : Network
        Le réseau routier.
    missions : list of tuples (start, end)
        Liste ordonnée des missions. Chaque mission est un couple (sommet_départ, sommet_arrivée).
        Exemple : [('A', 'B'), ('C', 'D'), ('E', 'F')]
 
    Retourne
    --------
    total_time : float
        Temps total minimal pour accomplir toutes les missions dans l'ordre.
        Retourne float('inf') si une mission est inatteignable.
    mission_times : list of float
        Temps de chaque segment (inter-mission + mission) dans l'ordre.
    """
    # Construction du graphe implicite avec fatigue (réutilisation de build_graph_implicit)
    graphe_implicite = Network.build_graph_implicit(network)
 
    # Monkey-patch de la méthode sur l'instance (ou l'appeler directement)
    import types
    graphe_implicite.shortest_path_with_pruning_from_state = types.MethodType(
        shortest_path_with_pruning_from_state, graphe_implicite
    )
 
    total_time = 0.0
    mission_times = []
 
    # État initial : sommet de départ de la première mission, fatigue = 0
    first_start, first_end = missions[0]
    current_state = (first_start, 0)
 
    for i, (ms, me) in enumerate(missions):
        # --- Segment inter-mission : se déplacer jusqu'au départ de la mission i ---
        # (pour i=0, current_state est déjà (ms, 0), donc pas de déplacement)
        if current_state[0] != ms:
            transit_time, current_state = graphe_implicite.shortest_path_with_pruning_from_state(
                current_state, ms
            )
            if current_state is None:
                print(f"Mission {i+1} : impossible d'atteindre le départ {ms}.")
                return float('inf'), mission_times
            total_time += transit_time
            mission_times.append(('transit', ms, transit_time))
 
        # --- Mission i : aller de ms à me ---
        mission_time, current_state = graphe_implicite.shortest_path_with_pruning_from_state(
            current_state, me
        )
 
        if current_state is None:
            print(f"Mission {i+1} ({ms} -> {me}) : impossible à accomplir.")
            return float('inf'), mission_times
 
        total_time += mission_time
        mission_times.append(('mission', f"{ms}->{me}", mission_time))
        print(f"  Mission {i+1} ({ms} -> {me}) : temps = {mission_time:.2f} "
              f"| fatigue accumulée = {current_state[1]}")
 
    return total_time, mission_times
 

 # Partie 3.3 : Extension — Point de repos optimal
print("\n--- Extension : Point de repos ---")

best_rest, best_time, time_without_rest, all_results = reseau.find_optimal_rest_point()

print(f"Temps sans lieu de repos     : {time_without_rest}")
print(f"Sommet optimal pour le repos : {best_rest}")
print(f"Temps avec lieu de repos     : {best_time}")

if best_time < time_without_rest:
    gain = time_without_rest - best_time
    print(f"Gain de temps               : {gain:.4f} ({100*gain/time_without_rest:.1f}%)")
else:
    print("Le lieu de repos n'améliore pas le temps (réseau sans fatigue).")

print("\nTop 5 des emplacements de repos :")
for i, (sommet, temps) in enumerate(all_results[:5], 1):
    print(f"  {i}. Sommet {sommet:>6}  →  temps total = {temps}")


from visualize import visualize_network, visualize_path

# Utilise shortest_path_naïve car elle retourne aussi le dictionnaire precedent
distances, precedent = graphe.shortest_path_naïve(reseau.start)

# Génère les deux images
visualize_network(reseau, output="network")
visualize_path(reseau, precedent, reseau.start, reseau.end,
               distances=distances, output="shortest_path")
    