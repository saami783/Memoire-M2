from __future__ import annotations
import os, time, signal
from pathlib import Path

def last_nonempty_line(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
        for line in reversed(lines):
            if line.strip():
                return line.strip()
    except FileNotFoundError:
        pass
    return ""

def create_boolean_queries_file(prompt: str, filename: str = "boolean_queries.txt") -> Path | None:
    """
    Lance Codex dans un processus fils pour générer boolean_queries.txt.
    Le processus père boucle jusqu'à ce que la dernière ligne du fichier
    soit exactement le nom du fichier, puis tue le fils et continue.
    Retourne le Path du fichier si présent, sinon None.
    """
    outpath = Path.cwd() / filename

    pid = os.fork()
    if pid == 0:
        # Processus fils : exécute Codex
        os.execvp("codex", ["codex", "--sandbox=danger-full-access", prompt])
        os._exit(1)  # si exec échoue

    # Processus père : surveille et stoppe le fils quand le fichier est finalisé
    try:
        while True:
            child, _ = os.waitpid(pid, os.WNOHANG)
            if child != 0:
                # Codex s'est terminé de lui-même
                break

            if outpath.exists():
                last = last_nonempty_line(outpath)
                if last == outpath.name:
                    # Termination condition atteinte → tuer le fils et sortir
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        os.waitpid(pid, 0)  # éviter zombie
                    except ChildProcessError:
                        pass
                    print(f"OK, boolean queries écrites : {outpath}")
                    break

            time.sleep(0.2)
    finally:
        # Filet de sécurité si le fils est encore vivant
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            os.waitpid(pid, 0)
        except ChildProcessError:
            pass

    return outpath if outpath.exists() else None
