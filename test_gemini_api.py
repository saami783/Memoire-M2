from google import genai
from dotenv import load_dotenv
import os
from conjectures-refutation.helpers.invariants import get_invariants
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key,)

config = genai.types.GenerateContentConfig(
    temperature=0.0,
)

conjecture = "\\mathrm{dc}_{r}^{\\delta}(G)', 'definition': 'The smallest integer $t$ such that in every $r$-coloring of the edges of $G$, there exists a monochromatic $t$-cover consisting of subgraphs of diameter at most $\\delta$."

invariants = get_invariants()

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=
            f"""
                Voici une conjecture en théorie des graphes : {conjecture}.

                Générez une fonction de score en Python qui évalue si un graphe est un contre-exemple à cette conjecture.
                La fonction doit avoir la signature suivante : conj_1(G, min_size, max_size). Et ajoute cette instruction dans les imports : 
                La fonction doit retourner None si le graphe n'est pas éligible (taille hors limites ou non conforme à la conjecture).
                Sinon, elle doit retourner un score numérique qui est négatif si le graphe est un contre-exemple à la conjecture.

                Exemples de fonctions de score :
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
                    
                Voici la liste des invariants calculés : {invariants}

                Assurez-vous que la fonction est correctement indentée.
                Ne fournissez que le code de la fonction, sans commentaires ni texte supplémentaire. 
                Vraiment uniquement la fonction est rien d'autre.
                """,
    config=config
)

print(response.text)