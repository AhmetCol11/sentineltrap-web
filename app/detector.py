import re

# SQLi, XSS, scanner pattern'leri
SQLI_PATTERNS = [
    r"'", r'"', r"--", r";", r"\bOR\b", r"\bAND\b",
    r"\bSELECT\b", r"\bUNION\b", r"\bINSERT\b", r"\bDROP\b",
    r"\bDELETE\b", r"\bUPDATE\b", r"\bEXEC\b", r"\bXP_\b",
    r"1=1", r"1=2"
]

XSS_PATTERNS = [
    r"<script", r"</script>", r"javascript:", r"onerror=",
    r"onload=", r"alert\(", r"document\.cookie", r"<iframe",
    r"<img", r"eval\("
]

SCANNER_PATTERNS = [
    r"sqlmap", r"nikto", r"nmap", r"masscan", r"nessus",
    r"burpsuite", r"metasploit", r"hydra", r"dirbuster",
    r"../", r"etc/passwd", r"cmd\.exe", r"powershell"
]


def _check_patterns(text: str, patterns: list) -> bool:
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def detect_payload(payload: dict) -> str | None:
    """
    Verilen sözlük payload'ını analiz eder.
    Saldırı türü tespit edilirse türünün adını döner, aksi halde None.
    """
    combined = " ".join(str(v) for v in payload.values())

    if _check_patterns(combined, SQLI_PATTERNS):
        return "SQLi"
    if _check_patterns(combined, XSS_PATTERNS):
        return "XSS"
    if _check_patterns(combined, SCANNER_PATTERNS):
        return "Scanner"
    return None
