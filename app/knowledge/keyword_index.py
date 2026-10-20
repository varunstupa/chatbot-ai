"""Keyword (BM25) search over the guide chunks, next to the semantic search.

Semantic search blurs exact screen labels ("Payment & Invoice", "Enable Streaming")
and message texts; keyword search finds them. The index is built in memory from the
chunks already stored in Chroma and rebuilt when the guides change. No access
decisions here: the caller passes the doc_ids it may read.
"""

from __future__ import annotations

import difflib
import math
import re
from collections import Counter
from dataclasses import dataclass

# Question words that say nothing about the topic; they would only add noise.
_STOPWORDS = frozenset(
    """a an and are as at be by can could do does for from get got how i if in into is it
    its me my of on or our so than that the their them then there these this to us was we
    what when where which who why will with would you your please want need should""".split()
)


def tokens(text: str) -> list[str]:
    """Lowercase words of every script, without stop words, plurals made singular."""
    words = re.sub(r"[\W_]+", " ", (text or "").casefold()).split()
    out = []
    for w in words:
        if w in _STOPWORDS or len(w) < 2:
            continue
        out.append(_singular(w))
    return out


def _singular(word: str) -> str:
    """English plural to singular, enough to match "matches" with "match" and "categories" with "category"."""
    if len(word) <= 3:
        return word
    if word.endswith(("ches", "shes", "sses", "xes", "zes")):
        return word[:-2]
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


@dataclass(frozen=True)
class KeywordHit:
    chunk_id: str
    doc_id: str
    score: float


class KeywordIndex:
    """BM25 (k1=1.5, b=0.75) over chunk title + section + text."""

    def __init__(self, rows: list[tuple[str, str, str]], k1: float = 1.5, b: float = 0.75):
        """rows: (chunk_id, doc_id, searchable text)."""
        self._k1, self._b = k1, b
        self._ids = [r[0] for r in rows]
        self._docs = [r[1] for r in rows]
        self._tf = [Counter(tokens(r[2])) for r in rows]
        self._len = [sum(tf.values()) for tf in self._tf]
        self._avg = (sum(self._len) / len(self._len)) if self._len else 0.0
        df: Counter[str] = Counter()
        for tf in self._tf:
            df.update(tf.keys())
        n = len(rows)
        self._idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self._vocab = [t for t in self._idf if len(t) >= 4]
        self._fuzzy: dict[str, str | None] = {}

    def __len__(self) -> int:
        return len(self._ids)

    def _known(self, word: str) -> str | None:
        """The word itself when a guide uses it; else the closest guide word (typos, "predefine").

        Only words no guide uses are mapped, so exact matches never change.
        """
        if word in self._idf:
            return word
        if len(word) < 5:
            return None
        if word not in self._fuzzy:
            starts = [w for w in self._idf if w.startswith(word) and len(w) - len(word) <= 3]
            close = starts or difflib.get_close_matches(word, self._vocab, n=1, cutoff=0.85)
            self._fuzzy[word] = min(close, key=len) if close else None
        return self._fuzzy[word]

    def search(self, query: str, doc_ids: set[str], limit: int) -> list[KeywordHit]:
        """Best chunks of the given documents, highest score first; chunks with no match are left out."""
        terms = [t for t in dict.fromkeys(self._known(w) for w in tokens(query)) if t]
        if not terms or limit <= 0:
            return []
        scored: list[KeywordHit] = []
        for i, tf in enumerate(self._tf):
            if self._docs[i] not in doc_ids:
                continue
            score = 0.0
            norm = self._k1 * (1 - self._b + self._b * self._len[i] / (self._avg or 1))
            for t in terms:
                f = tf.get(t)
                if f:
                    score += self._idf[t] * f * (self._k1 + 1) / (f + norm)
            if score > 0:
                scored.append(KeywordHit(self._ids[i], self._docs[i], score))
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:limit]
