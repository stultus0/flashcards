#!/usr/bin/env python3
"""Build an Italian flashcard app enriched from the source PDF's lesson text."""
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader


CHAPTER_TITLES = {
    1: "Piacere! Le presentazioni",
    2: "Il rappresentante e l'insegnante a lezione",
    3: "Ecco i nomi delle cose",
    4: "Un ufficio in città",
    5: "Tra il dire e il fare: i verbi",
    7: "Una malattia in famiglia",
    8: "Un altro ufficio in centro",
    9: "Un cappuccino al bar",
    10: "Una tazza di tè in sala da pranzo",
    11: "I numeri, finalmente i numeri",
    13: "Il nuovo sistema monetario",
    14: "I numeri nella vita di tutti i giorni",
    15: "Che ora è?",
    16: "Andiamo al cinema!",
    17: "Le date e la storia",
    19: "Dopo la storia, ecco la geografia",
    20: "Una giornata tipica",
    21: "La vita nel quartiere",
    22: "Che tempaccio!",
    23: "Aria di primavera",
    24: "Quella buona cucina italiana",
    25: "L'Italia: il bel paese",
    26: "Gli italiani e le italiane",
    27: "Progetti di viaggio",
    28: "Come si scrive una lettera",
    29: "Il piacere di ricevere una lettera",
    30: "Gli ultimi consigli prima di partire",
    31: "In partenza per l'Italia",
    32: "Finalmente l'arrivo a Roma",
    33: "Una famiglia italiana",
    34: "Una bella gita a Ostia",
    35: "Una passeggiata per Roma",
    36: "Nei dintorni di Roma",
    37: "Un fine-settimana a Siena",
    38: "…E qualche giorno a Firenze",
    39: "Finalmente insieme!",
    40: "Andarsene o rimanere?",
}


def normalize(text: str) -> str:
    # Preserve word boundaries for typographic apostrophes before ASCII folding.
    text = text.replace("’", "'").replace("‘", "'").replace("ʼ", "'")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def first_sentences(text: str, max_chars: int = 480) -> str:
    text = clean(text)
    if len(text) <= max_chars:
        return text
    boundaries = [
        match.start() + 1
        for match in re.finditer(r"(?<!Mr)(?<!Ms)(?<!Dr)(?<=[.!?])\s+", text)
        if match.start() + 1 <= max_chars
    ]
    if boundaries and boundaries[-1] >= 80:
        return text[: boundaries[-1]].strip()
    return text[:max_chars].rstrip(" ,;:") + "…"


def heading_case(text: str) -> str:
    text = clean(text).rstrip(".")
    if not text:
        return text
    return text[:1] + text[1:].lower()


def chapter_context(pages: list[str]) -> str:
    """Return a short, source-extracted lesson note for one chapter."""
    text = "\n".join(pages)
    intro_match = re.search(
        r"PRESENTAZIONE\s*[—-]\s*INTRODUCTION\s*(.*?)(?=VOCABOLARIO\s+NUOVO|NEW\s+VOCABULARY|$)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    parts: list[str] = []
    if intro_match:
        intro = first_sentences(intro_match.group(1))
        if intro:
            parts.append("Lesson context: " + intro)

    grammar_match = re.search(
        r"APPUNTI\s+DI\s+GRAMMATICA\s*[—-]\s*GRAMMAR\s+NOTES\s*(.*)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if grammar_match:
        grammar = grammar_match.group(1)[:7000]
        # Grammar headings end before exercises; otherwise numbered exercise
        # prompts are easily mistaken for grammar-topic headings.
        grammar = re.split(r"\b(?:ESERCIZI|EXERCISES|CHIACCHIERANDO)\b", grammar, maxsplit=1, flags=re.IGNORECASE)[0]
        headings = re.findall(r"(?:^|\n)\s*\d+\.\s*([^\n]+)", grammar)
        cleaned_headings = []
        for heading in headings:
            heading = heading_case(heading)
            if 6 <= len(heading) <= 100 and heading not in cleaned_headings:
                cleaned_headings.append(heading)
            if len(cleaned_headings) == 2:
                break
        if cleaned_headings:
            parts.append("Grammar: " + "; ".join(cleaned_headings) + ".")

    return " ".join(parts)


def merge_extra(existing: str, context: str) -> str:
    existing = (existing or "").strip()
    context = (context or "").strip()
    if not context or context in existing:
        return existing
    return f"{existing} {context}".strip()


def source_chapter_pages(reader: PdfReader) -> dict[int, list[str]]:
    pages = [page.extract_text() or "" for page in reader.pages]
    starts: dict[int, int] = {}
    for chapter, title in CHAPTER_TITLES.items():
        target = normalize(title)
        candidates = []
        for i, text in enumerate(pages):
            head = normalize(text[:500])
            if target in head:
                candidates.append(i)
        if not candidates:
            raise RuntimeError(f"Could not locate Chapter {chapter}: {title}")
        # The table of contents is before the actual lessons. The matching page
        # whose extracted text begins with the title is the lesson opening page.
        starts[chapter] = next((i for i in candidates if normalize(pages[i][:120]).startswith(target)), candidates[-1])

    ordered = sorted(starts.items(), key=lambda item: item[1])
    result: dict[int, list[str]] = {}
    for pos, (chapter, start) in enumerate(ordered):
        end = ordered[pos + 1][1] if pos + 1 < len(ordered) else len(pages)
        result[chapter] = pages[start:end]
    return result


def enrich_html(source_html: str, contexts: dict[int, str]) -> tuple[str, dict[str, int]]:
    changed = 0
    context_cards = 0

    def replace_card(match: re.Match[str]) -> str:
        nonlocal changed, context_cards
        obj = match.group(0)
        chapter_match = re.search(r'set:"ch(\d+)"', obj)
        if not chapter_match:
            return obj
        context = contexts.get(int(chapter_match.group(1)), "")
        if not context:
            return obj
        context_cards += 1
        extra_match = re.search(r',\s*extra:("(?:\\.|[^"\\])*")\s*(?=})', obj)
        existing = json.loads(extra_match.group(1)) if extra_match else ""
        merged = merge_extra(existing, context)
        if merged == existing:
            return obj
        encoded = json.dumps(merged, ensure_ascii=False)
        changed += 1
        if extra_match:
            return obj[:extra_match.start()] + ", extra:" + encoded + obj[extra_match.end():]
        return obj[:-1] + ", extra:" + encoded + " }"

    enriched = re.sub(r'\{\s*set:"ch\d+"[^\n]*\}', replace_card, source_html)
    return enriched, {"cards_with_source_context": context_cards, "cards_changed": changed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    reader = PdfReader(str(args.pdf))
    page_sets = source_chapter_pages(reader)
    contexts = {chapter: chapter_context(pages) for chapter, pages in page_sets.items()}
    missing = [chapter for chapter, context in contexts.items() if not context]
    if missing:
        raise RuntimeError(f"No source context extracted for chapters: {missing}")

    source = args.input.read_text(encoding="utf-8")
    enriched, counts = enrich_html(source, contexts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(enriched, encoding="utf-8")
    args.report.write_text(
        json.dumps(
            {
                "source_pdf": str(args.pdf),
                "source_html": str(args.input),
                "output_html": str(args.output),
                "chapters": contexts,
                **counts,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**counts, "chapters": len(contexts), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
