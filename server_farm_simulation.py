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
                # Planifier FIN_TRAITEMENT_ROUTEUR si nécessaire
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
                # Planifier FIN_TRAITEMENT_ROUTEUR pour la prochaine requête
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

def graphique_temps_reponse(nbr_requetes, ls_C = [1, 2, 3, 6], lambdas = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]):
    """
    Fonction pour tracer le temps de réponse moyen en fonction de λ
    avec intervalles de confiance à 95%.
    """
    for C in ls_C:
        temps_reponses = []  # On réinitialise ici pour CHAQUE courbe C
        intervalles = []     # Liste pour les intervalles de confiance

        for lambd in lambdas:
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

        # Tracé avec barres d'erreur
        plt.errorbar(lambdas, temps_reponses, yerr=intervalles, fmt='o-', capsize=5, label='C = ' + str(C))

    # Décorations
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

    for C in ls_C:
        taux_pertes = []  # On réinitialise ici pour CHAQUE courbe C
        intervalles = []  # Liste pour les intervalles de confiance

        for lambd in lambdas:
            _, taux_perte, _ = simulation_serveur(C, lambd, nbr_requetes)
            taux_pertes.append(100 * (taux_perte / nbr_requetes)) # Convertir en pourcentage
            intervalle = (1.96 * np.sqrt((taux_perte / nbr_requetes) * (1 - taux_perte / nbr_requetes) / nbr_requetes))
            intervalles.append(intervalle * 100)  # Convertir en pourcentage

        # Tracé avec barres d'erreur
        plt.errorbar(lambdas, taux_pertes, yerr=intervalles, fmt='o-', capsize=5, label='C = ' + str(C))

    # Décorations
    plt.title("Taux de perte (%) en fonction de λ avec intervalle 95%")
    plt.xlabel("λ (Taux d'arrivée)")
    plt.ylabel("Taux de perte (%)")
    plt.legend()
    plt.grid(True)

    plt.show()

def graphique_taux_perte_precis(nbr_requetes, lambd_max = 5, ls_C = [1, 2, 3, 6]):
    for C in ls_C:
        taux_pertes = []
        lambdas = []
        total = lambd_max * 100
        seuil_5 = 5
        lambda_au_seuil = None

        for i in range(1, total + 1):
            lambd = i / 100
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

    # Décorations
    plt.title("Taux de perte (%) en fonction de λ")
    plt.xlabel("λ (Taux d'arrivée)")
    plt.ylabel("Taux de perte (%)")
    plt.legend()
    plt.grid(True)
    plt.show()

def taux_perte_precis(nbr_requetes, nbr_test, ls_C = [1, 2, 3, 6], lambdas = [0.2, 0.4, 0.6, 0.8]):
    taille = len(ls_C)
    if taille != len(lambdas):
        raise ValueError("Les deux listes n'ont pas la même taille.")
    print(f"Taille de la simulation : {nbr_requetes}.")
    print(f"Moyenne sur {nbr_test} simulation.\n")
    for i in range(taille):
        pertes = 0
        C = ls_C[i]
        lambd = lambdas[i]
        print(f"C = {C}, lambda = {lambd}:")
        for j in range(nbr_test):

            _, taux_perte, _ = simulation_serveur(C, lambd, nbr_requetes)
            taux_perte_pct = 100 * (taux_perte / nbr_requetes)
            intervalle = 1.96 * np.sqrt((taux_perte / nbr_requetes) * (1 - taux_perte / nbr_requetes) / nbr_requetes) * 100
            pertes += taux_perte_pct
            if j < 10:
                print(f"    • {taux_perte_pct}%")
            elif j == 10:
                print("    • …")
        print(f"Moyenne de {pertes/nbr_test}%.\n")

def trouver_lambda(nbr_requetes, ls_C = [1, 2, 3, 6]):
    lambd = 1.25
    lambdas = []
    pourcent_perte = 100
    for C in ls_C:
        while True:
            lambd = lambd * 0.8
            _, taux_perte, _ = simulation_serveur(C, lambd, nbr_requetes)
            pourcent_perte = 100 * (taux_perte / nbr_requetes)
            if pourcent_perte < 5:
                p = 0
                for _ in range(100):
                    _, taux_perte, _ = simulation_serveur(C, lambd, nbr_requetes)
                    p += taux_perte
                if p/100 < 5:
                    break
        lambdas.append(lambd)
        lambd = 1.25
        pourcent_perte = 100
    return lambdas

lambdas = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2]
# lambdas = [0.64, 1.25]

# sur moyenne de 10 simulations avec lambda baisser à 0.8 pour précision approxiamtif
##lambdas = [0.40960000000000013, 1.2259964326927154e-06, 2.394524282602959e-06, 4.017345110647491e-07]
# sur moyenne de 100 simulations avec lambda baisser à 0.8
# lambdas = [0.32768000000000014, 2.5711008708143947e-07, 3.213876088517993e-07, 6.277101735386704e-07]

ls_C = [1, 2, 3, 6]

# R = lambdas
#R = trouver_lambda(100000)
# print(R)

# graphique_temps_reponse(100000, ls_C, lambdas)
# graphique_taux_perte(100000, ls_C, lambdas)
graphique_taux_perte_precis(100000, 3)
# taux_perte_precis(100000, 10, ls_C, R)
