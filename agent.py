import os
import platform
import shutil
import asyncio
import base64
import hashlib
from google.antigravity import LocalAgentConfig
from google.antigravity.hooks import policy

KEY_FILE = ".api_key.enc"

def get_machine_key() -> str:
    # Stable machine-specific key
    try:
        login = os.getlogin()
    except Exception:
        login = os.environ.get("USERNAME", os.environ.get("USER", "unknown"))
    data = (
        platform.node() + 
        login + 
        platform.processor() + 
        platform.system()
    )
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def encrypt_key(api_key: str) -> str:
    key = get_machine_key()
    key_bytes = key.encode('utf-8')
    data_bytes = api_key.encode('utf-8')
    encrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)])
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_key(encrypted_base64: str) -> str:
    key = get_machine_key()
    key_bytes = key.encode('utf-8')
    data_bytes = base64.b64decode(encrypted_base64.encode('utf-8'))
    decrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)])
    return decrypted.decode('utf-8')

def load_or_prompt_api_key() -> str:
    # 1. First check environment variable
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
        
    # 2. Check if encrypted file exists
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                encrypted_content = f.read().strip()
            decrypted = decrypt_key(encrypted_content)
            if decrypted:
                # Set it in env so google-antigravity finds it automatically
                os.environ["GEMINI_API_KEY"] = decrypted
                return decrypted
        except Exception as e:
            print(f"[VAROVANIE] Nepodarilo sa dešifrovať API kľúč zo súboru: {e}")
            
    # 3. If not found, prompt the user
    print("\n--- Nastavenie Gemini API kľúča ---")
    print("API kľúč nebol nájdený v premenných prostredia ani v šifrovanom súbore.")
    try:
        api_key = input("Zadaj svoj Gemini API kľúč (vstup bude zašifrovaný a uložený): ").strip()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("\n[CHYBA] Zadávanie API kľúča bolo prerušené.")
    
    if not api_key:
        raise ValueError("API kľúč nemôže byť prázdny.")
        
    # Encrypt and save
    try:
        encrypted = encrypt_key(api_key)
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            f.write(encrypted)
        print(f"[OK] API kľúč bol úspešne zašifrovaný a uložený do súboru '{KEY_FILE}'.")
    except Exception as e:
        print(f"[VAROVANIE] Nepodarilo sa uložiť zašifrovaný kľúč: {e}")
        
    os.environ["GEMINI_API_KEY"] = api_key
    return api_key


# 1. Definícia vlastného nástroja (Tool)
def get_system_info() -> str:
    """
    Získa základné informácie o operačnom systéme a voľnom mieste na disku.
    Tento nástroj neprijíma žiadne parametre.
    """
    system = platform.system()
    release = platform.release()
    try:
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (2**30)
        disk_info = f"Voľné miesto na disku C: {free_gb:.2f} GB"
    except Exception:
        disk_info = "Informácie o disku nie sú k dispozícii."
        
    return f"Operačný systém: {system} {release}\n{disk_info}"

# 2. Definovanie asynchrónneho handlera pre overovanie akcií (ask_user)
async def confirm_with_user(tool_call) -> bool:
    print(f"\n--- [BEZPEČNOSŤ] Požiadavka na spustenie nástroja '{tool_call.name}' ---")
    if hasattr(tool_call, "arguments") and tool_call.arguments:
        print(f"Argumenty: {tool_call.arguments}")
    
    # Použitie executor-a, aby sme nezablokovali event loop počas čakania na vstup
    loop = asyncio.get_event_loop()
    user_response = await loop.run_in_executor(
        None, 
        lambda: input("Povoliť vykonanie tohto príkazu? (y/n): ")
    )
    return user_response.strip().lower() == "y"

# 3. Nastavenie konfigurácie agenta s bezpečnostnými pravidlami
def create_agent_config() -> LocalAgentConfig:
    # Načítanie alebo vyžiadanie API kľúča
    load_or_prompt_api_key()
    
    # Definujeme zoznam pravidiel
    policies = [
        policy.allow("view_file"),                                  # Povoliť bezpečné čítanie súborov
        policy.allow("list_directory"),                            # Povoliť zobrazenie zoznamu súborov
        policy.allow("find_file"),                                 # Povoliť vyhľadávanie súborov podľa názvu
        policy.allow("search_directory"),                          # Povoliť vyhľadávanie textu v súboroch (grep)
        policy.allow("search_web"),                                # Povoliť vyhľadávanie na webe
        policy.allow("read_url_content"),                          # Povoliť načítanie obsahu z webu
        policy.ask_user("run_command", handler=confirm_with_user),  # Vyžiadať si súhlas užívateľa pre shell príkazy
        policy.deny("*")                                            # Zvyšok zakázať (deny by default)
    ]
    
    config = LocalAgentConfig(
        system_instructions=(
            "Si špecializovaný a inteligentný asistent pre správu lokálneho vývojového prostredia.\n"
            "Máš prístup k nasledujúcim nástrojom pre plnenie úloh:\n"
            "- `get_system_info`: Zistenie detailov o OS a voľnom mieste na disku.\n"
            "- `list_directory`: Zobrazenie zoznamu súborov v projekte.\n"
            "- `find_file`: Vyhľadávanie súborov podľa názvu.\n"
            "- `search_directory`: Vyhľadávanie konkrétneho textu/kódu v súboroch (grep).\n"
            "- `view_file`: Čítanie obsahu súborov.\n"
            "- `search_web`: Vyhľadávanie informácií a programátorskej dokumentácie na webe.\n"
            "- `read_url_content`: Načítanie celého textu/dokumentácie zo špecifických URL adries.\n"
            "- `run_command`: Spúšťanie systémových príkazov (vždy vyžaduje potvrdenie užívateľom).\n\n"
            "Komunikuj vždy jasne, vecne, konštruktívne a výhradne po slovensky. "
            "Pred spustením príkazov cez run_command sa uisti, že sú bezpečné a vysvetli užívateľovi ich účel."
        ),
        tools=[get_system_info],
        policies=policies
    )
    return config
