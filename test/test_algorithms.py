import sys
from pathlib import Path
import time

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))
NET_DIR = ROOT / "examples"

import pytest
from network import Network


# -------------------------------------------------------
# Partie 1.1 : graphe simple (sans fatigue)
# -------------------------------------------------------

def test_simple_graph_small():
    """Dijkstra sans fatigue sur small.txt."""
    network = Network.from_file(NET_DIR / "small.txt")
    graphe = network.build_simple_graph()
    distances = graphe.shortest_path(network.start)
    assert distances[network.end] == 55  # lozere→ensae(10) + ensae→saclay(45)

def test_naive_vs_optimized_small():
    """Les deux Dijkstra doivent donner le même résultat."""
    network = Network.from_file(NET_DIR / "small.txt")
    graphe = network.build_simple_graph()
    dist_naive, _ = graphe.shortest_path_naive(network.start)
    dist_opt = graphe.shortest_path(network.start)
    assert dist_naive[network.end] == dist_opt[network.end]

# -------------------------------------------------------
# Partie 1.2 : graphe implicite (avec fatigue)
# -------------------------------------------------------

def test_implicit_graph_small():
    """Dijkstra avec fatigue sur small.txt — résultat attendu : 125."""
    network = Network.from_file(NET_DIR / "small.txt")
    graphe_implicite = network.build_graph_implicit()
    distances = graphe_implicite.shortest_path((network.start, 0))

    # On cherche le meilleur temps parmi tous les états (saclay, *)
    best = min(
        (t for (node, f), t in distances.items() if node == network.end),
        default=float('inf')
    )
    assert best == 125

# -------------------------------------------------------
# Partie 2.1 : pruning Pareto
# -------------------------------------------------------

def test_pruning_small():
    """Pruning Pareto doit donner 125 sur small.txt."""
    network = Network.from_file(NET_DIR / "small.txt")
    graphe_implicite = network.build_graph_implicit()
    result = graphe_implicite.shortest_path_with_pruning(
        (network.start, 0), network.end
    )
    assert result == 125

# -------------------------------------------------------
# Partie 2.2 : A*
# -------------------------------------------------------

def test_astar_small():
    """A* doit donner le même résultat que Dijkstra avec fatigue."""
    network = Network.from_file(NET_DIR / "small.txt")
    graphe_implicite = network.build_graph_implicit()

    # Heuristique : Dijkstra inversé sans fatigue
    graphe_inverse = network.build_reversed_simple_graph()
    h_values = graphe_inverse.shortest_path(network.end)

    def heuristic(state):
        node, _ = state
        return h_values.get(node, float('inf'))

    result = graphe_implicite.astar((network.start, 0), network.end, heuristic)
    assert result == 125

# -------------------------------------------------------
# Partie 3 : point de repos
# -------------------------------------------------------

def test_rest_point_small():
    """Le temps avec repos ne doit pas être pire que sans repos."""
    network = Network.from_file(NET_DIR / "small.txt")
    best_rest, best_time, time_without_rest, results = network.find_optimal_rest_point()

    # Sanité : le repos ne peut pas être pire que sans repos
    assert best_time <= time_without_rest
    # Le sommet optimal doit exister dans le réseau
    assert best_rest in network._roads

# -------------------------------------------------------
# Mesure des temps d'exécution
# -------------------------------------------------------

def test_timing_small(capsys):
    """Affiche les temps d'exécution de chaque algorithme sur small.txt."""
    network = Network.from_file(NET_DIR / "small.txt")

    # Dijkstra simple
    t0 = time.perf_counter()
    graphe = network.build_simple_graph()
    graphe.shortest_path(network.start)
    t1 = time.perf_counter()

    # Dijkstra avec fatigue (graphe implicite)
    t2 = time.perf_counter()
    gi = network.build_graph_implicit()
    gi.shortest_path((network.start, 0))
    t3 = time.perf_counter()

    # Pruning Pareto
    t4 = time.perf_counter()
    gi.shortest_path_with_pruning((network.start, 0), network.end)
    t5 = time.perf_counter()

    # Point de repos
    t6 = time.perf_counter()
    network.find_optimal_rest_point()
    t7 = time.perf_counter()

    with capsys.disabled():
        print(f"\n--- Temps d'exécution sur small.txt ---")
        print(f"  Dijkstra simple       : {(t1-t0)*1000:.3f} ms")
        print(f"  Dijkstra avec fatigue : {(t3-t2)*1000:.3f} ms")
        print(f"  Pruning Pareto        : {(t5-t4)*1000:.3f} ms")
        print(f"  Point de repos        : {(t7-t6)*1000:.3f} ms")


def test_timing_medium(capsys):
    """Affiche les temps d'exécution sur medium-smallfatigue.txt."""
    network = Network.from_file(NET_DIR / "medium-smallfatigue.txt")

    t0 = time.perf_counter()
    graphe = network.build_simple_graph()
    graphe.shortest_path(network.start)
    t1 = time.perf_counter()

    t2 = time.perf_counter()
    gi = network.build_graph_implicit()
    gi.shortest_path((network.start, 0))
    t3 = time.perf_counter()

    t4 = time.perf_counter()
    gi.shortest_path_with_pruning((network.start, 0), network.end)
    t5 = time.perf_counter()

    t6 = time.perf_counter()
    network.find_optimal_rest_point()
    t7 = time.perf_counter()

    with capsys.disabled():
        print("\n--- Temps d'exécution sur medium-smallfatigue.txt ---")
        print(f"  Dijkstra simple       : {(t1-t0)*1000:.3f} ms")
        print(f"  Dijkstra avec fatigue : {(t3-t2)*1000:.3f} ms")
        print(f"  Pruning Pareto        : {(t5-t4)*1000:.3f} ms")
        print(f"  Point de repos        : {(t7-t6)*1000:.3f} ms")



def test_timing_pruning_tous_fichiers(capsys):
    """Compare le pruning Pareto sur tous les fichiers disponibles."""
    fichiers = [
        "small.txt",
        "medium-smallfatigue.txt",
        "large-smallfatigue.txt",
    ]

    with capsys.disabled():
        print("\n--- Pruning Pareto selon le fichier ---")
        for nom in fichiers:
            try:
                network = Network.from_file(NET_DIR / nom)
                gi = network.build_graph_implicit()
                t0 = time.perf_counter()
                result = gi.shortest_path_with_pruning((network.start, 0), network.end)
                t1 = time.perf_counter()
                print(f"  {nom:<35} : {(t1-t0)*1000:.3f} ms  (résultat={result})")
            except FileNotFoundError:
                print(f"  {nom:<35} : fichier introuvable")


def test_affichage_brut_small(capsys):
    """Affiche exactement ce que retourne chaque algorithme sur small.txt."""
    network = Network.from_file(NET_DIR / "small.txt")

    with capsys.disabled():
        print("\nReseau charge : start =", network.start, ", end =", network.end)

        # Dijkstra simple
        print("\n--- Dijkstra simple (sans fatigue) ---")
        graphe = network.build_simple_graph()
        distances = graphe.shortest_path(network.start)
        print(distances)

        # Dijkstra naif
        print("\n--- Dijkstra naif (sans fatigue) ---")
        dist_naive, precedent = graphe.shortest_path_naive(network.start)
        print("distances :", dist_naive)
        print("precedent :", precedent)

        # Dijkstra avec fatigue
        print("\n--- Dijkstra avec fatigue (graphe implicite) ---")
        gi = network.build_graph_implicit()
        distances_fatigue = gi.shortest_path((network.start, 0))
        print(distances_fatigue)

        # Pruning Pareto
        print("\n--- Pruning Pareto ---")
        result = gi.shortest_path_with_pruning((network.start, 0), network.end)
        print(result)

        # A*
        print("\n--- A* ---")
        h_values = network.build_reversed_simple_graph().shortest_path(network.end)
        result_astar = gi.astar(
            (network.start, 0), network.end,
            lambda s: h_values.get(s[0], float('inf'))
        )
        print(result_astar)

        # Point de repos
        print("\n--- Point de repos ---")
        best_rest, best_time, time_without_rest, results = network.find_optimal_rest_point()
        print("Sans repos         :", time_without_rest)
        print("Meilleur sommet    :", best_rest)
        print("Temps avec repos   :", best_time)
        print("Tous les candidats :", results)
