from __future__ import annotations
import argparse, sys
from create_pico_file import create_pico_file

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Génère un PICO via Codex puis continue (Unix/macOS).")
    p.add_argument("question", nargs="?", help="Question de recherche.")
    return p.parse_args()

def get_prompt() -> str:
    return (
        "RÔLE Tu es expert·e en théorie des graphes, optimisation combinatoire et algorithmique. "
        "Ta mission : générer un fichier texte PICO adapté aux recherches en algorithmique à partir d’une question et ÉCRIRE ce contenu dans un fichier. "
        "ACTIONS FICHIER (OBLIGATOIRE) Nomme un unique fichier texte commençant par PICO et finissant par .txt (ex: PICO_algos.txt ou PICO_algos_<slug>.txt). "
        "Écris le contenu PICO complet dans ce fichier au répertoire courant en UTF-8 et ÉCRASE s’il existe. "
        "IMPORTANT : la DERNIÈRE LIGNE du fichier doit être exactement le NOM DU FICHIER (par ex. PICO_algos.txt). "
        "ENTRÉES - Question de recherche : " + research_question + " - Langue de sortie : français - Public visé : chercheurs en algorithmique/optimisation. "
        "RÈGLES - Reste formel, précis et neutre ; n’invente aucun résultat expérimental. - Si des éléments manquent, liste des HYPOTHÈSES raisonnables puis construis le PICO en t’appuyant dessus. "
        "- Si la question est trop large, propose 2–3 reformulations plus ciblées et poursuis avec la meilleure. - Si la question est purement théorique, adapte O vers des PROPRIÉTÉS DÉMONTRÉES (bornes, complexité, ratio). "
        "SORTIE (TEXTE UNIQUEMENT) Rends uniquement les sections suivantes, sans commentaire hors sections. "
        "==== MÉTA ==== TITRE COURT : QUESTION DE RECHERCHE : DOMAINE / PROBLÈME : TYPE DE QUESTION : RÉSUMÉ PICO (2–3 lignes) : "
        "==== PICO ==== PROBLÈMES / INSTANCES (P) : ALGORITHME / MÉTHODE (I) : COMPARATEUR (C) : MESURES / PROPRIÉTÉS (O) : "
        "==== DÉLIMITATION DE LA PORTÉE ==== "
        "==== PROTOCOLE D’ÉVALUATION / BENCHMARK (SI EXPÉRIMENTAL) ==== "
        "==== STRATÉGIE DE RECHERCHE BIBLIO (OPTIONNEL) ==== "
        "==== QUALITÉ & REPRODUCTIBILITÉ ==== "
        "==== PLAN D’EXTRACTION (BREF) ==== "
        "==== HYPOTHÈSES & INCERTITUDES ==== "
        "==== CHECKLIST FINALE ==== "
        "==== NOM DE FICHIER ==== (rappelle le nom du fichier choisi et imprime-le aussi en DERNIÈRE LIGNE DU FICHIER)"
    )

def main() -> str | None:
    args = parse_args()
    if not args.question:
        print("No research question provided.", file=sys.stderr)
        return None
    print(args.question)
    return args.question

if __name__ == "__main__":
    research_question = main()

    prompt = get_prompt()

    create_pico_file(prompt)

    print("Coucou j'ai repris la main et je peux faire d'autres travaux")
