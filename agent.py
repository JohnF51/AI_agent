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
            print(f"[WARNING] Failed to decrypt API key from file: {e}")
            
    # 3. If not found, prompt the user
    print("\n--- Gemini API Key Setup ---")
    print("API key was not found in environment variables or the encrypted file.")
    try:
        api_key = input("Enter your Gemini API key (input will be encrypted and saved): ").strip()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("\n[ERROR] API key input was interrupted.")
    
    if not api_key:
        raise ValueError("API key cannot be empty.")
        
    # Encrypt and save
    try:
        encrypted = encrypt_key(api_key)
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            f.write(encrypted)
        print(f"[OK] API key was successfully encrypted and saved to file '{KEY_FILE}'.")
    except Exception as e:
        print(f"[WARNING] Failed to save encrypted key: {e}")
        
    os.environ["GEMINI_API_KEY"] = api_key
    return api_key


# 1. Definition of custom tool
def get_system_info() -> str:
    """
    Get basic information about the operating system and free disk space.
    This tool does not accept any parameters.
    """
    system = platform.system()
    release = platform.release()
    try:
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (2**30)
        disk_info = f"Free disk space on C: {free_gb:.2f} GB"
    except Exception:
        disk_info = "Disk information is not available."
        
    return f"Operating System: {system} {release}\n{disk_info}"

# 2. Definition of asynchronous handler for verifying actions (ask_user)
async def confirm_with_user(tool_call) -> bool:
    print(f"\n--- [SECURITY] Request to execute tool '{tool_call.name}' ---")
    if hasattr(tool_call, "arguments") and tool_call.arguments:
        print(f"Arguments: {tool_call.arguments}")
    
    # Use executor to avoid blocking the event loop while waiting for input
    loop = asyncio.get_event_loop()
    user_response = await loop.run_in_executor(
        None, 
        lambda: input("Allow execution of this command? (y/n): ")
    )
    return user_response.strip().lower() == "y"

# 3. Setting up agent configuration with safety policies
def create_agent_config(model_name: str = "gemini-3.5-flash") -> LocalAgentConfig:
    # Load or request API key
    load_or_prompt_api_key()
    
    # Define rule list
    policies = [
        policy.allow("view_file"),                                  # Allow safe file reading
        policy.allow("list_directory"),                            # Allow listing directory contents
        policy.allow("find_file"),                                 # Allow finding files by name
        policy.allow("search_directory"),                          # Allow grep search within files
        policy.allow("search_web"),                                # Allow searching the web
        policy.allow("read_url_content"),                          # Allow reading web content
        policy.ask_user("run_command", handler=confirm_with_user),  # Ask for user consent for shell commands
        policy.deny("*")                                            # Deny everything else by default
    ]
    
    config = LocalAgentConfig(
        model=model_name,
        system_instructions=(
            "You are a specialized and intelligent assistant for managing the local development environment.\n"
            "You have access to the following tools to fulfill user requests:\n"
            "- `get_system_info`: Get OS details and free disk space.\n"
            "- `list_directory`: View list of files in the project.\n"
            "- `find_file`: Search for files by name.\n"
            "- `search_directory`: Find specific text/code fragments inside files (grep).\n"
            "- `view_file`: Read the content of files.\n"
            "- `search_web`: Search for information and programming documentation on the web.\n"
            "- `read_url_content`: Fetch text/documentation from specific URL addresses.\n"
            "- `run_command`: Run system terminal commands (always requires user approval).\n\n"
            "Always communicate clearly, concisely, constructively, and exclusively in English. "
            "Before executing commands via run_command, verify that they are safe and explain their purpose to the user."
        ),
        tools=[get_system_info],
        policies=policies
    )
    return config
