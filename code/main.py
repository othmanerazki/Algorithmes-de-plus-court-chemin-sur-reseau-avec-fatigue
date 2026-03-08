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