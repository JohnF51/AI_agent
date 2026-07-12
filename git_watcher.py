import os
import sys
import time
import subprocess

# Colors for terminal output
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

# Ignored directories and files
IGNORE_DIRS = {".git", ".venv", "__pycache__", ".idea", ".vscode"}
IGNORE_FILES = {"git_watcher.py", ".api_key.enc", ".gitignore"}

def get_git_branch():
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL)
        return branch.decode("utf-8").strip()
    except Exception:
        return "unknown"

def scan_files(root_dir):
    """Scans all tracked files and returns their paths and modification times."""
    files_state = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove ignored directories in place so os.walk doesn't enter them
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for filename in filenames:
            if filename in IGNORE_FILES:
                continue
            full_path = os.path.join(dirpath, filename)
            try:
                mtime = os.path.getmtime(full_path)
                files_state[full_path] = mtime
            except OSError:
                # File might have been deleted during scanning
                pass
    return files_state

def has_git_changes():
    """Checks if there are any changes in the repository ready to commit."""
    try:
        output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL)
        return len(output.strip()) > 0
    except Exception:
        return False

def run_git_sync():
    """Runs git add, commit, and push."""
    print(f"\n{CYAN}[WATCHER] Changes detected. Starting sync...{RESET}")
    
    # 1. Stage changes
    try:
        subprocess.check_call(["git", "add", "-A"])
        print(f"{GREEN}[WATCHER] git add -A (successful){RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}[WATCHER] Error in git add: {e}{RESET}")
        return

    # 2. Create commit
    commit_msg = "Code update by admin"
    try:
        subprocess.check_call(["git", "commit", "-m", commit_msg])
        print(f"{GREEN}[WATCHER] git commit (successful: '{commit_msg}'){RESET}")
    except subprocess.CalledProcessError as e:
        # Commit might fail if there are no changes (handled, but just in case)
        print(f"{YELLOW}[WATCHER] git commit info/warning: {e}{RESET}")
        return

    # 3. Push to remote
    try:
        branch = get_git_branch()
        print(f"{CYAN}[WATCHER] Pushing changes to branch '{branch}'...{RESET}")
        # Set a 30-second timeout on push to avoid freezing indefinitely
        subprocess.check_call(["git", "push", "origin", branch], timeout=30)
        print(f"{GREEN}[WATCHER] git push completed successfully!{RESET}")
    except subprocess.TimeoutExpired:
        print(f"{RED}[WATCHER] Error: git push timed out.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}[WATCHER] Error in git push: {e}{RESET}")
        print(f"{YELLOW}[TIP] Make sure your permissions are set up correctly and 'git push' works manually.{RESET}")

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 60)
    print(f"{GREEN}Starting Git Auto-Watcher for folder:{RESET}")
    print(f"  {root_dir}")
    print(f"Current branch: {CYAN}{get_git_branch()}{RESET}")
    print("Press Ctrl+C to exit.")
    print("=" * 60)

    # Initial state
    last_state = scan_files(root_dir)
    print(f"[WATCHER] Watching {len(last_state)} files. Waiting for changes...")

    while True:
        try:
            time.sleep(1.5)
            current_state = scan_files(root_dir)
            
            # Compare file states
            changed = False
            
            # Check for modified or added files
            for path, mtime in current_state.items():
                if path not in last_state or last_state[path] != mtime:
                    changed = True
                    break
            
            # Check for deleted files
            if not changed:
                for path in last_state:
                    if path not in current_state:
                        changed = True
                        break
            
            if changed:
                # Settle time (wait a bit to let file writes finish)
                time.sleep(1.0)
                # Update state
                last_state = scan_files(root_dir)
                
                # If git actually registers changes, sync them
                if has_git_changes():
                    run_git_sync()
                else:
                    print(f"{YELLOW}[WATCHER] Changes detected outside Git tracking (or ignored files).{RESET}")
            
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[WATCHER] Watching terminated by user.{RESET}")
            sys.exit(0)
        except Exception as e:
            print(f"{RED}[WATCHER] Unexpected error in main loop: {e}{RESET}")
            time.sleep(5)  # Short pause before restarting the loop

if __name__ == "__main__":
    # Enable ANSI colors in Windows Command Prompt (if needed)
    if sys.platform == "win32":
        os.system("")
    main()
