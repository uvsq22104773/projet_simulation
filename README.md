# Simulation de Serveurs et Gestion de Requêtes

Ce programme simule un système de serveurs traitant des requêtes arrivant à une fréquence déterminée, avec gestion des files d'attente et des événements. L'objectif est de simuler le traitement des requêtes et d'analyser les performances du système en fonction de divers paramètres, tels que le nombre de serveurs, le taux d'arrivée des requêtes et le taux de perte.

## Structure du Programme

### Fonction `groupe_serveur(indice_serveur, C)`
Cette fonction détermine le groupe auquel appartient un serveur donné. Les serveurs sont regroupés en fonction du paramètre `C`.

- **Arguments** :
  - `indice_serveur` : Indice du serveur (int)
  - `C` : Nombre de groupes (int)

- **Retourne** : Le groupe auquel appartient le serveur (int)

### Fonction `simulation_serveur(C, lambd, nb_requetes_max)`
Simule le comportement du système avec un certain nombre de serveurs, un taux d'arrivée des requêtes (`lambd`) et un nombre maximum de requêtes à traiter.

- **Arguments** :
  - `C` : Nombre de groupes de serveurs (int)
  - `lambd` : Taux d'arrivée des requêtes (float)
  - `nb_requetes_max` : Nombre maximal de requêtes à traiter (int)

- **Retourne** :
  - Le nombre de requêtes traitées (int)
  - Le taux de perte des requêtes (float)
  - Une liste des temps de réponse des requêtes (list)

### Fonction `optimal_C_lambda(nbr_requetes, lambd = 1, ls_C = [1, 2, 3, 6])`
Détermine le meilleur nombre de groupes de serveurs (`C`) pour un taux d'arrivée donné (`lambd`) en fonction du temps moyen de réponse et du taux de perte.

- **Arguments** :
  - `nbr_requetes` : Nombre de requêtes à traiter (int)
  - `lambd` : Taux d'arrivée des requêtes (float)
  - `ls_C` : Liste des valeurs possibles pour `C` (list)

- **Retourne** : Une liste de résultats pour chaque valeur de `C` avec le temps moyen de réponse, l'intervalle de confiance et le taux de perte.

### Fonction `graphique_temps_reponse(nbr_requetes, ls_C = [1, 2, 3, 6], lambdas = [...])`
Trace un graphique du temps de réponse moyen en fonction de `λ` (le taux d'arrivée des requêtes) pour plusieurs valeurs de `C`.

- **Arguments** :
  - `nbr_requetes` : Nombre de requêtes à traiter (int)
  - `ls_C` : Liste des valeurs de `C` à tester (list)
  - `lambdas` : Liste des valeurs de `λ` (list)

- **Retourne** : Un graphique du temps de réponse moyen avec des intervalles de confiance à 95%.

### Fonction `graphique_temps_reponse_precis(nbr_requetes, ls_C = [1, 2, 3, 6], lambd_min = 1, lambd_max = 5, precision = 20)`
Trace un graphique du temps de réponse moyen avec une précision donnée sur l'intervalle `[lambd_min, lambd_max]` pour plusieurs valeurs de `C`.

- **Arguments** :
  - `nbr_requetes` : Nombre de requêtes à traiter (int)
  - `ls_C` : Liste des valeurs de `C` à tester (list)
  - `lambd_min` : Valeur minimale pour `λ` (float)
  - `lambd_max` : Valeur maximale pour `λ` (float)
  - `precision` : Précision du calcul (int)

- **Retourne** : Un graphique du temps de réponse moyen pour l'intervalle spécifié de `λ`.

### Fonction `graphique_taux_perte(nbr_requetes, ls_C = [1, 2, 3, 6], lambdas = [...])`
Trace un graphique du taux de perte en fonction de `λ` pour plusieurs valeurs de `C`.

- **Arguments** :
  - `nbr_requetes` : Nombre de requêtes à traiter (int)
  - `ls_C` : Liste des valeurs de `C` à tester (list)
  - `lambdas` : Liste des valeurs de `λ` (list)

- **Retourne** : Un graphique du taux de perte avec des intervalles de confiance à 95%.

### Fonction `graphique_taux_perte_precis(nbr_requetes, ls_C = [1, 2, 3, 6], lambd_min = 1, lambd_max = 5, precision = 20)`
Trace un graphique du taux de perte pour `λ` dans l'intervalle `[lambd_min, lambd_max]` avec une précision donnée.

- **Arguments** :
  - `nbr_requetes` : Nombre de requêtes à traiter (int)
  - `ls_C` : Liste des valeurs de `C` à tester (list)
  - `lambd_min` : Valeur minimale pour `λ` (float)
  - `lambd_max` : Valeur maximale pour `λ` (float)
  - `precision` : Précision du calcul (int)

- **Retourne** : Un graphique du taux de perte pour l'intervalle spécifié de `λ`.

### Fonction `optimal_C_intervalle_lambdas(nbr_requetes, ls_C, lambd_min = 1, lambd_max = 5, precision = 20)`
Cherche et affiche dans un tableau le meilleur `C` pour des valeurs de `λ` sur l'intervalle `[lambd_min, lambd_max]` avec une précision donnée.

- **Arguments** :
  - `nbr_requetes` : Nombre de requêtes à traiter (int)
  - `ls_C` : Liste des valeurs de `C` à tester (list)
  - `lambd_min` : Valeur minimale pour `λ` (float)
  - `lambd_max` : Valeur maximale pour `λ` (float)
  - `precision` : Précision du calcul (int)

- **Retourne** : Un tableau contenant les meilleurs résultats pour chaque valeur de `λ`.

### Fonction `affiche_tableau(data)`
Affiche un tableau des résultats pour déterminer le meilleur `C` pour un `λ` donné.

- **Arguments** :
  - `data` : Données de résultats à afficher (list)

- **Retourne** : Un tableau lisible des résultats de la simulation.

## Utilisation

### 1. Lancer la simulation pour analyser les temps de réponse :

```
graphique_temps_reponse(100000, ls_C, lambdas)
````

### 2. Afficher les temps de réponse avec une précision fine sur l’intervalle de λ :

```
graphique_temps_reponse_precis(100000, ls_C, 1, 5, 100)
```

### 3. Analyser le taux de perte en fonction de λ :

```
graphique_taux_perte(100000, ls_C, lambdas)
```

### 4. Analyser le taux de perte avec une précision fine :

```
graphique_taux_perte_precis(100000, ls_C, 1, 5, 20)
```

### 5. Trouver le meilleur C pour un taux d’arrivée de λ donné :

```
affiche_tableau(optimal_C_lambda(100000, 1))
```

### 6. Chercher le meilleur C sur un intervalle de λ :

```
optimal_C_intervalle_lambdas(100000, ls_C, 0, 3, 10)
```

## Dépendances

Ce programme nécessite les bibliothèques suivantes :
- `heapq` : Pour la gestion de la file d’attente des événements.
- `random` : Pour la génération de nombres aléatoires.- matplotlib : Pour la génération de graphiques.
- `numpy` : Pour les calculs statistiques.

Vous pouvez installer les dépendances nécessaires avec pip :

```
pip install matplotlib numpy
```

## Conclusion

Ce programme permet de simuler un système de serveurs avec des requêtes arrivant selon un processus de Poisson, d’analyser le comportement du système en fonction de divers paramètres, et de visualiser les performances à travers des graphiques.
