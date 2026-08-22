import json
from pathlib import Path
 
CONFIG = Path("config.json")
EXAMPLE = Path("config.json.example")
 
 
def merge_config():
    if not CONFIG.exists() or not EXAMPLE.exists():
        return
 
    current = json.loads(CONFIG.read_text())
    example = json.loads(EXAMPLE.read_text())
 
    missing = {k: v for k, v in example.items() if k not in current}
 
    if not missing:
        print("Config is up to date, nothing to add.")
        return
 
    # Backup before touching anything
    backup = CONFIG.with_suffix(".json.bak")
    backup.write_text(json.dumps(current, indent=4))
 
    current.update(missing)
    CONFIG.write_text(json.dumps(current, indent=4))
 
    print(f"Added {len(missing)} new config option(s), using example defaults:")
    for k, v in missing.items():
        print(f"  {k} = {json.dumps(v)}")
    print(f"\nYour existing settings were kept as-is.")
    print(f"A backup of the previous config.json was saved to {backup.name}")
    print("Review the new values above and adjust if needed.")
 
 
if __name__ == "__main__":
    merge_config()
 
