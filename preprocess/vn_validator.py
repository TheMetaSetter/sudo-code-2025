# -*- coding: utf-8 -*-
from __future__ import annotations
import unicodedata
import unicodedata as ud
import re
from dataclasses import dataclass
from typing import List, Optional
from preprocess.text_normalizer import normalize_nfc

# -------------------------------
# Data structures for reporting
# -------------------------------

@dataclass
class ValidationIssue:
    issue_type: str           # e.g., "INVISIBLE_CHAR", "CONFUSABLE", "COMBINING", "FAKE_LETTER", "TONE_PLACEMENT"
    message: str              # human-readable explanation
    start: int                # character index in the original string
    end: int                  # end index (exclusive)
    snippet: str              # local context excerpt
    suggestion: Optional[str] = None  # minimal hint/fix if feasible

@dataclass
class ValidationReport:
    issues: List[ValidationIssue]

    def summary_by_type(self):
        counts = {}
        for it in self.issues:
            counts[it.issue_type] = counts.get(it.issue_type, 0) + 1
        return counts


# -----------------------------------
# Utilities and Vietnamese definitions
# -----------------------------------

# Invisible / zero-width / spacing specials to flag
INVISIBLE_CODEPOINTS = {
    "\u200B",  # ZWSP
    "\u200C",  # ZWNJ
    "\u200D",  # ZWJ
    "\u2060",  # WJ
    "\u00A0",  # NBSP
    "\uFEFF",  # BOM / ZWNBSP
}

# Tone marks (combining) used in Vietnamese (NFD analysis)
# Note: Vietnamese tone marks include: acute, grave, hook above, tilde, dot below.
COMBINING_TONE_MARKS = {
    "\u0301",  # COMBINING ACUTE ACCENT
    "\u0300",  # COMBINING GRAVE ACCENT
    "\u0309",  # COMBINING HOOK ABOVE
    "\u0303",  # COMBINING TILDE
    "\u0323",  # COMBINING DOT BELOW
}

# Other combining marks used with Vietnamese vowels
COMBINING_VIET_MARKS = {
    "\u0302",  # COMBINING CIRCUMFLEX -> â, ê, ô
    "\u0306",  # COMBINING BREVE -> ă
    "\u031B",  # COMBINING HORN -> ơ, ư
}

# Allowed combining set for Vietnamese
ALLOWED_COMBINING = COMBINING_TONE_MARKS | COMBINING_VIET_MARKS

# Simple Latin block check (heuristic): reject obvious Greek, Cyrillic by Unicode block name
# Python doesn't expose "script", so we rely on name() prefixes.
def is_clearly_non_latin(ch: str) -> bool:
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return False
    # Accept ASCII controls/space/punct/digits as non-problematic; focus on letters.
    if ch.isalpha():
        if "GREEK" in name or "CYRILLIC" in name or "HEBREW" in name or "ARABIC" in name \
           or "DEVANAGARI" in name or "CJK" in name or "HIRAGANA" in name or "KATAKANA" in name:
            return True
    return False

# Vietnamese vowels (base letters), including y as vowel role in orthography
VOWELS_BASE = set("aeiouyAEIOUY")
# Vietnamese precomposed vowels often seen (NFC): include diacritics to detect vowel presence quickly
VIET_VOWEL_PRECOMPOSED = set("aăâeêioôơuưyAĂÂEÊIOÔƠUƯY")

# Quick helper to generate local snippet around a span
def local_snippet(text: str, start: int, end: int, radius: int = 10) -> str:
    s = max(0, start - radius)
    e = min(len(text), end + radius)
    return text[s:e]


# -----------------------------------
# Core validator
# -----------------------------------

class VietnameseTextValidator:
    """
    Validate Vietnamese text AFTER NFC normalization.
    Focus: invisible chars, confusables, combining mark validity, fake letters,
           and tone placement (heuristic).
    """

    def __init__(self):
        # precompile patterns
        # Rough tokenization: split on whitespace and punctuation, keep tokens with letters/digits/diacritics/hyphen
        self.token_pattern = re.compile(r"[A-Za-zÀ-ỹ\-]+", flags=re.UNICODE)

    # ---------- Public API ----------

    def validate(self, nfc_text: str) -> ValidationReport:
        issues: List[ValidationIssue] = []
        issues += self.scan_invisible_chars(nfc_text)
        issues += self.scan_non_latin_confusables(nfc_text)
        issues += self.scan_combining_sequences(nfc_text)
        issues += self.scan_fake_letters(nfc_text)
        issues += self.scan_tone_placement(nfc_text)
        return ValidationReport(issues=issues)

    # ---------- Step A: Invisible chars ----------

    def scan_invisible_chars(self, text: str) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        for i, ch in enumerate(text):
            if ch in INVISIBLE_CODEPOINTS:
                issues.append(ValidationIssue(
                    issue_type="INVISIBLE_CHAR",
                    message=f"Zero-width or non-breaking character U+{ord(ch):04X} detected.",
                    start=i, end=i+1, snippet=local_snippet(text, i, i+1),
                    suggestion="Remove this character."
                ))
        return issues

    # ---------- Step B: Non-Latin confusables ----------

    def scan_non_latin_confusables(self, text: str) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        for i, ch in enumerate(text):
            if is_clearly_non_latin(ch):
                issues.append(ValidationIssue(
                    issue_type="CONFUSABLE",
                    message=f"Non-Latin letter '{ch}' (likely confusable) found.",
                    start=i, end=i+1, snippet=local_snippet(text, i, i+1),
                    suggestion="Replace with the correct Latin letter."
                ))
        return issues

    # ---------- Step C: Combining sequence sanity (NFD analysis) ----------

    def scan_combining_sequences(self, text: str) -> List[ValidationIssue]:
        """
        Decompose to NFD and ensure:
          - At most one tone mark per base letter.
          - Combining marks appear only on vowels.
          - Only Vietnamese-relevant combining marks are used.
        """
        issues: List[ValidationIssue] = []
        i = 0
        while i < len(text):
            ch = text[i]
            # Skip non-letters quickly; punctuation/space are safe
            if not ch.isalpha():
                i += 1
                continue

            # Decompose the single NFC char to NFD pieces
            nfd = unicodedata.normalize("NFD", ch)
            base = nfd[0]
            comb = nfd[1:]

            # Count tone marks
            tone_count = sum(1 for c in comb if c in COMBINING_TONE_MARKS)
            if tone_count > 1:
                issues.append(ValidationIssue(
                    issue_type="COMBINING",
                    message="A letter carries more than one tone mark.",
                    start=i, end=i+1, snippet=local_snippet(text, i, i+1),
                    suggestion="Keep only one tone mark (acute/grave/hook/tilde/dot-below)."
                ))

            # Only vowels should carry tone/diacritics in Vietnamese
            if comb and (base.lower() not in "aeiouy"):
                issues.append(ValidationIssue(
                    issue_type="COMBINING",
                    message="Combining mark(s) applied on a non-vowel letter.",
                    start=i, end=i+1, snippet=local_snippet(text, i, i+1),
                    suggestion="Move the mark to the correct vowel."
                ))

            # Disallow combining marks outside Vietnamese set
            for c in comb:
                if c not in ALLOWED_COMBINING:
                    cp = f"U+{ord(c):04X}"
                    issues.append(ValidationIssue(
                        issue_type="COMBINING",
                        message=f"Unsupported combining mark {cp} for Vietnamese.",
                        start=i, end=i+1, snippet=local_snippet(text, i, i+1),
                        suggestion="Use Vietnamese tone/diacritic marks only."
                    ))

            i += 1

        return issues

    # ---------- Step D: Fake letters detection ----------

    def scan_fake_letters(self, text: str) -> List[ValidationIssue]:
        """
        Detect obvious attempts to 'fake' Vietnamese letters using overlays or wrong marks in NFD.
        Examples:
          - 'd' + COMBINING SHORT STROKE OVERLAY -> pretend to be 'đ'
          - 'o'/'u' + wrong combining to mimic 'ơ'/'ư'
        """
        issues: List[ValidationIssue] = []
        for idx, ch in enumerate(text):
            nfd = unicodedata.normalize("NFD", ch)
            base = nfd[0]
            comb = nfd[1:]

            # 'đ' must be U+0111 / 'Đ' U+0110 in NFC; flag 'd' with overlays
            if base in ('d', 'D') and comb:
                # Any overlay-ish marks are suspicious (not part of Vietnamese set)
                suspicious = [c for c in comb if c not in ALLOWED_COMBINING]
                if suspicious:
                    issues.append(ValidationIssue(
                        issue_type="FAKE_LETTER",
                        message="Possible fake 'đ' constructed by overlays.",
                        start=idx, end=idx+1, snippet=local_snippet(text, idx, idx+1),
                        suggestion="Use the precomposed 'đ' (U+0111) or 'Đ' (U+0110)."
                    ))

            # For ơ/ư, horn must be U+031B; if other odd marks used, flag
            if base in ('o','O','u','U') and comb:
                has_horn = any(c == "\u031B" for c in comb)
                # If looks like someone tries to bend into ơ/ư without horn
                # (we only flag when there is any combining but not horn and not typical tone/mũ/breve)
                if not has_horn:
                    non_viet = [c for c in comb if c not in (ALLOWED_COMBINING - {"\u031B"})]
                    if non_viet:
                        issues.append(ValidationIssue(
                            issue_type="FAKE_LETTER",
                            message="Suspicious attempt to mimic 'ơ/ư' without using horn (U+031B).",
                            start=idx, end=idx+1, snippet=local_snippet(text, idx, idx+1),
                            suggestion="Use precomposed 'ơ/ư' or add COMBINING HORN."
                        ))
        return issues

    # ---------- Step E: Tone placement heuristic ----------

    def scan_tone_placement(self, text: str) -> List[ValidationIssue]:
        """
        Heuristic syllable-wise tone placement check for Vietnamese.
        Strategy:
          - Tokenize likely words (letters/hyphen).
          - For each token, find letters bearing a tone mark (via NFD).
          - Compute expected tone-bearing vowel index using safe rules.
          - If exactly one tone is present but sits on a different vowel than expected, flag.
        """
        issues: List[ValidationIssue] = []
        for m in self.token_pattern.finditer(text):
            token = m.group(0)
            tone_positions = self._tone_positions_in_token(token)
            if len(tone_positions) != 1:
                # 0 or >1 tones: skip here; combining step already flags multi-tones
                continue

            tone_idx = tone_positions[0]  # index within token
            expected_idx = self._expected_tone_index(token)

            if expected_idx is not None and expected_idx != tone_idx:
                glob_start = m.start() + tone_idx
                glob_end = glob_start + 1
                issues.append(ValidationIssue(
                    issue_type="TONE_PLACEMENT",
                    message=f"Tone mark appears on the wrong vowel in '{token}'.",
                    start=glob_start, end=glob_end,
                    snippet=local_snippet(text, glob_start, glob_end),
                    suggestion="Move the tone to the main vowel per Vietnamese orthography."
                ))

        return issues

    # ----- Helpers for tone placement -----

    def _tone_positions_in_token(self, token: str) -> List[int]:
        """Return indices of letters in token that carry a tone mark (NFD analysis per char)."""
        positions = []
        for i, ch in enumerate(token):
            nfd = unicodedata.normalize("NFD", ch)
            comb = nfd[1:]
            if any(c in COMBINING_TONE_MARKS for c in comb):
                positions.append(i)
        return positions

    def _expected_tone_index(self, token: str) -> Optional[int]:
        """
        Determine expected tone-bearing vowel index using safe heuristics.
        Steps:
          - Extract indices of vowels within the token.
          - Prefer the vowel that already has non-tone Vietnamese diacritic (circumflex/breve/horn).
          - Handle common clusters:
              * iê / uô / ươ + coda: tone on ê/ô/ơ
              * ia / ua / ưa with no coda: tone on a
              * oa / oe / uy: tone on second vowel
              * uyê: tone on ê
          - If ambiguous, return None (no flag).
        """
        # Identify vowels with their NFD features
        chars = list(token)
        vowel_indices = [i for i, ch in enumerate(chars) if self._is_vowel_letter(ch)]
        if not vowel_indices:
            return None

        # If exactly one vowel -> tone should be there
        if len(vowel_indices) == 1:
            return vowel_indices[0]

        # Prefer a vowel that has circumflex/breve/horn (as main vowel)
        nfd_marks = [self._nfd_marks(chars[i]) for i in vowel_indices]
        prefers = {"\u0302", "\u0306", "\u031B"}  # ^, breve, horn
        preferred = [vi for vi, marks in zip(vowel_indices, nfd_marks) if any(m in prefers for m in marks)]
        if len(preferred) == 1:
            return preferred[0]

        # Build a simple lowercase view for pattern checks
        low = token.lower()

        # Detect presence of coda (final consonant) roughly: if ends with consonant or 'ng/nh/ch/nh'
        # This is heuristic; we only need to know if there's a coda for iê/uô/ươ rule.
        has_coda = bool(re.search(r"[bcdđghklmnpqrstvxỳỵỷỹý]$|ng$|nh$|ch$", low))

        # Cluster-based rules:
        # uyê -> tone on ê
        m = re.search(r"uyê", low)
        if m:
            # Put tone on the ê within the token
            idx = self._find_char_with_base_and_mark(chars, base_set={'e','E'}, need_mark="\u0302")  # ê has ^ in NFD
            if idx is not None:
                return idx

        # iê/uô/ươ + coda: tone on ê/ô/ơ
        if has_coda:
            for base, mark in (('e', "\u0302"), ('o', "\u0302"), ('o', "\u031B")):
                idx = self._find_char_with_base_and_mark(chars, base_set={base, base.upper()}, need_mark=mark)
                if idx is not None:
                    return idx

        # No coda with ia/ua/ưa: tone on 'a'
        if not has_coda and re.search(r"(ia|ua|ưa)$", low):
            for i in range(len(chars)-1, -1, -1):
                if chars[i].lower() == 'a':
                    return i

        # oa/oe/uy: tone on the second vowel in that cluster if present
        for pat in ("oa", "oe", "uy"):
            m = re.search(pat, low)
            if m:
                # pick the vowel index that matches the second letter of the cluster
                start = m.start()
                second = start + 1
                # map to token indices among vowels
                if second < len(chars) and self._is_vowel_letter(chars[second]):
                    return second

        # If multiple vowels with diacritics, ambiguity rises – avoid false positives
        return None

    def _nfd_marks(self, ch: str) -> List[str]:
        nfd = unicodedata.normalize("NFD", ch)
        return list(nfd[1:])

    def _is_vowel_letter(self, ch: str) -> bool:
        # Consider as vowel if base is a/e/i/o/u/y or the NFC precomposed Vietnamese versions
        base = unicodedata.normalize("NFD", ch)[0]
        return base in VOWELS_BASE or ch in VIET_VOWEL_PRECOMPOSED

    def _find_char_with_base_and_mark(self, chars: List[str], base_set: set, need_mark: str) -> Optional[int]:
        for i, ch in enumerate(chars):
            nfd = unicodedata.normalize("NFD", ch)
            base = nfd[0]
            comb = nfd[1:]
            if base in base_set and need_mark in comb:
                return i
        return None


# -------------------------------
# Convenience function
# -------------------------------

def validate_vietnamese_text(nfc_text: str) -> ValidationReport:
    """
    High-level entry for validating Vietnamese text after NFC normalization.
    """
    validator = VietnameseTextValidator()
    return validator.validate(nfc_text)

# ---- Small, safe fixers corresponding to validator issue types ---------------

# Minimal homoglyph mapping (very conservative) from common non-Latin lookalikes to Latin
# Reference: Unicode confusables data & UTS #39 concept; here we only include a tiny safe subset.
HOMOGLYPH_SAFE_MAP = {
    "\u0430": "a",  # Cyrillic 'a' -> Latin 'a'
    "\u0435": "e",  # Cyrillic 'e' -> Latin 'e'
    "\u0440": "p",  # Cyrillic 'er' -> Latin 'p'
    "\u0441": "c",  # Cyrillic 'es' -> Latin 'c'
    "\u0456": "i",  # Cyrillic 'i' -> Latin 'i'
    "\u03B1": "a",  # Greek alpha -> Latin 'a'
    "\u03BF": "o",  # Greek omicron -> Latin 'o'
    "\u03B5": "e",  # Greek epsilon -> Latin 'e'
    # Add more only if you are confident; keep it conservative to avoid false fixes.
}

COMBINING_MAJOR_VIET = {
    "\u0302",  # circumflex  -> â ê ô
    "\u0306",  # breve       -> ă
    "\u031B",  # horn        -> ơ ư
}

ALLOWED_COMBINING = COMBINING_TONE_MARKS | COMBINING_MAJOR_VIET

def strip_invisible_characters(nfc_text: str) -> str:
    """
    Remove invisible/zero-width and NBSP-like characters.
    This is safe and generally desirable before indexing/searching.
    """
    return "".join(ch for ch in nfc_text if ch not in INVISIBLE_CODEPOINTS)

def replace_safe_homoglyphs(nfc_text: str) -> str:
    """
    Replace a tiny, conservative set of common non-Latin homoglyphs with Latin equivalents.
    The mapping is intentionally minimal to avoid corrupting legitimate non-Latin text.
    """
    return "".join(HOMOGLYPH_SAFE_MAP.get(ch, ch) for ch in nfc_text)

def clamp_to_single_tone_per_letter(nfc_text: str) -> str:
    """
    Ensure each *letter* carries at most one tone mark.
    If multiple tone marks occur on the same character, keep the first and drop the rest.
    This is a narrow fix to handle 'COMBINING' issues safely.
    """
    out_chars: List[str] = []
    for ch in nfc_text:
        if not ch.isalpha():
            out_chars.append(ch)
            continue
        nfd = ud.normalize("NFD", ch)
        base, marks = nfd[0], list(nfd[1:])
        # Keep only the first tone mark (if any), and keep all non-tone Vietnamese marks
        seen_tone = False
        filtered: List[str] = []
        for m in marks:
            if m in COMBINING_TONE_MARKS:
                if not seen_tone:
                    filtered.append(m)
                    seen_tone = True
                # else drop extra tone marks
            elif m in COMBINING_MAJOR_VIET:
                filtered.append(m)
            else:
                # Drop unsupported combining marks on letters (safer)
                continue
        out_chars.append(ud.normalize("NFC", base + "".join(filtered)))
    return "".join(out_chars)

def move_tone_mark_within_token(token: str) -> str:
    """
    Move the tone mark to the 'expected' vowel position (heuristic).
    Only apply when:
      - token has exactly one tone-bearing letter
      - expected position is unambiguous (per heuristic)
    Otherwise return token unchanged.
    """
    # Helper functions reused from validator-like logic
    def nfd_marks(ch: str) -> List[str]:
        return list(ud.normalize("NFD", ch)[1:])
    def is_vowel(ch: str) -> bool:
        return ud.normalize("NFD", ch)[0] in VOWELS_BASE

    # Find tone-bearing index(es)
    tone_positions = []
    for i, ch in enumerate(token):
        if any(m in COMBINING_TONE_MARKS for m in nfd_marks(ch)):
            tone_positions.append(i)
    if len(tone_positions) != 1:
        return token  # ambiguous or no tone → do nothing

    tone_idx = tone_positions[0]

    # Compute expected vowel index (heuristic aligned with common rules)
    expected_idx = expected_tone_index_heuristic(token)
    if expected_idx is None or expected_idx == tone_idx:
        return token  # no need to move

    # Rebuild token: remove tone from current position, add to expected position
    chars = list(token)
    # Remove tone marks from current char
    base = ud.normalize("NFD", chars[tone_idx])[0]
    marks = [m for m in nfd_marks(chars[tone_idx]) if m not in COMBINING_TONE_MARKS]
    chars[tone_idx] = ud.normalize("NFC", base + "".join(marks))
    # Add tone to expected char (preserve existing marks + one tone)
    base_e = ud.normalize("NFD", chars[expected_idx])[0]
    marks_e = nfd_marks(chars[expected_idx])

    # If expected already has a tone (rare due to earlier clamp), keep it; else add original tone
    # Determine which tone was used originally by inspecting the original tone char
    orig_tone = None
    for m in ud.normalize("NFD", token[tone_idx])[1:]:
        if m in COMBINING_TONE_MARKS:
            orig_tone = m
            break
    if orig_tone and not any(m in COMBINING_TONE_MARKS for m in marks_e):
        marks_e.append(orig_tone)

    chars[expected_idx] = ud.normalize("NFC", base_e + "".join(marks_e))
    return "".join(chars)

def expected_tone_index_heuristic(token: str) -> int | None:
    """
    A conservative heuristic for Vietnamese tone placement:
      - Prefer the vowel that already has ^, ˘, or horn (â/ê/ô, ă, ơ/ư).
      - For iê/uô/ươ + coda: tone on ê/ô/ơ.
      - For ia/ua/ưa w/o coda: tone on a.
      - For oa/oe/uy: tone on the second vowel.
      - For uyê: tone on ê.
    Returns the target index or None if ambiguous.
    Sources summarize practice differences but agree on: tone goes on the main vowel
    and must sit on any vowel that already bears a quality diacritic. :contentReference[oaicite:5]{index=5}
    """
    chars = list(token)
    # Indices of vowels by base letter
    vowels = []
    for i, ch in enumerate(chars):
        base = ud.normalize("NFD", ch)[0]
        if base in VOWELS_BASE:
            vowels.append(i)
    if not vowels:
        return None
    if len(vowels) == 1:
        return vowels[0]

    # Prefer vowel carrying ^, ˘, or horn
    prefer_marks = {"\u0302", "\u0306", "\u031B"}
    preferred = [i for i in vowels if any(m in prefer_marks for m in ud.normalize("NFD", chars[i])[1:])]
    if len(preferred) == 1:
        return preferred[0]

    low = token.lower()

    # Simple 'coda' heuristic: final consonant exists?
    has_coda = bool(re.search(r"(ng|nh|ch|[bcdđghklmnpqrstvx])$", low))

    # uyê -> tone on ê
    if "uyê" in low:
        for i, ch in enumerate(chars):
            nfd = ud.normalize("NFD", ch)
            if nfd[0].lower() == 'e' and "\u0302" in nfd[1:]:  # ê
                return i

    # iê/uô/ươ + coda: tone on ê/ô/ơ
    if has_coda:
        for target in [('e', "\u0302"), ('o', "\u0302"), ('o', "\u031B")]:
            base_needed, mark_needed = target
            for i, ch in enumerate(chars):
                nfd = ud.normalize("NFD", ch)
                if nfd[0].lower() == base_needed and mark_needed in nfd[1:]:
                    return i

    # No coda & ia/ua/ưa -> tone on a
    if (not has_coda) and re.search(r"(ia|ua|ưa)$", low):
        for i in range(len(chars)-1, -1, -1):
            if ud.normalize("NFD", chars[i])[0].lower() == 'a':
                return i

    # oa/oe/uy -> tone on second vowel
    for pat in ("oa", "oe", "uy"):
        pos = low.find(pat)
        if pos != -1:
            second = pos + 1
            if second < len(chars) and ud.normalize("NFD", chars[second])[0].lower() in "aeiouy":
                return second

    return None


def fix_tone_placement_in_text(nfc_text: str) -> str:
    """
    Apply tone movement within tokens where heuristic is confident.
    Tokenization: letters & hyphen words.
    """
    token_pattern = re.compile(r"[A-Za-zÀ-ỹ\-]+", flags=re.UNICODE)
    out = []
    last_end = 0
    for m in token_pattern.finditer(nfc_text):
        out.append(nfc_text[last_end:m.start()])
        token = m.group(0)
        out.append(move_tone_mark_within_token(token))
        last_end = m.end()
    out.append(nfc_text[last_end:])
    return "".join(out)


# ---- 3) High-level pipeline -----------------------------------------------------

def validate_and_fix_vietnamese_text(raw_text: str):
    """
    Full pipeline:
      1) Normalize to NFC
      2) Validate (collect issues)
      3) Apply conservative fixes in passes:
         a) strip invisible chars
         b) replace safe homoglyphs
         c) clamp to single tone per letter
         d) move tone mark to expected vowel (heuristic)
      4) Re-run validation to report any remaining issues
    Returns: (fixed_text, initial_report, final_report)
    """
    # 1) Normalize
    nfc_text = normalize_nfc(raw_text)

    # 2) Validate before fixes
    initial_report = validate_vietnamese_text(nfc_text)

    # 3) Fix passes (conservative)
    fixed = nfc_text
    fixed = strip_invisible_characters(fixed)        # safe strip
    fixed = replace_safe_homoglyphs(fixed)           # safe homoglyph reduction
    fixed = clamp_to_single_tone_per_letter(fixed)   # sanitize multi-tone per letter
    fixed = fix_tone_placement_in_text(fixed)        # move tone when unambiguous

    # 4) Validate after fixes
    final_report = validate_vietnamese_text(fixed)

    return fixed, initial_report, final_report