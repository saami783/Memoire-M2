from __future__ import annotations
import time
from pathlib import Path
from subprocess import Popen
from typing import Optional

POLL_INTERVAL = 0.2  # secondes

def last_nonempty_line(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in reversed(f.read().splitlines()):
                s = line.strip()
                if s:
                    return s
    except FileNotFoundError:
        pass
    return ""

def newest(path_list: list[Path]) -> Optional[Path]:
    return max(path_list, key=lambda p: p.stat().st_mtime, default=None)

def strip_trailing_term_file(path: Path, term: str = "FIN") -> None:
    """
    Si la dernière ligne non vide vaut `term`, on la supprime et on réécrit le fichier
    proprement (en conservant UTF-8 et en terminant par un '\n').
    """
    if not path.exists():
        return
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()  # sans conserver les fins de ligne

    # Retirer les lignes vides en fin de fichier
    while lines and not lines[-1].strip():
        lines.pop()

    if lines and lines[-1].strip() == term:
        lines.pop()

    # Réécrire proprement, avec un \n final (bonne pratique POSIX)
    with path.open("w", encoding="utf-8") as f:
        if lines:
            f.write("\n".join(lines) + "\n")

def create_json_conjecture(
    prompt: str,
    watch_dir: Path,
    *,
    ext: str = ".json",
    term: str = "FIN",
    codex_cwd: Optional[Path] = None,
) -> Path | None:
    """
    Lance 'codex' dans `watch_dir`, détecte le NOUVEAU fichier créé (par défaut .json),
    puis le surveille jusqu’à ce que sa dernière ligne non vide égale `term`.
    Termine proprement le processus enfant, nettoie la fin du fichier, et retourne le chemin.
    """
    watch_dir.mkdir(parents=True, exist_ok=True)

    def list_files(d: Path) -> list[Path]:
        files = [p for p in d.iterdir() if p.is_file()]
        if ext:
            files = [p for p in files if p.suffix == ext]
        return files

    baseline = set(p.resolve() for p in list_files(watch_dir))

    run_dir = codex_cwd or Path.cwd()

    proc = Popen(
        ["codex", "--sandbox=danger-full-access", prompt],
        cwd=str(run_dir),
    )

    start = time.time()
    target: Optional[Path] = None

    try:
        while True:
            # a) Le processus a-t-il terminé tout seul ?
            if proc.poll() is not None:
                if target is None:
                    candidates = [p for p in watch_dir.iterdir() if p.is_file()]
                    if ext:
                        candidates = [p for p in candidates if p.suffix == ext]
                    target = newest(candidates)
                break

            # b) Détecter le nouveau fichier
            if target is None:
                candidates = [p.resolve() for p in watch_dir.iterdir() if p.is_file()]
                if ext:
                    candidates = [p for p in candidates if p.suffix == ext]
                new_files = [p for p in candidates if p not in baseline]
                if new_files:
                    target = newest(new_files)

            # c) Condition d’arrêt: dernière ligne == term
            if target and target.exists():
                if last_nonempty_line(target) == term:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                    # petite période de grâce
                    end_grace = time.time() + 1.0
                    while proc.poll() is None and time.time() < end_grace:
                        time.sleep(POLL_INTERVAL)
                    if proc.poll() is None:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                    break

            time.sleep(POLL_INTERVAL)
    finally:
        # Filet de sécurité
        if proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass
            time.sleep(0.5)
            if proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass

    # Nettoyage du marqueur "FIN" si on a bien un fichier
    if target and target.exists():
        strip_trailing_term_file(target, term=term)
        return target
    return None
