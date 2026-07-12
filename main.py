import asyncio
import sys
from google.antigravity import Agent
from agent import create_agent_config

async def main():
    config = create_agent_config()
    
    print("=" * 60)
    print("Spúšťam Antigravity Agenta...")
    print("Môžeš klásť otázky (napr. 'Aké sú systémové informácie?').")
    print("Napíš 'exit' pre ukončenie programu.")
    print("=" * 60)
    
    async with Agent(config) as agent:
        while True:
            try:
                # Načítanie vstupu
                sys.stdout.write("\nUžívateľ: ")
                sys.stdout.flush()
                
                # Použijeme executor na neblokujúce načítanie vstupu z konzoly
                user_input = await asyncio.get_event_loop().run_in_executor(None, input)
                
                if user_input.strip().lower() == "exit":
                    print("Ukončujem reláciu...")
                    break
                
                if not user_input.strip():
                    continue
                
                print("Agent premýšľa...")
                response = await agent.chat(user_input)
                print(f"\nAgent: {await response.text()}")
                
            except KeyboardInterrupt:
                print("\nUkončujem reláciu...")
                break
            except Exception as e:
                print(f"\nNastala chyba: {e}")

if __name__ == "__main__":
    # Nastavenie podpory pre Windows Event Loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
