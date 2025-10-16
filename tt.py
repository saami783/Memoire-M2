import os
import json
import time
import requests

def telecharger_pdfs_hal(query_url: str, dossier: str = "pdf_hal"):
    os.makedirs(dossier, exist_ok=True)
    r = requests.get(query_url, timeout=10)
    r.raise_for_status()
    data = r.json()

    telecharges = 0
    for doc in data.get("response", {}).get("docs", []):
        # 1) on privilégie le fichier principal s'il est un PDF
        urls = []
        main = doc.get("fileMain_s")
        if isinstance(main, str):
            urls.append(main)

        # 2) sinon on balaie tous les fichiers associés
        files = doc.get("files_s") or []
        if isinstance(files, list):
            urls.extend(files)

        # élimine les doublons
        seen = set()
        urls = [u for u in urls if not (u in seen or seen.add(u))]

        # essaie de trouver une URL de PDF
        pdf_url = next((u for u in urls if u.lower().endswith(".pdf")), None)
        if not pdf_url:
            # parfois l’URL n’a pas d’extension → on tentera quand même
            pdf_url = next(iter(urls), None)

        if not pdf_url:
            continue

        # nom de fichier propre: halId + .pdf si possible
        base_name = doc.get("halId_s") or str(doc.get("docid", "hal_doc"))
        if not base_name.lower().endswith(".pdf"):
            base_name += ".pdf"
        chemin = os.path.join(dossier, base_name)

        try:
            with requests.get(pdf_url, stream=True, timeout=30) as resp:
                resp.raise_for_status()
                # on vérifie le type MIME quand il est fourni
                ct = resp.headers.get("Content-Type", "")
                if "pdf" not in ct.lower() and not chemin.lower().endswith(".pdf"):
                    # force l’extension si pas de Content-Type explicite
                    chemin += ".pdf"

                with open(chemin, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            telecharges += 1
            # petite pause pour rester poli avec l'API/domaine de fichiers
            time.sleep(0.2)
        except Exception as e:
            print(f"[!] Échec {pdf_url} — {e}")

    print(f"✔ Téléchargements terminés : {telecharges} fichier(s).")


# Exemple de requête :
# - limite au portail CRLAO (comme ton exemple)
# - cherche "python" dans le titre
# - ne retourne que les dépôts avec fichier
# - demande explicitement les champs utiles
ma_requete = (
    "https://api.archives-ouvertes.fr/search/CRLAO/"
    "?q=title_t:python"
    "&fq=submitType_s:file"
    "&rows=100"
    "&sort=submittedDate_tdate desc"
    "&fl=docid,halId_s,title_s,uri_s,fileMain_s,files_s"
    "&wt=json"
)

telecharger_pdfs_hal(ma_requete)
