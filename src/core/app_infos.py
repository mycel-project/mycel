from pathlib import Path


class AppInfos:
    def __init__(self):
        try:
            self.version = Path("VERSION").read_text().strip()
        except FileNotFoundError:
            self.version = "unknown"
