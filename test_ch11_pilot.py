import json
import re
import statistics
import unittest
from pathlib import Path


OUTPUT = Path("ims-flashcards-enriched-tts-ch11-pilot.html")


class Chapter11PilotTests(unittest.TestCase):
    def test_chapter_11_notes_match_existing_note_style(self):
        text = OUTPUT.read_text(encoding="utf-8")
        chapter_11 = [line for line in text.splitlines() if 'set:"ch11"' in line]
        notes = []
        for line in chapter_11:
            match = re.search(r'extra:("(?:\\.|[^"\\])*")', line)
            if match:
                notes.append(json.loads(match.group(1)))

        self.assertEqual(len(chapter_11), 37)
        self.assertEqual(len(notes), 23)
        self.assertLessEqual(max(map(len, notes)), 84)
        self.assertLessEqual(statistics.median(map(len, notes)), 40)
        self.assertFalse(any(note.startswith("Lesson context:") for note in notes))

    def test_chapter_11_contains_high_value_source_grounded_notes(self):
        text = OUTPUT.read_text(encoding="utf-8")
        for expected in (
            "Categoria di parole = word class",
            "Fare progressi = to make progress",
            "Numero di telefono = phone number",
            "A giovedì prossimo = see you next Thursday",
            "Fare tutto il possibile = do everything possible",
        ):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
