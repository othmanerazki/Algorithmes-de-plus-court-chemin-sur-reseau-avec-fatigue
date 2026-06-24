# Plus Court Chemin sur un Réseau avec Fatigue
**ENSAE Paris — Projet de Programmation 2025–2026**  
*Othmane Razki & Jean Palazuelo — Encadrant : Simon Mauras*

---

## Présentation

Ce projet implémente et compare plusieurs algorithmes de plus court chemin sur un graphe orienté pondéré représentant un réseau routier. Chaque arête possède deux attributs : une **longueur** et un **coefficient de fatigue** qui augmente le coût de parcours au fur et à mesure que l'agent accumule de la fatigue.

L'objectif est de trouver le chemin minimisant le temps total de trajet entre un sommet de départ `vs` et un sommet d'arrivée `vt`, où :

$$\text{temps}(v_0, \ldots, v_k) = \sum_{i=1}^{k} \ell(v_{i-1}, v_i) \times \left(1 + \sum_{j=1}^{i-1} f(v_{j-1}, v_j)\right)$$

---

## Fonctionnalités

### Partie 1 — Plus Court Chemin de Base
- **Dijkstra naïf** `O(n² + m)` — sans file de priorité
- **Dijkstra optimisé** `O((n + m) log n)` — avec tas binaire
- **Construction du graphe étendu** — la fatigue est encodée comme dimension d'état `(sommet, fatigue)`
- **Graphe implicite** (`GraphImplicit`) — voisins calculés à la volée pour éviter l'explosion mémoire

### Partie 2 — Améliorations Algorithmiques
- **Élagage Pareto (pruning)** — élimine les états Pareto-dominés `(sommet, fatigue, temps)` lors de l'exploration ; réduit le temps d'exécution de ~4850ms à ~7ms sur les instances moyennes (gain ×700)
- **Algorithme A\*** — recherche guidée par une heuristique admissible (Dijkstra sans fatigue depuis l'arrivée, précalculé sur le graphe inversé)

### Partie 3 — Extension : Point de Repos Optimal
- Trouve le sommet optimal `r` où placer un lieu de repos remettant la fatigue à zéro
- Minimise `T(r) = d_aller(r) + d_retour(r)` via deux passes de Dijkstra (aller + graphe implicite inversé)

---

## Structure du Projet

```
ensae-prog26/
├── code/
│   ├── graph.py          # Classes Graph et GraphImplicit, tous les algorithmes
│   ├── network.py        # Classe Network, parsing des fichiers, constructeurs de graphes
│   └── main.py           # Script principal
├── test/
│   ├── test_algorithms.py                  # Suite de tests pytest
│   ├── test_network_from_file.py           # Suite unittest
│   └── test_network_from_file_pytest.py
├── examples/
│   ├── small.txt
│   ├── medium-smallfatigue.txt
│   └── large-nofatigue.txt
└── Projet_de_Programmation_ENSAE.pdf
```

---

## Lancement

```bash
# Cloner le dépôt
git clone https://github.com/othmanerazki/ensae-prog26.git
cd ensae-prog26

# Lancer le script principal
python code/main.py

# Lancer les tests
pytest test/test_algorithms.py -v
```

Aucune dépendance externe — bibliothèque standard Python uniquement (`heapq`, `pathlib`).

---

## Résultats sur `small.txt` (lozere → saclay)

| Algorithme | Résultat |
|---|---|
| Dijkstra (sans fatigue) | 55 |
| Dijkstra (avec fatigue) | 125 |
| Élagage Pareto | 125 |
| A\* | 125 |
| Avec lieu de repos en `ensae` | 55 |

---

## Comparaison des Performances

| Fichier | Dijkstra simple | Dijkstra + fatigue | Élagage Pareto |
|---|---|---|---|
| `small.txt` | 0.01 ms | 0.013 ms | 0.017 ms |
| `medium-smallfatigue.txt` | 0.55 ms | 4850 ms | **6.9 ms** |

L'élagage Pareto offre un **gain de ×700** sur les instances moyennes en éliminant précocement les états dominés.

---

## Concepts Utilisés

`Dijkstra` · `A*` · `Dominance Pareto` · `Graphe étendu` · `Graphe implicite` · `Inversion de graphe` · `heapq` · `POO (héritage)`
