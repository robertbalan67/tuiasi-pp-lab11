"""
Pipeline de procesare fișiere cu ThreadPoolExecutor.

Fiecare fișier trece prin 3 etape:
  read_file → count_words → write_result (JSON)
"""

from __future__ import annotations
import json
import os
from concurrent.futures import ThreadPoolExecutor


# ─── Funcții individuale ──────────────────────────────────────────────────────

def read_file(path: str) -> str:
    """Citește și returnează conținutul unui fișier text UTF-8."""
    with open(path, encoding="utf-8") as f:
        return f.read()


def count_words(text: str) -> dict[str, int]:
    """
    Numără frecvența cuvintelor din text.
    Separatori: spații și newline-uri (orice whitespace).

    Exemplu:
        count_words("ana are mere") == {'ana': 1, 'are': 1, 'mere': 1}
        count_words("a a b")        == {'a': 2, 'b': 1}
        count_words("")             == {}
    """
    if not text or not text.strip():
        return {}
    counts: dict[str, int] = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def write_result(result: dict, output_path: str) -> None:
    """Scrie result-ul în format JSON la output_path."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


# ─── Pipeline paralel ─────────────────────────────────────────────────────────

def process_files_pipeline(input_paths: list[str], output_dir: str) -> None:
    """
    Procesează mai multe fișiere simultan cu ThreadPoolExecutor.

    Pentru fiecare cale din input_paths:
      1. read_file(path)  → text
      2. count_words(text) → dict de frecvențe
      3. write_result(dict, output_dir/<basename>.json) → fișier JSON

    Exemplu:
        process_files_pipeline(["/tmp/doc1.txt", "/tmp/doc2.txt"], "/tmp/output/")
        # Creează /tmp/output/doc1.json și /tmp/output/doc2.json
    """
    os.makedirs(output_dir, exist_ok=True)

    def _process_single(path: str) -> None:
        text       = read_file(path)
        word_counts = count_words(text)
        base       = os.path.splitext(os.path.basename(path))[0]
        out_path   = os.path.join(output_dir, f"{base}.json")
        write_result(word_counts, out_path)

    with ThreadPoolExecutor() as executor:
        # map() garantează că excepțiile sunt propagate și așteptăm finalizarea
        list(executor.map(_process_single, input_paths))
