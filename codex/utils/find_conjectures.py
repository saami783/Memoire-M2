# find_conjectures.py
from __future__ import annotations
import os, time, signal, subprocess
from pathlib import Path
from typing import Optional

__all__ = ["run_conjecture_analysis"]

SENTINEL_DEFAULT = "DONE_CONJECTURES_ANALYSIS.txt"


def _is_empty_file(path: Path) -> bool:
    try:
        return path.exists() and path.stat().st_size == 0
    except FileNotFoundError:
        return False


def run_conjecture_analysis(prompt: str, done_filename: str = SENTINEL_DEFAULT) -> Optional[Path]:
    """
    Lance Codex pour analyser des PDFs et extraire les conjectures (selon un prompt).
    Le processus parent attend que `done_filename` soit créé (fichier vide), puis
    tue Codex et rend le Path du fichier sentinelle.

    - `prompt`: le prompt passé à `codex --sandbox=danger-full-access`
    - `done_filename`: nom du fichier sentinelle à attendre (vide)

    Retourne Path(done_filename) si créé, sinon None.
    """

    done_path = Path.cwd() / done_filename

    # --- Implémentation Unix/macOS (fork), avec fallback subprocess pour Windows ---
    if hasattr(os, "fork"):
        pid = os.fork()
        if pid == 0:
            # Processus fils : remplace par Codex
            os.execvp("codex", ["codex", "--sandbox=danger-full-access", prompt])
            os._exit(1)  # si exec échoue
        else:
            # Processus père : boucle jusqu'à la création du fichier sentinelle vide
            try:
                while True:
                    # Si le fils s'est terminé de lui-même, on sort de la boucle
                    child, _ = os.waitpid(pid, os.WNOHANG)
                    if child != 0:
                        break

                    if _is_empty_file(done_path):
                        # Condition satisfaite → terminer le fils et continuer
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        try:
                            os.waitpid(pid, 0)  # éviter zombie
                        except ChildProcessError:
                            pass
                        print(f"OK, conjectures analysées. Sentinelle : {done_path}")
                        return done_path

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

            # Si on arrive ici sans sentinelle, on vérifie une dernière fois
            return done_path if _is_empty_file(done_path) else None

    else:
        # Fallback (Windows) : subprocess + polling du fichier sentinelle
        p = subprocess.Popen(
            ["codex", "--sandbox=danger-full-access", prompt],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            while True:
                # Si le processus Codex a terminé, on s'arrête
                if p.poll() is not None:
                    break

                if _is_empty_file(done_path):
                    # Terminer Codex proprement
                    try:
                        p.terminate()
                    except Exception:
                        pass
                    try:
                        p.wait(timeout=2)
                    except Exception:
                        try:
                            p.kill()
                        except Exception:
                            pass
                    print(f"OK, conjectures analysées. Sentinelle : {done_path}")
                    return done_path

                time.sleep(0.2)
        finally:
            # Sécurité
            try:
                p.terminate()
            except Exception:
                pass
            try:
                p.wait(timeout=2)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass

        return done_path if _is_empty_file(done_path) else None
