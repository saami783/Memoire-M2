from google import genai
from dotenv import load_dotenv
import os
from invariants import *


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


client = genai.Client(api_key=api_key,)

config = genai.types.GenerateContentConfig(
    temperature=0.0,
)

conjecture = "\\operatorname{tc}_{r}(H)', 'definition': 'The minimum integer $t$ such that in every $r$-coloring of the edges of $H$, there exists a monochromatic $t$-cover of $H$"
invariants = get_invariants()

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=
            f"""
                Voici une conjecture en théorie des graphes : {conjecture}.

                Génère une fonction de score en Python qui évalue si un graphe est un contre-exemple à cette conjecture.
                La fonction doit avoir la signature suivante : conj_1(G, min_size, max_size).
                Ne fait aucune supposition sur les conjectures, écris la fonction de score conformément à la conjecture que je t'ai donné.

                La fonction doit retourner None si le graphe n'est pas éligible (taille hors limites ou non conforme à la conjecture).
                Sinon, elle doit retourner un score numérique qui est négatif si le graphe est un contre-exemple à la conjecture.
                
                Si tu as besoin de calculer des invariants, ajoute exactement cette instruction dans les imports de la fonction, sans rien changer
                "from helpers.invariants import *". Elle te permet d'accéder à une liste de fonctions d'invariants qui sont les suivants :
                {invariants}
                
                Voici des exemples de fonctions de score pour différente conjecture :
                def conj_a(G, min_size, max_size):
                    order = G.number_of_nodes()
                    if order < min_size or order > max_size:
                        return None
                    if not binary_properties_functions["connected"](G):
                        return None
                    lambda_max = invariants_functions["largest_eigenvalue"](G)
                    matching_number = invariants_functions["matching_number"](G)
                    return - (math.sqrt(order - 1) + 1 - lambda_max - matching_number)

                def conj_b(G, min_size, max_size):
                    order = G.number_of_nodes()
                    if order < min_size or order > max_size:
                        return None
                    if not binary_properties_functions["tree"](G):
                        return None
                    diameter = invariants_functions["diameter"](G)
                    k = math.floor(2 * diameter / 3)
                    proximity = invariants_functions["proximity"](G)
                    kth_largest_distance_eigenvalue = invariants_functions["kth_largest_distance_eigenvalue"](G, k)
                    return -(-proximity - kth_largest_distance_eigenvalue)

                def conj_c(G, min_size, max_size):
                    order = G.number_of_nodes()
                    if order < min_size or order > max_size:
                        return None
                    if not binary_properties_functions["tree"](G):
                        return None
                    pA, pD = invariants_functions["pA"](G), invariants_functions["pD"](G)
                    m = invariants_functions["m"](G)
                    return -(abs(pA / m  - (1 - pD / order)) - 0.28)

                def conj_d(G, min_size, max_size):
                    order = G.number_of_nodes()
                    if order < min_size or order > max_size:
                        return None
                    if not binary_properties_functions["connected"](G):
                        return None
                    A = nx.adjacency_matrix(G).todense()
                    eigenvalues = np.linalg.eigvals(A)
                    second_largest_eigenvalues = np.sort(eigenvalues)[-2]
                    harmonic_index = invariants_functions["harmonic_index"](G)
                    return -(second_largest_eigenvalues - harmonic_index) 

                Assure-toi que la fonction est correctement indentée.
                Ne fournis que le code de la fonction, sans commentaires ni texte supplémentaire.
                """,
    config=config
)

print(response.text)