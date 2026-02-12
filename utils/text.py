# utils/text.py
import re

TITLE_CUSTOMER_DELIM = "--"


def label_ends_with_ku(label: str) -> bool:
    """
    True wenn Label am Schluss 'KU' hat, z.B. 'E65-441-KU'.
    Erlaubt auch ' ... KU' oder '...-KU' (case-insensitive).
    """
    s = (label or "").strip()
    if not s:
        return False
    return re.search(r"(?i)(?:[-\s])KU\s*$", s) is not None


def split_title_and_customer(full_title: str):
    s = (full_title or "").strip()
    if not s:
        return "(ohne Titel)", ""
    if TITLE_CUSTOMER_DELIM in s:
        left, right = s.split(TITLE_CUSTOMER_DELIM, 1)
        return left.strip() or "(ohne Titel)", right.strip()
    return s, ""
