from bs4 import BeautifulSoup
import unicodedata
import re

def normalize_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)

def strip_html(text: str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def normalize_spacing(text: str) -> str:
    """
    Normalize spacing in Vietnamese text:
    - Remove redundant whitespace
    - Remove space before punctuation
    - Ensure exactly one space after punctuation
    - Fix spacing inside parentheses and quotes
    """

    # Remove space before punctuation
    text = re.sub(r"\s+([.,;:?!])", r"\1", text)

    # Ensure exactly one space after punctuation
    text = re.sub(r"([.,;:?!])\s*", r"\1 ", text)

    # Remove space after opening brackets/quotes
    text = re.sub(r"([\(\[\{“‘])\s+", r"\1", text)

    # Remove space before closing brackets/quotes
    text = re.sub(r"\s+([\)\]\}”’])", r"\1", text)

    # Collapse multiple spaces (including tabs, newlines) into one space
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing spaces
    return text.strip()

def remove_code_artifacts(text: str) -> str:
    """
    Remove common code artifacts (HTML, JS, CSS, ad snippets) from crawled text.
    More robust to extra spaces around dots and operators.
    """

    # Remove <script>, <style>, <noscript> blocks
    text = re.sub(r"<(script|style|noscript).*?>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Remove inline HTML tags likely ads or embeds
    text = re.sub(r"<(iframe|ins|object|embed|link|meta|base|source|track)[^>]*?>.*?</\1>", "", text,
                  flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<(iframe|ins|object|embed|link|meta|base|source|track)[^>]*?>", "", text,
                  flags=re.IGNORECASE)

    # Remove Google ads/analytics snippets (tolerant to spaces around dots)
    text = re.sub(
        r"\(\s*adsbygoogle\s*=\s*window\s*\.\s*adsbygoogle\s*\|\|\s*\[\s*\]\s*\)\s*\.\s*push\s*\([^)]*\);?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"googletag\s*\.\s*\w+\s*\([^)]*\);?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"gtag\s*\([^)]*\);?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"dataLayer\s*\.\s*push\s*\([^)]*\);?", "", text, flags=re.IGNORECASE)

    # Remove generic JS array pushes or object literals
    text = re.sub(r"\[[^\]]*\]\s*\.\s*push\s*\(\{.*?\}\);?", "", text, flags=re.DOTALL)

    # Remove event handler attributes like onclick="..."
    text = re.sub(r'on\w+\s*=\s*"[^"]*"', "", text, flags=re.IGNORECASE)
    text = re.sub(r"on\w+\s*=\s*'[^']*'", "", text, flags=re.IGNORECASE)

    # Remove inline style attributes if undesired
    text = re.sub(r'style\s*=\s*"[^"]*"', "", text, flags=re.IGNORECASE)

    # Remove leftover braces or code fragments { ... } ; 
    text = re.sub(r"\{[^{}]*\};?", "", text)

    # Collapse whitespace
    text = re.sub(r"\s{2,}", " ", text).strip()

    return text