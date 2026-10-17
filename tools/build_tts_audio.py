#!/usr/bin/env python3
"""Pre-render Italian TTS audio for all unique flashcard words.

Downloads MP3s from Google Translate TTS into audio/ (flat, hash-named),
and writes manifest.json mapping word -> filename. Re-runnable: skips
words that already have a valid file.
"""
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "italian"
AUDIO_DIR = BASE / "audio"
MANIFEST = BASE / "manifest.json"
HTML = BASE / "italian-flashcards-v1.0.html"
MIN_BYTES = 2000          # real TTS clips are >= ~7KB; anything smaller is an error page
MAX_RETRIES = 4
SLEEP_BETWEEN = 0.15      # gentle rate limiting


def extract_words():
    html = HTML.read_text(encoding="utf-8")
    m = re.search(r"const CARDS = \[(.*?)\n\];", html, re.S)
    if not m:
        raise SystemExit("CARDS array not found in HTML")
    its = re.findall(r'it:"([^"]+)"', m.group(1))
    return sorted(set(w.strip() for w in its if w.strip()))


def slug(word):
    h = hashlib.sha1(word.encode("utf-8")).hexdigest()[:12]
    safe = re.sub(r"[^a-z0-9]+", "-", word.lower()).strip("-")[:40]
    return f"{safe}-{h}.mp3"


def fetch(word, dest, retries=MAX_RETRIES):
    url = ("https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob"
           "&q=" + urllib.parse.quote(word) + "&tl=it")
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=15).read()
            if len(data) >= MIN_BYTES and data[:3] == b"ID3" or len(data) >= MIN_BYTES and data[:2] == b"\xff\xf3" or len(data) >= MIN_BYTES:
                dest.write_bytes(data)
                return True
            last_err = f"short response ({len(data)} bytes)"
        except Exception as e:
            last_err = str(e)[:80]
        time.sleep(1.0 * (attempt + 1))
    print(f"  FAIL {word!r}: {last_err}", flush=True)
    return False


def main():
    AUDIO_DIR.mkdir(exist_ok=True)
    words = extract_words()
    print(f"{len(words)} unique words")

    manifest = {}
    if MANIFEST.exists():
        try:
            manifest = json.loads(MANIFEST.read_text())
        except Exception:
            manifest = {}

    todo, done = [], 0
    for w in words:
        name = slug(w)
        path = AUDIO_DIR / name
        if w in manifest and path.exists() and path.stat().st_size >= MIN_BYTES:
            done += 1
        else:
            todo.append((w, name, path))

    print(f"{done} cached, {len(todo)} to download")
    failures = []
    for i, (w, name, path) in enumerate(todo, 1):
        ok = fetch(w, path)
        if ok:
            manifest[w] = name
        else:
            failures.append(w)
        if i % 50 == 0:
            print(f"  progress {i}/{len(todo)}", flush=True)
            MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=0))
        time.sleep(SLEEP_BETWEEN)

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=0))
    total = sum(p.stat().st_size for p in AUDIO_DIR.glob("*.mp3"))
    print(f"done. {len(manifest)} entries, {total/1e6:.1f} MB on disk, {len(failures)} failures")
    if failures:
        print("failed words:", failures)
        sys.exit(1)


if __name__ == "__main__":
    main()