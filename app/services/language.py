"""Detect the language a question is written in, so the answer can use the same one."""

from __future__ import annotations

import re
from dataclasses import dataclass
from threading import Lock

from lingua import Language, LanguageDetector, LanguageDetectorBuilder

# Below this confidence (short inputs such as "ok") the language is left to the model.
_MIN_CONFIDENCE = 0.6
# Low-accuracy candidates below this are noise, not worth a high-accuracy model.
_MIN_CANDIDATE = 0.05
_MAX_CANDIDATES = 3
_NAMES = {Language.BOKMAL: "Norwegian", Language.NYNORSK: "Norwegian"}

_lock = Lock()
_detector: LanguageDetector | None = None
# High-accuracy detectors per candidate set; their models load lazily, so memory
# only grows with the languages users actually write in.
_verifiers: dict[frozenset[Language], LanguageDetector] = {}


@dataclass(frozen=True)
class QuestionLanguage:
    code: str  # ISO 639-1, lowercase ("de", "hi")
    name: str  # English name for the prompt ("German")


# Hindi written in English letters ("event live nahi ho raha"). The detectors read it as
# Tagalog, Indonesian and the like, so common Hindi words decide it first. Words that are
# also English ("me", "ho", "to", "so") are left out.
_HINGLISH_WORDS = frozenset(
    """nahi nahin nhi kya kaise kaisa kese kyu kyun kyon hai hain raha rahi rahe karun karu
    karna karni karein kare karte karta karo kijiye mein ko ka ki ke se aur bhi dikh dikhta dikhai
    bana banaye banana chahiye kaha kahan kab kaun mera meri mujhe hum aap apna wala wali hota hoti
    hua gaya gayi sakte sakta sakti batao bataye liye abhi galat sahi theek thik chal chalu kuch
    agar lekin isme usme yaha yahan waha wahan""".split()
)
HINGLISH = QuestionLanguage(code="hi-latn", name="Hinglish (Hindi written in English letters)")


def is_hinglish(text: str) -> bool:
    """Latin-letter text with at least two distinct common Hindi words."""
    if re.search("[ऀ-ॿ]", text):  # Devanagari is plain Hindi
        return False
    words = set(re.findall(r"[a-z]+", text.casefold()))
    return len(words & _HINGLISH_WORDS) >= 2


def _get_detector() -> LanguageDetector:
    global _detector
    with _lock:
        if _detector is None:
            _detector = (
                LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()
            )
        return _detector


def _get_verifier(candidates: frozenset[Language]) -> LanguageDetector:
    with _lock:
        verifier = _verifiers.get(candidates)
        if verifier is None:
            verifier = LanguageDetectorBuilder.from_languages(*candidates).build()
            _verifiers[candidates] = verifier
        return verifier


def detect_language(text: str) -> QuestionLanguage | None:
    """The question's language, or None when it cannot be told reliably.

    The low-accuracy pass over all languages names the candidates; a high-accuracy
    pass then decides between them and English. Low accuracy alone reads short
    English questions such as "How do I forfeit a player?" as German.
    """
    text = (text or "").strip()
    if is_hinglish(text):
        return HINGLISH
    values = _get_detector().compute_language_confidence_values(text)
    if not values:
        return None
    candidates = {Language.ENGLISH} | {
        v.language for v in values[:_MAX_CANDIDATES] if v.value >= _MIN_CANDIDATE
    }
    if len(candidates) > 1:
        values = _get_verifier(frozenset(candidates)).compute_language_confidence_values(text)
    if not values or values[0].value < _MIN_CONFIDENCE:
        return None
    language = values[0].language
    code = language.iso_code_639_1.name.lower()
    if language in (Language.BOKMAL, Language.NYNORSK):
        code = "no"
    return QuestionLanguage(code=code, name=_NAMES.get(language, language.name.title()))
