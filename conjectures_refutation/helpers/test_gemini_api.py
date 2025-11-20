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

conjecture = "Conjecture 2.2. For all integers $r \geq 2$ and all $K \in \mathcal{K}_{r}, \operatorname{tc}_{r-1}(K) \leq r-1$. In particular, this implies that for every $r$-coloring of a complete graph $K$ and every color $i \in[r]$, either there is a monochromatic $(r-1)$-cover consisting entirely of subgraphs of color $i$, or entirely of subgraphs which don't have color $i$."
invariants = get_invariants()
index = 1

# des fois le modèle donne une réponse sous ```python ... ```
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=f"""
    Tu es un système expert en théorie des graphes et en algorithmique.

    TA MISSION :
    À partir d'une conjecture mathématique que je te donne, tu dois générer une fonction 
    Python `conj_{index}(G, min_size, max_size)` capable de détecter un contre-exemple.

    LA CONJECTURE UTILISATEUR :
    "{conjecture}"

    RÈGLES STRICTES DE LA FONCTION :
    1. Signature : `def conj_1(G, min_size, max_size):`
    2. Imports : Tu peux utiliser à l'intérieur de la fonction les imports suivants `networkx as nx`, `numpy as np`, `math`, `itertools`, `random`, 
    `collections` et `from helpers.invariants import *`.
    3. Le Score (CRUCIAL) :
       - Retourne `None` si le graphe ne respecte pas les pré-conditions (taille, type de graphe, etc.).
       - Retourne une valeur NÉGATIVE si et seulement si le graphe G est un CONTRE-EXEMPLE.
       - Plus le score est négatif, plus le contre-exemple est fort (pour guider l'optimiseur).
       - Si la conjecture est respectée, retourne une valeur positive (ex: 1.0 ou score > 0).

    4. GESTION DE L'OBJET G (TRES IMPORTANT) :
       - CAS A : Conjecture sur des graphes généraux (ex: "Si G est planaire...", "Pour tout arbre T...").
         -> Utilise l'objet `G` tel quel (ses arêtes, sa structure).
       - CAS B : Conjecture sur des structures fixes définies par la taille (ex: "Pour tout K_n...", 
            "Pour tout cycle C_n...", "Pour tout hypergraphe K_n^r...").
         -> IGNORE les arêtes de `G`. Utilise seulement `n = G.number_of_nodes()` pour reconstruire mathématiquement 
            la structure demandée (ex: génère toutes les paires pour K_n, ou toutes les combinaisons pour un hypergraphe).

    CATÉGORIES DE CONJECTURES (Few-Shot Learning) :

    --- TYPE A : Inégalités d'Invariants (A <= B) ---
    Stratégie : Retourner `-(B - A)`.
    Exemple :
    def conj_type_a(G, min_size, max_size):
        order = G.number_of_nodes()
        if order < min_size or order > max_size: return None
        if not binary_properties_functions["connected"](G): return None
        # Conjecture: lambda_1 <= sqrt(n-1)
        val_left = invariants_functions["largest_eigenvalue"](G)
        val_right = math.sqrt(order - 1)
        return -(val_right - val_left)

    --- TYPE B : Implication Structurelle (Si X alors Y) ---
    Stratégie : Si non(X) -> None. Si X et non(Y) -> -1.0 (Contre-exemple). Sinon -> 1.0.
    Exemple ("Si G est planaire, il est 4-coloriable") :
    def conj_type_b(G, min_size, max_size):
        import networkx as nx
        if G.number_of_nodes() < min_size: return None
        # 1. Pré-condition
        is_planar, _ = nx.check_planarity(G)
        if not is_planar: return None
        # 2. Test (Heuristique pour chercher contre-exemple)
        d = nx.coloring.greedy_color(G, strategy="largest_first")
        if (max(d.values()) + 1) > 4: return -1.0 # Contre-exemple !
        return 1.0

    --- TYPE C : Existence Combinatoire / Hypergraphes ---
    Stratégie : Construire la structure depuis 'n', tester (aléatoirement ou exhaustivement).
    Exemple ("Dans tout 2-coloriage de K_n^3, il existe...") :
    def conj_type_c(G, min_size, max_size):
        import itertools, random
        n = G.number_of_nodes() # On récupère juste la taille
        if n < min_size: return None
        # On ignore les arêtes de G, on construit un hypergraphe complet K_n^3
        hyperedges = list(itertools.combinations(range(n), 3))

        # Test sur 50 colorations aléatoires (Approche probabiliste pour rapidité)
        for _ in range(50):
            colors = [random.randint(0, 1) for _ in hyperedges]
            # ... logique de vérification ...
            found_property = False # Supposons qu'on vérifie la propriété ici

            if not found_property: 
                return -1.0 # Contre-exemple trouvé (une coloration qui n'a pas la propriété)
        return 1.0

    INVARIANTS DISPONIBLES :
    {invariants}

    GÉNÈRE MAINTENANT LE CODE PYTHON POUR LA CONJECTURE CI-DESSUS.
    N'écris QUE le code de la fonction, sans balises markdown, sans explications.
    """,
    config=config
)

print(response.text)