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

    return nbr_requetes, taux_perte, ls_temps_requetes

def graphique_temps_reponse(ls_C, nbr_requetes):
    """
    Fonction pour tracer le temps de réponse moyen en fonction de λ
    avec intervalles de confiance à 95%.
    """
    lambdas = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

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

def graphique_taux_perte(ls_C, nbr_requetes):
    """
    Fonction pour tracer le taux de perte en fonction de λ
    avec intervalles de confiance à 95%.
    """
    lambdas = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

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

ls_C = [1, 2, 3, 6]
graphique_temps_reponse(ls_C, 100000)
graphique_taux_perte(ls_C, 100000)
