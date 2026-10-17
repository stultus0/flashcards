import json
import re
import statistics
import unittest
from pathlib import Path


BASELINE = Path(__file__).resolve().parent.parent / "archive" / "ai-delivery" / "ims-flashcards-enriched-tts.html"
OUTPUT = Path("italian-flashcards-v1.0.html")
ACTIVE_CHAPTERS = (13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40)


def card_lines(text, chapter):
    return [line for line in text.splitlines() if f'set:"ch{chapter}"' in line]


def extras(lines):
    values = []
    for line in lines:
        match = re.search(r'extra:("(?:\\.|[^"\\])*")', line)
        if match:
            values.append(json.loads(match.group(1)))
    return values


class AllChaptersEnrichmentTests(unittest.TestCase):
    def test_output_preserves_deck_and_existing_early_chapters(self):
        baseline = BASELINE.read_text(encoding="utf-8")
        output = OUTPUT.read_text(encoding="utf-8")
        self.assertEqual(sum(len(card_lines(output, chapter)) for chapter in (0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40)), 1503)
        for chapter in (0, 1, 2, 3, 4, 5, 7, 8, 9, 10):
            self.assertEqual(card_lines(output, chapter), card_lines(baseline, chapter))

    def test_notes_are_concise_and_have_expected_coverage(self):
        output = OUTPUT.read_text(encoding="utf-8")
        all_lines = [line for line in output.splitlines() if 'set:"ch' in line]
        notes = extras(all_lines)
        self.assertEqual(len(notes), 730)
        self.assertLessEqual(max(map(len, notes)), 84)
        self.assertLessEqual(statistics.median(map(len, notes)), 43)
        self.assertFalse(any(note.startswith("Lesson context:") for note in notes))
        self.assertEqual(len(extras(card_lines(output, 11))), 23)
        for chapter in ACTIVE_CHAPTERS:
            cards = card_lines(output, chapter)
            coverage = len(extras(cards)) / len(cards)
            self.assertGreaterEqual(coverage, .45, f"ch{chapter}: {coverage:.1%}")
            self.assertLessEqual(coverage, .65, f"ch{chapter}: {coverage:.1%}")


if __name__ == "__main__":
    unittest.main()
