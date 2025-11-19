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

