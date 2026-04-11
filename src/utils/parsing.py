from urllib.parse import urlparse
import socket
import ipaddress

def is_valid_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
    except Exception:
        return False


    # ✅ Schéma
    if parsed.scheme not in ("http", "https"):
        return False

    # ✅ Netloc
    if not parsed.netloc:
        return False

    # ✅ Bloquer localhost / IP privées
    try:
        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)

        if ip_obj.is_private or ip_obj.is_loopback:
            return False
    except Exception:
        return False

    return True
