# Flashcards — phone setup

Two decks are available as single-file web apps:

| Deck | File | Cards | Audio |
|---|---|---|---|
| Italian (Italiano Semplice / *Italian Made Simple*, Introduction + Chapters 1–40) | `italian/index.html` (~170 KB) | 1,503 | pre-rendered MP3s in `italian/audio/`, listed in `italian/manifest.json`; falls back to live TTS when a word has no file |
| French (*Invitation au Français*, lessons 1–28) | `french/index.html` (~90 KB) | 638 | pre-rendered MP3s in `french/audio/`, listed in `french/manifest.json`; falls back to live TTS when a word has no file |

Each deck keeps its own progress, so you can study both on the same phone without them interfering.

## Send the files

Email **both** of these folders to yourself as attachments (zip them if your mail app won't attach many files):

- `italian/index.html`, `italian/manifest.json`, and everything in `italian/audio/`
- `french/index.html`, `french/manifest.json`, and everything in `french/audio/`

Keep the folder structure intact — the page looks for `manifest.json` and `audio/…mp3` files relative to itself. If you'd rather send only one deck at a time, send just that deck's folder; the steps below work per deck.

If you're short on space, you can still send just `index.html`: cards and progress work fully offline, but 🔊 pronunciation will stream from Google Translate over the Internet instead of using the bundled audio.

## iPhone / iPad

1. Open an email attachment.
2. Tap **Share** → **Save to Files**.
3. Choose **On My iPhone/iPad**, create a folder named after the deck (e.g. **Flashcards/italian**), keep the subfolders (`audio/`) as they are, and tap **Save**. Repeat for the second deck.
4. Open the **Files** app, go to the deck's folder, and tap `index.html`.
5. Confirm that a card appears; tap it to reveal the answer, then choose a grade.

Launch each deck from **Files** whenever you study. iOS does not provide a dependable Home Screen web-app shortcut for a local HTML attachment. If the file opens as text or a static preview rather than interactive cards, the iPhone is blocking local HTML execution; use a hosted web link instead.

## Android

1. Open an email attachment and tap **Download**.
2. Open **Files by Google** (or your phone's Files app) → **Downloads**.
3. Put each deck in its own subfolder (`Downloads/flashcards-italian`, `Downloads/flashcards-french`) with the `audio/` subfolder inside it, preserving the layout.
4. Tap the deck's `index.html` and choose **Chrome** if Android asks which app to use.
5. Confirm that a card appears; tap it to reveal the answer, then choose a grade.

Open the saved file from its folder whenever you study. If Chrome shows source text, refuses to open the file, or does not retain progress, the phone/browser is blocking local HTML; use a hosted web link instead.

## Important

- Progress is saved separately per deck and per phone/browser (each deck uses its own storage key). It does not sync across devices.
- The 🔊 pronunciation button plays the bundled MP3s offline; only words missing a local file need Internet access (live TTS fallback).
- Do not use **Reset progress** unless you intend to erase that deck's schedule on that phone/browser.

## Optional desktop shortcut

For a web-hosted copy of either deck: in **Chrome**, open the URL → **three-dot menu** → **Cast, save, and share** → **Create shortcut**. On a Mac in **Safari**, open the URL → **File** → **Add to Dock**.