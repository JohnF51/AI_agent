import asyncio
import sys
import os
import platform
from google.antigravity import Agent
from agent import create_agent_config

# ANSI farby pre terminálové rozhranie
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def get_git_branch():
    import subprocess
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL)
        return branch.decode("utf-8").strip()
    except Exception:
        return "unknown"

async def main():
    if sys.platform == 'win32':
        os.system("") # Zapne podporu ANSI farieb vo Windows konzole
        
    config = create_agent_config()
    
    print(f"{CYAN}{BOLD}============================================================{RESET}")
    print(f"{GREEN}{BOLD}      Antigravity AI Agent - Vylepšené lokálne rozhranie{RESET}")
    print(f"{CYAN}============================================================{RESET}")
    print(f" Napíš {YELLOW}help{RESET} alebo {YELLOW}?{RESET} pre zoznam príkazov a schopností.")
    print(f" Napíš {RED}exit{RESET} pre ukončenie programu.")
    print(f"{CYAN}============================================================{RESET}")
    
    async with Agent(config) as agent:
        while True:
            try:
                # Načítanie vstupu
                sys.stdout.write(f"\n{GREEN}{BOLD}Užívateľ:{RESET} ")
                sys.stdout.flush()
                
                # Použijeme executor na neblokujúce načítanie vstupu z konzoly
                user_input = await asyncio.get_event_loop().run_in_executor(None, input)
                user_input_stripped = user_input.strip()
                
                if not user_input_stripped:
                    continue
                
                cmd = user_input_stripped.lower()
                
                if cmd in ("exit", "/exit"):
                    print(f"{YELLOW}Ukončujem reláciu a zatváram agenta...{RESET}")
                    break
                    
                elif cmd in ("help", "?", "/help", "h"):
                    print(f"\n{CYAN}{BOLD}--- NÁPOVEDA & DOSTUPNÉ MOŽNOSTI ---{RESET}")
                    print(f"{BOLD}Vstavané príkazy v príkazovom riadku:{RESET}")
                    print(f"  {YELLOW}help{RESET} / {YELLOW}?{RESET}      - Zobrazí túto nápovedu.")
                    print(f"  {YELLOW}clear{RESET} / {YELLOW}cls{RESET}   - Vyčistí obrazovku terminálu.")
                    print(f"  {YELLOW}status{RESET}        - Vypíše informácie o konfigurácii a prostredí.")
                    print(f"  {YELLOW}exit{RESET}          - Bezpečne ukončí program.")
                    print(f"\n{BOLD}Čo všetko dokáže tento AI Agent (schopnosti):{RESET}")
                    print("  - Zistiť systémové informácie o tvojom PC (OS, disky).")
                    print("  - Prehliadať priečinky projektu a hľadať v nich súbory.")
                    print("  - Vyhľadávať konkrétne kódové fragmenty (grep) v súboroch.")
                    print("  - Čítať a analyzovať obsahy súborov projektu.")
                    print("  - Prehľadávať internet a čítať dokumentácie na webových stránkach.")
                    print(f"  - Spúšťať shell príkazy ({RED}bezpečnostná poistka{RESET}: pred spustením si vyžiada schválenie).")
                    print(f"{CYAN}------------------------------------{RESET}")
                    continue
                    
                elif cmd in ("clear", "cls", "/clear"):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                    
                elif cmd in ("status", "/status"):
                    print(f"\n{CYAN}{BOLD}--- STAV SYSTÉMU & AGENTA ---{RESET}")
                    print(f"  Platforma:      {platform.system()} {platform.release()} ({platform.machine()})")
                    print(f"  Adresár:        {os.getcwd()}")
                    api_key_status = f"{GREEN}Nájdený a aktívny{RESET}" if os.environ.get("GEMINI_API_KEY") else f"{RED}Chýba / Vyžiadaný{RESET}"
                    print(f"  Gemini API kľúč: {api_key_status}")
                    print(f"  Aktuálna vetva: {CYAN}{get_git_branch()}{RESET}")
                    print(f"{CYAN}-----------------------------{RESET}")
                    continue
                
                print(f"{YELLOW}Agent premýšľa...{RESET}")
                response = await agent.chat(user_input_stripped)
                print(f"\n{CYAN}{BOLD}Agent:{RESET} {await response.text()}")
                
            except KeyboardInterrupt:
                print(f"\n{YELLOW}Ukončujem reláciu...{RESET}")
                break
            except Exception as e:
                print(f"\n{RED}Nastala chyba: {e}{RESET}")

if __name__ == "__main__":
    # Nastavenie podpory pre Windows Event Loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
