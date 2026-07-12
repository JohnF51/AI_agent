import asyncio
import sys
import os
import platform
from google.antigravity import Agent
from agent import create_agent_config

# ANSI colors for terminal interface
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

def select_model() -> str:
    # Clear screen first to present the selection menu cleanly
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"{CYAN}{BOLD}============================================================{RESET}")
    print(f"{GREEN}{BOLD}              Gemini Model Selection Menu{RESET}")
    print(f"{CYAN}============================================================{RESET}")
    print("Choose a Gemini model to run your AI Agent:")
    print(f"  1) {GREEN}Gemini 3.5 Flash{RESET} (Default)   - Fastest, optimized for speed and agents")
    print(f"  2) {GREEN}Gemini 3.5 Pro{RESET}             - Ultimate reasoning, coding and agent performance")
    print(f"  3) {GREEN}Gemini 3.1 Pro{RESET}             - Stable reasoning and coding flagship")
    print(f"  4) {GREEN}Gemini 3.1 Flash Lite{RESET}      - Efficient, cost-effective, high-volume tasks")
    print(f"  5) {GREEN}Gemini 3.0 Pro{RESET}             - Legacy reasoning model")
    print(f"  6) {GREEN}Gemini 3.0 Flash{RESET}           - Legacy lightweight speed model")
    print("  7) Custom model name")
    print(f"{CYAN}============================================================{RESET}")
    
    try:
        choice = input("Enter choice [1-7, default: 1]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{YELLOW}Selection interrupted. Using default Gemini 3.5 Flash.{RESET}")
        return "gemini-3.5-flash"
        
    if not choice or choice == "1":
        return "gemini-3.5-flash"
    elif choice == "2":
        return "gemini-3.5-pro"
    elif choice == "3":
        return "gemini-3.1-pro"
    elif choice == "4":
        return "gemini-3.1-flash-lite"
    elif choice == "5":
        return "gemini-3.0-pro"
    elif choice == "6":
        return "gemini-3.0-flash"
    elif choice == "7":
        try:
            custom_name = input("Enter custom model name (e.g. gemini-3.5-flash-latest): ").strip()
            return custom_name if custom_name else "gemini-3.5-flash"
        except (KeyboardInterrupt, EOFError):
            return "gemini-3.5-flash"
    else:
        print(f"{YELLOW}Invalid choice. Defaulting to Gemini 3.5 Flash.{RESET}")
        return "gemini-3.5-flash"

async def main():
    if sys.platform == 'win32':
        os.system("") # Enable ANSI colors in Windows console
        
    selected_model = select_model()
    config = create_agent_config(model_name=selected_model)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{CYAN}{BOLD}============================================================{RESET}")
    print(f"{GREEN}{BOLD}      Antigravity AI Agent - Enhanced CLI Interface{RESET}")
    print(f"{CYAN}============================================================{RESET}")
    print(f" Model selected: {GREEN}{selected_model}{RESET}")
    print(f" Type {YELLOW}help{RESET} or {YELLOW}?{RESET} for commands and capabilities.")
    print(f" Type {RED}exit{RESET} to exit the session.")
    print(f"{CYAN}============================================================{RESET}")
    
    # Initialize token counters
    total_input_tokens = 0
    total_output_tokens = 0
    
    async with Agent(config) as agent:
        while True:
            try:
                # Prompt user input
                sys.stdout.write(f"\n{GREEN}{BOLD}User:{RESET} ")
                sys.stdout.flush()
                
                # Use executor to fetch console input asynchronously
                user_input = await asyncio.get_event_loop().run_in_executor(None, input)
                user_input_stripped = user_input.strip()
                
                if not user_input_stripped:
                    continue
                
                cmd = user_input_stripped.lower()
                
                if cmd in ("exit", "/exit"):
                    print(f"{YELLOW}Exiting the session and closing the agent...{RESET}")
                    break
                    
                elif cmd in ("help", "?", "/help", "h"):
                    print(f"\n{CYAN}{BOLD}--- HELP & AVAILABLE COMMANDS ---{RESET}")
                    print(f"{BOLD}Local Console Commands:{RESET}")
                    print(f"  {YELLOW}help{RESET} / {YELLOW}?{RESET}      - Show this help menu.")
                    print(f"  {YELLOW}clear{RESET} / {YELLOW}cls{RESET}   - Clear the console screen.")
                    print(f"  {YELLOW}status{RESET}        - Display system, environment and API config.")
                    print(f"  {YELLOW}exit{RESET}          - Terminate the program session.")
                    print(f"\n{BOLD}AI Agent Capabilities:{RESET}")
                    print("  - Retrieve system metrics and hardware info (OS, disk space).")
                    print("  - Browse workspace folders and find files by name.")
                    print("  - Perform grep text search across codebase files.")
                    print("  - Read and analyze file contents of the project.")
                    print("  - Query the web and read documentation from URLs.")
                    print(f"  - Execute shell commands ({RED}requires user approval confirmation{RESET}).")
                    print(f"{CYAN}---------------------------------{RESET}")
                    continue
                    
                elif cmd in ("clear", "cls", "/clear"):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                    
                elif cmd in ("status", "/status"):
                    print(f"\n{CYAN}{BOLD}--- ENVIRONMENT & AGENT STATUS ---{RESET}")
                    print(f"  Platform:        {platform.system()} {platform.release()} ({platform.machine()})")
                    print(f"  CWD:             {os.getcwd()}")
                    print(f"  Active Model:    {GREEN}{selected_model}{RESET}")
                    api_key_status = f"{GREEN}Loaded & Active{RESET}" if os.environ.get("GEMINI_API_KEY") else f"{RED}Missing / Prompted{RESET}"
                    print(f"  Gemini API Key:  {api_key_status}")
                    print(f"  Current Branch:  {CYAN}{get_git_branch()}{RESET}")
                    print(f"  Session Tokens:  Input: {total_input_tokens} | Output: {total_output_tokens} | Total: {total_input_tokens + total_output_tokens}")
                    print(f"{CYAN}----------------------------------{RESET}")
                    continue
                
                print(f"{YELLOW}Agent thinking...{RESET}")
                response = await agent.chat(user_input_stripped)
                print(f"\n{CYAN}{BOLD}Agent:{RESET} {await response.text()}")
                
                # Update and print token usage
                usage = response.usage_metadata
                if usage:
                    in_t = usage.prompt_token_count or 0
                    out_t = usage.candidates_token_count or 0
                    th_t = usage.thoughts_token_count or 0
                    tot_t = usage.total_token_count or 0
                    
                    total_input_tokens += in_t
                    total_output_tokens += out_t
                    
                    print(f"\n{YELLOW}[Tokens - Turn: In: {in_t} | Out: {out_t}", end="")
                    if th_t > 0:
                        print(f" (Thinking: {th_t})", end="")
                    print(f" | Total: {tot_t}]")
                    print(f"[Tokens - Session: In: {total_input_tokens} | Out: {total_output_tokens} | Total: {total_input_tokens + total_output_tokens}]{RESET}")
                
            except KeyboardInterrupt:
                print(f"\n{YELLOW}Session interrupted by user. Exiting...{RESET}")
                break
            except Exception as e:
                print(f"\n{RED}Error occurred: {e}{RESET}")

if __name__ == "__main__":
    # Configure Windows Event Loop Policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
