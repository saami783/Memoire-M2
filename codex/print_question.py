"""Simple script that prints the provided research question."""
from __future__ import annotations
import os
import subprocess

# --dangerously-bypass-approvals-and-sandbox
import argparse
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print the research question provided as an argument.",
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Research question to display.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.question:
        print("No research question provided.", file=sys.stderr)
        return 1
    print(args.question)
    return args.question


if __name__ == "__main__":
    research_question = main()

    prompt = (
            "RÔLE Tu es expert·e en théorie des graphes, optimisation combinatoire et algorithmique. Ta mission : générer un fichier texte PICO adapté aux recherches en algorithmique à partir d’une question et ÉCRIRE ce contenu dans un fichier. "
            "ACTIONS FICHIER (OBLIGATOIRE) Calcule un slug lisible à partir de la question (règles : tout en minuscules ; remplace toute séquence non [a-z0-9] par un tiret ; supprime les tirets en tête/queue ; compresse les tirets consécutifs ; tronque à 80 caractères ; si vide utiliser pico). Nomme exactement le fichier PICO_algos_{slug}.txt. Écris le contenu PICO complet dans ce fichier au répertoire courant en UTF-8 et ÉCRASE s’il existe. Si l’écriture RÉUSSIT, n’imprime en console que la ligne: FILE_WRITTEN: PICO_algos_{slug}.txt. Si l’écriture ÉCHOUE ou n’est pas autorisée, imprime la ligne: WRITE_FAILED puis imprime le contenu complet. "
            "ENTRÉES - Question de recherche : " + research_question + " - Langue de sortie : français - Public visé : chercheurs en algorithmique/optimisation. "
                                                                       "RÈGLES - Reste formel, précis et neutre ; n’invente aucun résultat expérimental. - Si des éléments manquent (classe de graphes, objectifs, métriques, ressources), liste d’abord des HYPOTHÈSES raisonnables, puis construis le PICO en t’appuyant dessus. - Si la question est trop large, propose 2–3 reformulations plus ciblées et poursuis avec la meilleure. - Si la question est purement théorique (sans expérimentation), adapte O vers des PROPRIÉTÉS DÉMONTRÉES (bornes, complexité, ratio) et indique clairement le cadre. "
                                                                       "SORTIE (TEXTE UNIQUEMENT) Rends uniquement les sections ci-dessous, sans commentaires hors sections. "
                                                                       "==== MÉTA ==== TITRE COURT : QUESTION DE RECHERCHE : DOMAINE / PROBLÈME : (ex. TSP, Max-Cut, Couverture de sommets, Flots, Coloration, etc.) TYPE DE QUESTION : (conception d’algorithme / approximation / FPT / EPTAS / complexité / bornes inférieures / online/streaming / expérimentation/benchmark / heuristique / métaheuristique / autre) RÉSUMÉ PICO (2–3 lignes) : "
                                                                       "==== PICO ==== PROBLÈMES / INSTANCES (P) : - Définition formelle : (classe de graphes : orientés/non orientés, pondérés/non pondérés, planaires, bipartis, k-partis, arbres, DAG, denses/parcimonieux…) - Paramètres d’échelle : (n=|V|, m=|E|, densité, distribution des poids) - Génération/benchmarks : (Erdős–Rényi G(n,p), Barabási–Albert, DIMACS, SNAP, TSPLIB, NETLIB) - Contraintes/propriétés : (connectivité, degrés, métrique, triangle inequality, etc.) "
                                                                       "ALGORITHME / MÉTHODE (I) : - Description : (exact ILP/CP/branch-and-bound/DP, approx, FPT, heuristique, métaheuristique, randomisé, online, streaming) - Détails clés : (critères d’arrêt, paramètres, initialisation, randomisation/graines) - Ressources : (modèle de calcul, temps/mémoire, CPU/GPU, parallélisme) "
                                                                       "COMPARATEUR (C) : - Baselines : (SOTA, heuristiques classiques, exacts petites tailles, ablations) - Cadre : (mêmes instances, budgets, temps limite, tuning équitable) "
                                                                       "MESURES / PROPRIÉTÉS (O) : - Qualité : (valeur objective, écart à l’optimal %, ratio d’approximation prouvé) - Efficacité : (complexité O(·), temps mur/CPU, mémoire, scalabilité par n et m) - Robustesse : (variance sur graines, sensibilité hyperparamètres) - Autres : (taux de réussite, itérations, preuves de correction/terminaison) - Horizon : (tailles cibles, budgets temps/mémoire). "
                                                                       "==== DÉLIMITATION DE LA PORTÉE ==== HYPOTHÈSES/CONTRAINTES SUR LES INSTANCES : BUDGETS/ENVIRONNEMENT : SOUS-PROBLÈMES/PARAMÈTRES : NON-OBJECTIFS : TYPE(S) D’ÉTUDE CIBLÉ(S) : (preuve, conception+analyse, benchmark, simulation) "
                                                                       "==== PROTOCOLE D’ÉVALUATION / BENCHMARK (SI EXPÉRIMENTAL) ==== Jeux d’instances : Procédure : Équité de comparaison : Analyse statistique : "
                                                                       "==== STRATÉGIE DE RECHERCHE BIBLIO (OPTIONNEL) ==== Mots-clés FR/EN : Bases : (arXiv cs.DS/cs.LG, DBLP, ACM DL, IEEE Xplore, HAL) Chaînes booléennes : Restrictions : "
                                                                       "==== QUALITÉ & REPRODUCTIBILITÉ ==== Menaces à la validité : Mesures d’atténuation : "
                                                                       "==== PLAN D’EXTRACTION (BREF) ==== Pour chaque étude : (problème, classe de graphes, algo, complexité, ratio/écart, datasets, tailles n/m, temps/mémoire, matériel, liens code/données) "
                                                                       "==== HYPOTHÈSES & INCERTITUDES ==== (liste claire des hypothèses faites quand l’info manque) "
                                                                       "==== CHECKLIST FINALE ==== [ ] P défini | [ ] I clair | [ ] C pertinent | [ ] O mesurables/prouvables | [ ] Métriques/budgets comparables | [ ] Reproductibilité (graines, code) "
                                                                       "==== NOM DE FICHIER ==== PICO_algos_{slug}.txt"
    )

    os.system('codex --sandbox=danger-full-access "' + prompt + '"')
