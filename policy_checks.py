BANNED_KEYWORDS = [
    "violent content",
    "hate speech",
    # Add additional banned keywords as needed.
]

def check_script_compliance(script_text: str) -> bool:
    """
    Checks if the script complies with content policies.
    Returns False if any banned keywords are detected.
    """
    text_lower = script_text.lower()
    for kw in BANNED_KEYWORDS:
        if kw.lower() in text_lower:
            return False
    return True

def sanitize_script(script_text: str) -> str:
    """
    Sanitizes the script by replacing banned keywords with asterisks.
    """
    sanitized = script_text
    for kw in BANNED_KEYWORDS:
        sanitized = sanitized.replace(kw, "****")
    return sanitized
