from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv
import os
from openpyxl import load_workbook
from google import genai
from .invariants import get_invariants

# todo : J'interroge un LLM pour qu'il me donne une fonction de score pour chaque conjecture de mon fichier xls, et je l'exécute dynamiquement
# en 1 : on ouvre le fichier excel, et pour chaque conjecture :
    # en 1 : Le LLM (température fixé pour la reproductibilité) génère une fonction de score sous forme de code Python pour une conjecture donnée.
    # en 2 : Le programme exécute dynamiquement ce code pour obtenir une fonction de score utilisable.
    # en 3 : Cette fonction de score est ensuite utilisée par le programme de Thibualt pour évaluer les graphes générés et mutés.
    # note : on doit logger plusieurs choses :
    # la fonction de score généré par le LLM, le temps mis pour trouvé le contre-exemple,

# ça se passera dans refutation_heuristics/local_search.py, dans la fonction _evaluate_graph.

"""
on va découper le code pour qu'il soit plus lisible.
Donc, comprend bien qu'il ne faut pas toucher au fonctionnement général du programme existant.
Lui ce qu'il fait c'est que s'il y a des ID dans le fichier identifiers.txt alors
il va chercher les conjectures du benchmark.csv, si ils existent alors il exécute une fonction de score générique,
sinon si l'id n'est pas dans le benchmark.csv mais que ça correspond à un ID d'une fonction de conjecture.
par exemple "a" alors il exécutera la fonction conj_a. Dans tous les cas, il exécute une fonction de score de la conjecture,
donc c'est ici qu'il faut que nous branchions notre logique, où, si dans identifiers.txt il y a marqué 'export' par exemple,
alors c'est ma logique à moi qui sera prise en compte en exécutant la fonction de score dynamique.
"""

"""
# Supposons que le LLM génère le code suivant pour une conjecture donnée
function_code =
def conj_x(G, min_size, max_size):
    la logique 
    return le calcul de la fonction de score.

# Exécutee dynamiquement le code pour obtenir la fonction
exec(function_code, globals())

# Maintenant, la fonction conj_x est disponible dans le namespace global
score = conj_x(graph, min_size, max_size)

"""

def load_conjectures_from_excel(excel_path: str) -> List[Dict[str, Any]]:
    p = Path(excel_path)
    if not p.exists():
        raise SystemExit("No excel file found.")

    wb = load_workbook(excel_path, data_only=True)
    ws = wb["Conjectures"]

    header_row = 1
    col_conjecture_index = None

    for cell in ws[header_row]:
        if cell.value == "Conjecture":
            col_conjecture_index = cell.column

    if col_conjecture_index is None:
        raise ValueError("No 'Conjecture' column found.")

    conjectures = []

    for index, row in enumerate(range(header_row+1, ws.max_row+1), start=1):
        cell = ws.cell(row=row, column=col_conjecture_index)
        conjecture_text = cell.value

        function_code = get_gemini_response(conjecture_text, index)
        exec(function_code, globals())

        function_name = f"conj_{index}"
        conjecture = {
            "ID": f"export_{index}",
            "conjecture": conjecture_text,
            "subclass": "",
            "score_function": globals()[function_name]
        }
        print(conjecture)
        conjectures.append(conjecture)
    return conjectures

def get_gemini_response(conjecture: str, index: int):
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    invariants = get_invariants()

    client = genai.Client(api_key=api_key, )

    config = genai.types.GenerateContentConfig(
        temperature=0.0,
    )

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
        `collections` et `from .invariants import *`.
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

    function = extract_code(response.text)
    print(function)
    return function


def extract_code(content: str) -> str:
    """
    Enlève les ```python / ``` autour du code si présents
    et renvoie uniquement le code exécutable.
    """
    lines = content.strip().splitlines()

    if not lines:
        return content.strip()

    first = lines[0].strip().lower()
    if first.startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()