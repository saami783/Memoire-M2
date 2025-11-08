def get_prompt_to_generate_pico(research_question: str, file_name: str) -> str:
    return (
        "RÔLE Tu es expert·e en théorie des graphes, optimisation combinatoire et algorithmique. "
        "Ta mission : à partir d’une question de recherche, générer un fichier texte PICO **strict** (P, I, C, O) et ÉCRIRE ce contenu dans un fichier. "
        f"ACTIONS FICHIER (OBLIGATOIRE) Nomme un unique fichier texte commençant par {file_name} et finissant par .txt. "
        "Écris le contenu PICO complet dans ce fichier au répertoire courant en UTF-8 et ÉCRASE s’il existe. "
        "IMPORTANT : la DERNIÈRE LIGNE du fichier doit être exactement le NOM DU FICHIER (ex. PICO_algos.txt). "
        "ENTRÉES - Question de recherche : " + research_question + " - Langue de sortie : français - Public visé : chercheurs en algorithmique/optimisation. "
        "CONTRAINTES (FOCUS PICO) "
        "- **NE PAS** inclure de mots-clés/synonymes, critères d’inclusion/exclusion, requêtes de recherche, stratégie bibliographique, ni annexes d’extraction. "
        "- Rester formel, précis et neutre ; n’inventer aucun résultat expérimental ni théorème. "
        "- Si des éléments manquent, lister des **HYPOTHÈSES** raisonnables puis construire le PICO sur cette base. "
        "- Si la question est trop large, proposer 2–3 **reformulations** plus ciblées et poursuivre avec la meilleure. "
        "- Si la question est **purement théorique**, adapter O vers des **propriétés démontrées** (bornes, complexité, ratio d’approximation). "
        "SORTIE (TEXTE UNIQUEMENT) — Rends exactement les sections suivantes, sans autre texte. "
        "==== MÉTA ==== "
        "TITRE COURT : "
        "QUESTION DE RECHERCHE : "
        "DOMAINE / PROBLÈME : "
        "TYPE DE QUESTION (théorique / expérimental / mixte) : "
        "RÉSUMÉ PICO (2–3 lignes) : "
        "==== PICO ==== "
        "PROBLÈMES / INSTANCES (P) : "
        "ALGORITHME / MÉTHODE (I) : "
        "COMPARATEUR (C) : "
        "MESURES / PROPRIÉTÉS (O) : "
        "==== DÉLIMITATION DE LA PORTÉE ==== "
        "- Reformulations proposées (2–3) : "
        "- Reformulation retenue : "
        "- Inclusions / exclusions **méthodologiques** internes au PICO (périmètre technique uniquement) : "
        "==== PROTOCOLE D’ÉVALUATION / BENCHMARK (SI EXPÉRIMENTAL) ==== "
        "- Données/familles de graphes, budgets, seeds, métriques rapportées, équité des comparaisons. "
        "==== QUALITÉ & REPRODUCTIBILITÉ ==== "
        "- Code/disponibilité, versionnement, contrôle des aléas, transparence des baselines. "
        "==== HYPOTHÈSES & INCERTITUDES ==== "
        "- Hypothèses posées ; points ambigus ; limites attendues. "
        "==== CHECKLIST FINALE ==== "
        "- P/I/C/O cohérents et traçables ; protocole (si applicable) défini ; hypothèses explicites. "
        "==== NOM DE FICHIER ==== "
        "(rappelle le nom du fichier choisi et imprime-le aussi en DERNIÈRE LIGNE DU FICHIER)"
    )


def get_prompt_to_generate_boolean_query(
    pico_filename: str,
    research_question: str,
    output_file_name_boolean_queries: str,
    doc_boolean_queries: str,
) -> str:
    """
    - Lit le PICO et la doc de syntaxe (doc_boolean_queries)
    - Extrait quelques mots-clés EN (généraux), construit UNE requête arXiv
      avec un FILTRE DE DATE >= 2017
    - Écrit le fichier (UTF-8, écrasement) et termine par le nom du fichier
    """

    def ensure_txt(name: str) -> str:
        return name if name.lower().endswith(".txt") else f"{name}.txt"

    out_file = ensure_txt(output_file_name_boolean_queries)
    doc_file = ensure_txt(doc_boolean_queries)

    return (
        "RÔLE Tu es un·e assistant·e de recherche en algorithmique/THÉORIE DES GRAPHES. "
        "Objectif : lire le PICO, lire la doc de syntaxe, puis produire UNE requête arXiv propre, courte et exploitable en Python, "
        "avec un filtre temporel pour ne garder que les articles publiés depuis 2017 inclus. "

        "CONTEXTES D’ENTRÉE "
        f"- QUESTION DE RECHERCHE : {research_question} "
        f"- FICHIER PICO À LIRE : {pico_filename} "
        f"- FICHIER DE RÉFÉRENCE SYNTAXE : {doc_file} (opérateurs, champs, parenthèses, guillemets, échappements). "

        "CONTRAINTES CRITIQUES "
        f"- Tu DOIS d’abord LIRE et RESPECTER {doc_file}. N’invente aucune syntaxe. "
        "- Générer EXACTEMENT UNE requête finale (ligne ARXIV_FINAL). "
        "- La requête tient sur UNE seule ligne, respecte les champs autorisés et inclut OBLIGATOIREMENT "
        "  un filtre de date au format arXiv : submittedDate:[20170101 TO 20991231]. "
        "- Utiliser quelques termes GÉNÉRAUX uniquement (2–4 blocs OR max) : "
        "  ex. problème (« minimum vertex cover » OR « vertex cover ») ET apprentissage (learning / “graph neural network” / “reinforcement learning”). "
        "- Éviter tout terme trop spécifique ou hors sujet (ex. policy gradient, actor-critic, model-view-controller, noms précis d’architectures), "
        "  sauf si absolument nécessaire (à éviter ici). "
        "- Ne rien imprimer en console : tout va dans le fichier. "

        "EXTRACTION (depuis le PICO) "
        "- Dégager des mots/expressions EN très concis : problème (\"minimum vertex cover\" / \"vertex cover\"), "
        "  apprentissage (learning, \"graph neural network\", \"reinforcement learning\"). "

        f"FORMAT DE SORTIE EXACT À ÉCRIRE DANS {out_file} (UTF-8, ÉCRASE si existe) "
        "Écris EXACTEMENT ces lignes dans cet ordre : "
        f"==== SOURCE ==== PICO_FILE: {pico_filename} DOC_SYNTAX: {doc_file} "
        "- EN: <liste très courte (2–6 termes) séparés par ';'> "
        "ARXIV_FINAL: <UNE SEULE LIGNE avec la requête conforme + submittedDate:[20170101 TO 20991231]> "
        "ARXIV_QUERY_PY: query = \"<LA MÊME REQUÊTE QUE ARXIV_FINAL, avec tous les guillemets doubles internes échappés en \\\" >\" "
        "[optionnel] NOTE: <si une règle de la doc est ambiguë, indiquer le choix> "
        f"{out_file} "

        "RÈGLES POUR ARXIV_QUERY_PY "
        "- Utilise des guillemets doubles autour de la chaîne Python : query = \"...\" "
        "- À l’intérieur de cette chaîne Python, ÉCHAPPE chaque guillemet double par \\\": ex. ti:\\\"graph theory\\\" "
        "- Pas de triple quotes, pas de concaténation, pas de backticks. "
        "- Chaîne STRICTEMENT sur une seule ligne. "

        "PROCÉDURE FICHIER (OBLIGATOIRE) "
        f"- Ouvre/Lis {doc_file} puis {pico_filename}. "
        "- Construit UNE requête courte et lisible, avec : "
        "  (ti:\"minimum vertex cover\" OR abs:\"minimum vertex cover\" OR ti:\"vertex cover\" OR abs:\"vertex cover\") "
        "  AND (ti:learning OR abs:learning OR ti:\"graph neural network\" OR abs:\"graph neural network\" OR ti:\"reinforcement learning\" OR abs:\"reinforcement learning\") "
        "  AND submittedDate:[20170101 TO 20991231] "
        f"- Écris le fichier {out_file} (UTF-8). "
        f"- Vérifie que la DERNIÈRE LIGNE du fichier est exactement : {out_file} "
    )

def get_prompt_find_conjecture(folder: str, file: str) -> str:
    return (
        f"dans le dossier {folder} je souhaite que tu ouvres le fichier {file} et que tu me détectes "
            "si oui ou non il existe une ou plusieurs conjecture(s) formulées par les auteurs de cet article. On ne tiendra"
            " pas compte des conjectures citées d'autres articles. Raisonne uniquement par ton intelligence, je ne veux aucun script."
            f" Réfléchis et donne moi ta réponse. Je veux que tu trouves des conjectures pour le fichier {file}. "
            "Aussi pour chaque conjecture, je souhaite que tu définisses les paramètres utilisés. Pour les formules mathématiques "
            "ainsi que les paramètres, utilise la syntaxe latex."
            "Une fois ta tâche terminée, je veux que tu fasses une repasses afin de faire quelques micro-retouches de notation/terminologie "
            "pour coller exactement au papier si nécessaire. Mets un point de vigilance sur les indices par exemple."
            "Tu dois faire du mot-à-mot pour les conjectures, ce qui signifie que tu ne dois "
            "pas traduire le texte ni inventer des choses. Reste fidèle à ce que le(s) auteur(s) a/ont écrit."
            f"Écris toutes les conjectures que tu as trouvé dans un fichier json dans le répertoire {folder}/json."
            "Le fichier json que tu vas créer doit suivre exactement le schéma suivant :"
            "{\n"
            "  \"contains_conjecture\": true,\n"
            "  \"conjectures\": [\n"
            "    {\n"
            "      \"label\": \"title/index of the conjecture\",\n"
            "      \"conjecture\": \"the entire conjecture\",\n"
            "      \"parameters\": [\n"
            "        {\n"
            "          \"name\": \"the name of the parameter\",\n"
            "          \"definition\": \"the definition of the parameter\"\n"
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}"
            "N'échappe pas les $ dans les formules mathématiques latex."
            f"Le nom du fichier json doit exactement être {file}.json (tu supprimeras le .txt pour que ça donne .pdf.json)."
            "Lorsque tu auras terminé, je veux que tu écrives dans la dernière ligne du fichier JSON cela : `FIN`."
    )

# certains paramètres sont inventés