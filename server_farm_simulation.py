import heapq
import random
import matplotlib.pyplot as plt
import numpy as np

def groupe_serveur(indice_serveur, C):
    K = 12 // C
    return indice_serveur // K

def simulation_serveur(C, lambd, nb_requetes_max):
    serveurs = [True] * 12  # True = libre, False = occupé
    file_routeur = []
    file_bloque = False

    ls_temps_requetes = []

    taux_perte = 0
    nbr_requetes = 0

    # Temps constant pour le traitement du routeur
    temps_traitement_routeur = (C - 1) / C

    # Durées de traitement serveurs selon C
    parametres_serveur = {
        1: 4/20,
        2: 7/20,
        3: 10/20,
        6: 14/20
    }

    evenements = []
    temps_courant = 0
    nb_requetes_traite_bloque = 0

    # Ajouter premier événement
    delta_t = random.expovariate(lambd)
    nouvelle_categorie = random.choice(range(C))
    nouvelle_requete = (nouvelle_categorie, temps_courant + delta_t)
    heapq.heappush(evenements, (temps_courant + delta_t, 'ARRIVEE_REQUETE', nouvelle_requete))

    while evenements and nbr_requetes < nb_requetes_max:
        t_event, type_event, data = heapq.heappop(evenements)
        temps_courant = t_event

        if type_event == 'ARRIVEE_REQUETE':
            categorie, temps_arrivee = data
            nbr_requetes += 1

            # Ajouter dans file routeur
            if len(file_routeur) < 100:
                file_routeur.append((categorie, temps_arrivee))
                # Planifier FIN_TRAITEMENT_ROUTEUR si la file était vide
                if len(file_routeur) == 1:
                    heapq.heappush(evenements, (temps_courant + temps_traitement_routeur, 'FIN_TRAITEMENT_ROUTEUR', file_routeur[0]))
            else:
                # Requête perdue
                taux_perte += 1
            # Planifier prochaine ARRIVEE_REQUETE
            delta_t = random.expovariate(lambd)
            nouvelle_categorie = random.choice(range(C))
            nouvelle_requete = (nouvelle_categorie, temps_courant + delta_t)
            heapq.heappush(evenements, (temps_courant + delta_t, 'ARRIVEE_REQUETE', nouvelle_requete))

        elif type_event == 'FIN_TRAITEMENT_ROUTEUR':
            categorie, temps_arrivee = data

            serveur_libre = None
            for i in range(12):
                if groupe_serveur(i, C) == categorie and serveurs[i]:
                    serveur_libre = i
                    break

            if serveur_libre is not None:
                # Serveur trouvé
                serveurs[serveur_libre] = False
                # Retirer la requête de la file routeur
                file_routeur.pop(0)
                file_bloque = False
                # Planifier FIN_TRAITEMENT_SERVEUR
                temps_traitement_serveur = random.expovariate(parametres_serveur[C])
                heapq.heappush(evenements, (temps_courant + temps_traitement_serveur, 'FIN_TRAITEMENT_SERVEUR', (categorie, temps_arrivee, serveur_libre)))
                # Planifier potentiellement FIN_TRAITEMENT_ROUTEUR pour la prochaine requête si requête dans la file
                if file_routeur:
                    heapq.heappush(evenements, (temps_courant + temps_traitement_routeur, 'FIN_TRAITEMENT_ROUTEUR', file_routeur[0]))
            else:
                # Pas de serveur disponible, on bloque la file
                file_bloque = True

        elif type_event == 'FIN_TRAITEMENT_SERVEUR':
            categorie, temps_arrivee, indice_serveur = data

            # Libérer serveur
            serveurs[indice_serveur] = True

            ls_temps_requetes.append(temps_courant - temps_arrivee)

            # Débloquer potentiellement une requête en file
            if file_bloque:
                categorie, temps_arrivee = file_routeur[0]
                if categorie == groupe_serveur(indice_serveur, C):
                    # Serveur libéré pour cette requête
                    serveurs[indice_serveur] = False
                    file_routeur.pop(0)
                    file_bloque = False
                    # Planifier FIN_TRAITEMENT_SERVEUR
                    temps_traitement_serveur = random.expovariate(parametres_serveur[C])
                    heapq.heappush(evenements, (temps_courant + temps_traitement_serveur, 'FIN_TRAITEMENT_SERVEUR', (categorie, temps_arrivee, indice_serveur)))
                    if file_routeur:
                        heapq.heappush(evenements, (temps_courant + temps_traitement_routeur, 'FIN_TRAITEMENT_ROUTEUR', file_routeur[0]))

    return nbr_requetes, taux_perte, ls_temps_requetes


def optimal_C_lambda(nbr_requetes, lambd = 1, ls_C = [1, 2, 3, 6]):
    """
    Fonction pour trouver le C optimal pour un lambda donnée
    """
    res = []

    for C in ls_C:
        _, taux_perte, ls_temps_requetes = simulation_serveur(C, lambd, nbr_requetes)
        if ls_temps_requetes:
            temps_moyenne = np.mean(ls_temps_requetes)
            std = np.std(ls_temps_requetes, ddof=1)
            intervalle = 1.96 * (std / np.sqrt(len(ls_temps_requetes)))
        else:
            temps_moyenne = 0
            intervalle = 0
        taux_perte = (taux_perte / nbr_requetes) * 100
        res.append([C, temps_moyenne, (temps_moyenne - intervalle, temps_moyenne + intervalle), taux_perte])

    min = res[0][1]
    min_i = 0
    for i in range(1, len(res)):
        if res[i][1] < min:
            min = res[i][1]
            min_i = i

    potentiel_i = []
    potentiel_i.append(min_i)
    for i in range(len(res)):
        if i != min_i:
            if res[i][3] < 5:
                if not (res[min_i][2][1] < res[i][2][0] or res[i][2][1] < res[min_i][2][0]):
                    potentiel_i.append(i)
            else:
                res[i].append("perte")
    
    if len(potentiel_i) == 1:
        res[min_i].append("valide")
        for i in range(len(res)):
            if i != min_i and len(res[i]) < 5:
                res[i].append("mauvais")
    else:
        for i in range(len(res)):
            if i in potentiel_i:
                res[i].append("potentiel")
            elif len(res[i]) < 5:
                res[i].append("mauvais")
    return res


def graphique_temps_reponse(nbr_requetes, ls_C = [1, 2, 3, 6], lambdas = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]):
    """
    Fonction pour tracer le temps de réponse moyen en fonction de λ
    avec intervalles de confiance à 95%.
    """
    total = len(lambdas)

    for C in ls_C:
        i = 0
        temps_reponses = []  # On réinitialise ici pour chaque courbe C
        intervalles = []     # Liste pour les intervalles de confiance

        # Affichage progression
        print(f"C = {C} : 0.0% terminé", end="\r")

        for lambd in lambdas:
            i += 1
            _, _, ls_temps_requetes = simulation_serveur(C, lambd, nbr_requetes)
            if ls_temps_requetes:
                moyenne = np.mean(ls_temps_requetes)
                std = np.std(ls_temps_requetes, ddof=1)
                intervalle = 1.96 * (std / np.sqrt(len(ls_temps_requetes)))
            else:
                moyenne = 0
                intervalle = 0
            temps_reponses.append(moyenne)
            intervalles.append(intervalle)

            # Affichage progression
            pourcentage = (i / total) * 100
            print(f"C = {C} : {pourcentage:.1f}% terminé", end="\r")

        print()

        # Intervalles de confiance
        plt.errorbar(lambdas, temps_reponses, yerr=intervalles, fmt='o-', capsize=5, label='C = ' + str(C))

    # Légendes graphique
    plt.title("Temps de réponse moyen en fonction de λ avec intervalle 95%")
    plt.xlabel("λ (Taux d'arrivée)")
    plt.ylabel("Temps de réponse moyen")
    plt.legend()
    plt.grid(True)

    plt.show()


def graphique_temps_reponse_precis(nbr_requetes, ls_C = [1, 2, 3, 6], lambd_min = 1, lambd_max = 5, precision = 20):
    """
    Fonction pour tracer le temps de réponse moyen en fonction de λ, 
    sur l’intervalle [lambda_min, lambda_max], avec une précision donnée.
    """
    if lambd_min > lambd_max:
        tmp = lambd_max
        lambd_max = lambd_min
        lambd_min = tmp
    for C in ls_C:
        temps_reponses = []  # On réinitialise ici pour chaque courbe C
        intervalles = []     # Liste pour les intervalles de confiance
        lambdas = []
        total = (lambd_max-lambd_min) * precision

        # Affichage progression
        print(f"C = {C} : 0.0% terminé", end="\r")

        for i in range(1, total + 1):
            lambd = (i / precision) + lambd_min
            lambdas.append(lambd)
            _, _, ls_temps_requetes = simulation_serveur(C, lambd, nbr_requetes)
            if ls_temps_requetes:
                moyenne = np.mean(ls_temps_requetes)
                std = np.std(ls_temps_requetes, ddof=1)
                intervalle = 1.96 * (std / np.sqrt(len(ls_temps_requetes)))
            else:
                moyenne = 0
                intervalle = 0
            temps_reponses.append(moyenne)
            intervalles.append(intervalle)

            # Affichage progression
            pourcentage = (i / total) * 100
            print(f"C = {C} : {pourcentage:.1f}% terminé", end="\r")

        print()

        # Tracé de la courbe
        plt.plot(lambdas, temps_reponses, label='C = ' + str(C))


    # Légendes graphique
    plt.title("Temps de réponse moyen en fonction de λ avec intervalle 95%")
    plt.xlabel("λ (Taux d'arrivée)")
    plt.ylabel("Temps de réponse moyen")
    plt.legend()
    plt.grid(True)

    plt.show()


def graphique_taux_perte(nbr_requetes, ls_C = [1, 2, 3, 6], lambdas = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]):
    """
    Fonction pour tracer le taux de perte en fonction de λ
    avec intervalles de confiance à 95%.
    """
    total = len(lambdas)

    for C in ls_C:
        i = 0
        taux_pertes = []  # On réinitialise ici pour chaque courbe C
        intervalles = []  # Liste pour les intervalles de confiance

        # Affichage progression
        print(f"C = {C} : 0.0% terminé", end="\r")

        for lambd in lambdas:
            i += 1
            _, taux_perte, _ = simulation_serveur(C, lambd, nbr_requetes)
            taux_pertes.append(100 * (taux_perte / nbr_requetes)) # x100 pour convertir en pourcentage
            intervalle = (1.96 * np.sqrt((taux_perte / nbr_requetes) * (1 - taux_perte / nbr_requetes) / nbr_requetes))
            intervalles.append(intervalle * 100)  # x100 pour convertir en pourcentage

            # Affichage progression
            pourcentage = (i / total) * 100
            print(f"C = {C} : {pourcentage:.1f}% terminé", end="\r")

        print()

        # Intervalles de confiance
        plt.errorbar(lambdas, taux_pertes, yerr=intervalles, fmt='o-', capsize=5, label='C = ' + str(C))

    # Légendes graphique
    plt.title("Taux de perte (%) en fonction de λ avec intervalle 95%")
    plt.xlabel("λ (Taux d'arrivée)")
    plt.ylabel("Taux de perte (%)")
    plt.legend()
    plt.grid(True)

    plt.show()


def graphique_taux_perte_precis(nbr_requetes, ls_C = [1, 2, 3, 6], lambd_min = 1, lambd_max = 5, precision = 20):
    """
    Fonction pour tracer le taux de perte en fonction de λ, 
    sur l’intervalle [lambda_min, lambda_max], avec une précision donnée.
    """
    if lambd_min > lambd_max:
        tmp = lambd_max
        lambd_max = lambd_min
        lambd_min = tmp
    for C in ls_C:
        taux_pertes = []
        lambdas = []
        total = (lambd_max-lambd_min) * precision
        seuil_5 = 5
        lambda_au_seuil = None

        # Affichage progression
        print(f"C = {C} : 0.0% terminé", end="\r")

        for i in range(1, total + 1):
            lambd = (i / precision) + lambd_min
            lambdas.append(lambd)
            _, taux_perte, _ = simulation_serveur(C, lambd, nbr_requetes)
            perte_pct = 100 * (taux_perte / nbr_requetes)
            taux_pertes.append(perte_pct)

            if lambda_au_seuil is None and perte_pct >= seuil_5:
                lambda_au_seuil = lambd  # Retenir le premier lambda dépassant 5 %


            # Affichage progression
            pourcentage = (i / total) * 100
            print(f"C = {C} : {pourcentage:.1f}% terminé", end="\r")

        print()

        # Tracé de la courbe
        plt.plot(lambdas, taux_pertes, label='C = ' + str(C))

        # Annotation du point de croisement
        if lambda_au_seuil is not None:
            plt.annotate(f"{lambda_au_seuil:.2f}",
                         xy=(lambda_au_seuil, seuil_5),
                         xytext=(lambda_au_seuil, seuil_5 - 5),
                         ha='center',
                         arrowprops=dict(arrowstyle="->", color='black'),
                         fontsize=9)

    # Ligne horizontale à 5 %
    plt.axhline(y=5, color='red', linestyle='--', label='Seuil 5 %')

    # Légendes graphique
    plt.title("Taux de perte (%) en fonction de λ")
    plt.xlabel("λ (Taux d'arrivée)")
    plt.ylabel("Taux de perte (%)")
    plt.legend()
    plt.grid(True)
    plt.show()


def optimal_C_intervalle_lambdas(nbr_requetes, ls_C, lambd_min = 1, lambd_max = 5, precision = 20):
    """
    Fonction qui cherche et affiche dans un tableau le meilleur C pour des valeurs de λ,
    sur l'intervalle [lambda_min, lambda_max], avec une précision donnée,
    en utilisant la fonction `optimal_C_lambda`.
    """
    if lambd_min > lambd_max:
        tmp = lambd_max
        lambd_max = lambd_min
        lambd_min = tmp

    total = (lambd_max-lambd_min) * precision
    lambda_sym = '\u03BB'
    print("|" + "-" * 116 + "|")
    print(f"|{lambda_sym:<20}| {'Meilleur(s) C':<20}| {'IC 95%':<50}| {'Taux de perte':<20}|")
    print("|" + "-" * 116 + "|")

    for i in range(1, total + 1):
        lambd = (i / precision) + lambd_min
        res = optimal_C_lambda(nbr_requetes, lambd, ls_C)
        IC_str = ""
        perte_str = ""
        C_str = ""
        for C, TRM, IC, perte, eval in res:
            if eval == "valide" or eval =="potentiel":
                tmp_str = ", ".join(f"{elem:.3f}" for elem in IC)
                if IC_str != "":
                    IC_str = IC_str + ", "
                IC_str = IC_str + f"[{tmp_str}]"
                if perte_str != "":
                    perte_str = perte_str + ", "
                perte_str = perte_str + f"{perte:.2f}%"
                if C_str != "":
                    C_str = C_str + ", "
                C_str = C_str + str(C)

        print(f"|{lambd:<20}| {C_str:<20}| {IC_str:<50}| {perte_str:<20}|")
    print("|" + "-" * 116 + "|")


def affiche_tableau(data):
    """
    Fonction qui affiche le tableau des résultats pour déterminer le 
    meilleur C pour un λ donné, en utilisant les résultats de sortie 
    de la fonction `optimal_C_lambda`.
    """
    print("|" + "-" * 86 + "|")
    print(f"|{'C':<5}| {'TRM moyen':<12}| {'IC 95%':<25}| {'Taux de perte':<15}| {'Évaluation':<20} |")
    print("|" + "-" * 86 + "|")
    for C, TRM, IC, perte, eval in data:
        if eval == "mauvais":
            eval_str = "\u274C Rejeté"
        elif eval == "valide":
            eval_str = "\u2705 Optimal"
        elif eval == "perte":
            eval_str = "\u274C Perte > 5%"
        else:
            eval_str = "\U0001F536 Comparable"
        IC_str = ", ".join(f"{elem:.6f}" for elem in IC)
        IC_str = f"[{IC_str}]"
        perte_str = f"{perte:.2f}%"
        print(f"|{C:<5}| {TRM:<12.2f}| {IC_str:<25}| {perte_str:<15}| {eval_str:<20}|")
    print("|" + "-" * 86 + "|")


lambdas = [0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 
           1.6, 1.7, 1.8, 1.9, 2, 2.1, 2.2, 2.3, 2.4, 2.5, 
           2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.3, 3.4, 3.5]

ls_C = [1, 2, 3, 6]

### Question 1
# graphique_temps_reponse(100000, ls_C, lambdas)
## Plus fin mais sans les intervalles
# graphique_temps_reponse_precis(100000, ls_C, 1, 5, 100)

### Question 2
# graphique_taux_perte(100000, ls_C, lambdas)
## Plus fin mais sans les intervalles
# graphique_taux_perte_precis(100000, ls_C, 1, 5, 20)

### Question 3
# affiche_tableau(optimal_C_lambda(100000, 1))

### Question 4
optimal_C_intervalle_lambdas(100000, ls_C, 0, 3, 10)
