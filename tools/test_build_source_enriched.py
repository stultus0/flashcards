import unittest

from build_source_enriched import chapter_context, merge_extra


class ChapterContextTests(unittest.TestCase):
    def test_extracts_introduction_and_grammar_topics(self):
        pages = [
            "I NUMERI\nPRESENTAZIONE — INTRODUCTION Numbers are used every day. "
            "VOCABOLARIO NUOVO — NEW VOCABULARY nomi — nouns",
            "APPUNTI DI GRAMMATICA — GRAMMAR NOTES\n"
            "1. PRESENT TENSE OF POTERE, TO BE ABLE TO\n"
            "2. NUMBERS FROM 1 UP TO 1,000",
        ]
        context = chapter_context(pages)
        self.assertEqual(
            context,
            "Lesson context: Numbers are used every day. Grammar: Present tense of potere, to be able to; Numbers from 1 up to 1,000.",
        )

    def test_stops_grammar_at_exercises_and_ignores_blank_prompts(self):
        pages = [
            "PRESENTAZIONE — INTRODUCTION A long lesson introduction. "
            "VOCABOLARIO NUOVO — NEW VOCABULARY",
            "APPUNTI DI GRAMMATICA — GRAMMAR NOTES\n"
            "1. PRESENT TENSE OF FARE, TO DO, TO MAKE\n"
            "ESERCIZI — EXERCISES\n"
            "2. Noi ______________________ ogni giorno.",
        ]
        self.assertEqual(
            chapter_context(pages),
            "Lesson context: A long lesson introduction. Grammar: Present tense of fare, to do, to make.",
        )

    def test_keeps_existing_note_and_adds_context_once(self):
        self.assertEqual(
            merge_extra("Existing note.", "Lesson context: Useful lesson."),
            "Existing note. Lesson context: Useful lesson.",
        )
        self.assertEqual(
            merge_extra("", "Lesson context: Useful lesson."),
            "Lesson context: Useful lesson.",
        )


if __name__ == "__main__":
    unittest.main()
