import os, time, signal
from pathlib import Path

def create_pico_file(prompt: str):
    pid = os.fork()
    if pid == 0:
        # Processus fils
        os.execvp("codex", ["codex", "--sandbox=danger-full-access", prompt])
        os._exit(1)

    # Processus père
    try:
        while True:
            child, _ = os.waitpid(pid, os.WNOHANG)
            if child != 0:
                # Codex s'est terminé de lui-même (avec ou sans fichier)
                break

            # y a-t-il un PICO*.txt ?
            f = latest_pico_file()
            if f and f.exists():
                last = last_nonempty_line(f)
                if last == f.name:
                    # condition satisfaite -> tuer le fils et continuer
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        os.waitpid(pid, 0)  # éviter zombie
                    except ChildProcessError:
                        pass
                    print(f"OK, fichier créé et finalisé : {f}")
                    break

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

def latest_pico_file() -> Path | None:
    files = list(Path.cwd().glob("PICO*.txt"))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)

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