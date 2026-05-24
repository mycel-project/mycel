import re

from pathlib import Path

class AppInfos:
    def __init__(self):
        try:
            raw = Path("VERSION").read_text().strip()
            self.version = re.sub(r'-(alpha|beta|rc).*', '', raw)
        except FileNotFoundError:
            self.version = "unknown"
