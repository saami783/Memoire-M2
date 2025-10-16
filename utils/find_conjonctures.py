from __future__ import annotations
import os, time, signal, subprocess, sys
from pathlib import Path
from typing import Optional

def run_codex_until_sentinel(prompt: str, sentinel: str = "DONE_CONJECTURES_ANALYSIS.txt") -> Optional[Path]:
    """
    Lance Codex dans un processus fils (Unix/macOS) ou sous-processus (Windows).
    Boucle jusqu'à la création de la sentinelle (fichier vide). À ce moment,
    stoppe Codex et rend le Path de la sentinelle.
    """
    sent = Path.cwd() / sentinel

    def _done():
        if not sent.exists():
            sent.write_text("", encoding="utf-8")
        return sent

    if hasattr(os, "fork"):
        pid = os.fork()
        if pid == 0:
            os.execvp("codex", ["codex", "--sandbox=danger-full-access", prompt])
            os._exit(1)

        try:
            while True:
                child, _ = os.waitpid(pid, os.WNOHANG)
                if child != 0:
                    return sent if sent.exists() else None
                if sent.exists():
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        os.waitpid(pid, 0)
                    except ChildProcessError:
                        pass
                    return _done()

                time.sleep(0.2)
        finally:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass
    else:
        p = subprocess.Popen(
            ["codex", "--sandbox=danger-full-access", prompt],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            while True:
                if sent.exists():
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
                    return _done()

                if p.poll() is not None:
                    return sent if sent.exists() else None

                time.sleep(0.2)
        finally:
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
