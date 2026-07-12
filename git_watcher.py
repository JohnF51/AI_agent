import os
import sys
import time
import subprocess

# Farby pre terminálový výstup
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

# Ignorované priečinky a súbory
IGNORE_DIRS = {".git", ".venv", "__pycache__", ".idea", ".vscode"}
IGNORE_FILES = {"git_watcher.py", ".api_key.enc", ".gitignore"}

def get_git_branch():
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL)
        return branch.decode("utf-8").strip()
    except Exception:
        return "unknown"

def scan_files(root_dir):
    """Naskenuje všetky sledované súbory a vráti ich cesty a čas poslednej úpravy."""
    files_state = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Odstránime ignorované priečinky z dirnames na mieste, aby os.walk do nich nevstupoval
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for filename in filenames:
            if filename in IGNORE_FILES:
                continue
            full_path = os.path.join(dirpath, filename)
            try:
                mtime = os.path.getmtime(full_path)
                files_state[full_path] = mtime
            except OSError:
                # Súbor mohol byť vymazaný počas skenovania
                pass
    return files_state

def has_git_changes():
    """Skontroluje, či sú v repozitári nejaké zmeny pripravené na commit."""
    try:
        output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL)
        return len(output.strip()) > 0
    except Exception:
        return False

def run_git_sync():
    """Spustí git add, commit a push."""
    print(f"\n{CYAN}[WATCHER] Zmeny detegované. Spúšťam synchronizáciu...{RESET}")
    
    # 1. Pridanie zmien
    try:
        subprocess.check_call(["git", "add", "-A"])
        print(f"{GREEN}[WATCHER] git add -A (úspešné){RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}[WATCHER] Chyba pri git add: {e}{RESET}")
        return

    # 2. Vytvorenie commitu
    commit_msg = "Code update by admin"
    try:
        subprocess.check_call(["git", "commit", "-m", commit_msg])
        print(f"{GREEN}[WATCHER] git commit (úspešné: '{commit_msg}'){RESET}")
    except subprocess.CalledProcessError as e:
        # Commit môže zlyhať napr. ak nie sú žiadne zmeny (čo by malo byť ošetrené, ale pre istotu)
        print(f"{YELLOW}[WATCHER] git commit info/upozornenie: {e}{RESET}")
        return

    # 3. Odoslanie do remote
    try:
        branch = get_git_branch()
        print(f"{CYAN}[WATCHER] Odosielam zmeny do vetvy '{branch}'...{RESET}")
        # Nastavíme timeout 30 sekúnd na push, aby to nezamrzlo navždy
        subprocess.check_call(["git", "push", "origin", branch], timeout=30)
        print(f"{GREEN}[WATCHER] git push úspešne dokončený!{RESET}")
    except subprocess.TimeoutExpired:
        print(f"{RED}[WATCHER] Chyba: git push vypršal časový limit (timeout).{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}[WATCHER] Chyba pri git push: {e}{RESET}")
        print(f"{YELLOW}[TIP] Uisti sa, že máš správne nastavené oprávnenia a 'git push' funguje manuálne.{RESET}")

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 60)
    print(f"{GREEN}Spúšťam Git Auto-Watcher pre priečinok:{RESET}")
    print(f"  {root_dir}")
    print(f"Aktuálna vetva: {CYAN}{get_git_branch()}{RESET}")
    print("Pre ukončenie stlač Ctrl+C.")
    print("=" * 60)

    # Inicializačný stav
    last_state = scan_files(root_dir)
    print(f"[WATCHER] Sledujem {len(last_state)} súborov. Čakám na zmeny...")

    while True:
        try:
            time.sleep(1.5)
            current_state = scan_files(root_dir)
            
            # Porovnanie stavov súborov
            changed = False
            
            # Skontrolujeme zmenené alebo pridané súbory
            for path, mtime in current_state.items():
                if path not in last_state or last_state[path] != mtime:
                    changed = True
                    break
            
            # Skontrolujeme vymazané súbory
            if not changed:
                for path in last_state:
                    if path not in current_state:
                        changed = True
                        break
            
            if changed:
                # Settle time (počkať chvíľu, kým sa dokončia zápisy všetkých súborov)
                time.sleep(1.0)
                # Aktualizujeme stav
                last_state = scan_files(root_dir)
                
                # Ak git skutočne eviduje zmeny, synchronizujeme
                if has_git_changes():
                    run_git_sync()
                else:
                    print(f"{YELLOW}[WATCHER] Detegované zmeny mimo sledovania Gitu (alebo ignorované súbory).{RESET}")
            
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[WATCHER] Sledovanie ukončené užívateľom.{RESET}")
            sys.exit(0)
        except Exception as e:
            print(f"{RED}[WATCHER] Neočakávaná chyba v hlavnej slučke: {e}{RESET}")
            time.sleep(5) # Krátka pauza pred reštartom slučky

if __name__ == "__main__":
    # Zapnutie ANSI farieb vo Windows Command Prompt (ak je potrebné)
    if sys.platform == "win32":
        os.system("")
    main()
