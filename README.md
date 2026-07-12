# Lokálny AI Agent s Google Antigravity SDK a 'uv'

Tento projekt demonštruje vytvorenie a spustenie vlastného autonómneho AI agenta pomocou knižnice `google-antigravity` a správcu balíkov `uv`.

## Rýchly štart (Automatická inštalácia)

Pre automatickú inštaláciu `uv`, Pythonu a všetkých závislostí stačí spustiť skript **`setup.bat`** (napr. dvojklikom alebo spustením v termináli):

```cmd
setup.bat
```

Skript automaticky:
1. Skontroluje / nainštaluje správcu balíkov `uv`.
2. Nainštaluje Python verzie 3.12.
3. Vytvorí lokálne virtuálne prostredie `.venv`.
4. Nainštaluje `google-antigravity` z `requirements.txt`.

Po dokončení inštalácie spustíte agenta príkazom:
```bash
uv run main.py
```

---

## Manuálny postup

Ak preferujete manuálnu inštaláciu krok po kroku, postupujte takto:

### 1. Inštalácia `uv`
- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- Alebo cez **pip**:
  ```bash
  pip install uv
  ```

### 2. Inštalácia Pythonu
```bash
uv python install 3.12
```

### 3. Vytvorenie a aktivácia virtuálneho prostredia
```bash
uv venv --python 3.12
```

Aktivácia:
- **PowerShell:** `.venv\Scripts\Activate.ps1`
- **CMD:** `.venv\Scripts\activate.bat`

### 4. Inštalácia závislostí
```bash
uv pip install -r requirements.txt
```

### 5. Spustenie agenta
```bash
uv run main.py
```

## Príklady na vyskúšanie v chate
1. **Zistenie informácií o systéme:** Opýtajte sa agenta: *"Aké sú systémové informácie?"* alebo *"Zisti voľné miesto na disku C"*.
2. **Bezpečnostný test (Human-in-the-loop):** Prikážte agentovi: *"Spusti príkaz whoami"* alebo *"Zobraz súbory v priečinku"*. Agent si pred spustením shell príkazu vyžiada vaše povolenie.
