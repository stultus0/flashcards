# Handoff — French Flashcard Example-Enrichment (Lessons 7–28)

**Created:** 2026-10-17 · **Session:** `20261017_095932_954bca`
**Status:** L19–23 DONE & pushed. L7–10, L11–14, L15–18, L24–28 still need example sentences mined from the textbook. Do NOT re-dispatch those four yet — awaiting user go-ahead.

**Update 2026-10-17 (second review):** `/ai` git repo removed (deck lives only at `french/index.html` in this repo). All 17 remaining lesson windows re-verified against the PDF dump — **12 of 17 were wrong or badly shifted**. Corrected windows saved to `/opt/data/cache/scratch/enrich_windows_v2.json`. See §9 for corrected table and recommended execution plan.

**Update 2026-10-17 (batch A merged):** L7–L10 done — 144 example sentences mined from pp. 196–271 and merged into `french/index.html`. Deck now at 368/780 cards with examples. Commit `f42eda1`. Merge script now targets `french/index.html` directly (no more `/ai` copy needed). Remaining: L11–L14, L15–L18, L24–L28 = 270 cards.

---

## 1. What this task is

The deck `/ai/french-flashcards-v1.0.html` (synced to GitHub `stultus0/flashcards` → `french/index.html`) has **780 cards / 742 unique French words** for Lessons 1–28 of *Invitation au français* (Holt McDougal TE). Originally only L1–L6 had `example` sentences; L7–28 were bare word→translation pairs (589 cards). The goal is to add a short, natural **French example sentence** (in `example`) + **English gloss** (in `extra`) for every card in L7–28, grounded in the actual book dialogues/exercises.

Field mapping (already decided, do not change):
- `example` = French sentence only (≤ ~25 words, uses the card's `fr` term or an inflection of it).
- `extra` = English gloss (≤ ~20 words). Renders as muted text on the card back (`backExtra`).
- No new `en_example` key.

## 2. Progress so far

| Group | Lessons | Cards | Status |
|-------|---------|-------|--------|
| L19–23 | 19,20,21,22,23 | 56 | ✅ DONE — merged, verified, committed `/ai` `d064131`, pushed GitHub `487f510` |
| L7–10 | 7,8,9,10 | ~150 | ❌ stuck, no output |
| L11–14 | 11,12,13,14 | ~160 | ❌ stuck, no output |
| L15–18 | 15,16,17,18 | ~150 | ❌ stuck, no output |
| L24–28 | 24,25,26,27,28 | ~130 | ❌ stuck, no output |

L19–23 verification (runtime VM check): total 780 cards, 0 bad; L19 11/11, L20 13/13, L21 11/11, L22 10/10, L23 11/11 examples.

## 3. Key files

- **Deck (dev):** `/ai/french-flashcards-v1.0.html`
- **Deck (repo):** `/opt/data/projects/italian-lessons/french/index.html`
- **Audio:** `/opt/data/projects/italian-lessons/french/audio/` (742 MP3s) + `french/manifest.json`
- **TTS generator:** `/opt/data/projects/italian-lessons/tools/build_french_tts_audio.py` (regex already fixed to match both quoted `"fr":"..."` and unquoted `fr:"..."` key styles)
- **Source text:** `/opt/data/cache/scratch/pdf_dump_full.txt` — OCR dump, 57,548 lines, 648 pages. Page markers `===PAGE NNN===` at line start. **Book page ≈ PDF page − 110** (offset +110).
- **Done enrichment:** `/opt/data/cache/scratch/enrich_l19_23.json`
- **Per-lesson page windows:** `/opt/data/cache/scratch/enrich_windows.json`
- **Merge script:** `/opt/data/cache/scratch/merge_examples.py` (line-based; matches cards by exact `(set, fr)`; injects `example`+`extra`; backs up first)
- **Pre-merge backup:** `/opt/data/cache/scratch/french_backup_premerge.html`
- **Subagent transcripts:** `/opt/data/cache/delegation/live/deleg_be8611fd/task-{0..4}.log`

## 4. How to mine + merge (the proven workflow)

### A. Mine one group into a JSON file
For each lesson in the group, read its source window from the PDF dump and pull real example sentences from the dialogues/exercises. Output shape (match `enrich_l19_23.json` exactly):
```json
{
  "l19": {
    "attendre":   {"example": "Pierre attend Michèle au café.", "en_example": "Pierre is waiting for Michèle at the café."},
    "...":        {"example": "...", "en_example": "..."}
  }
}
```
Keys MUST equal the deck's exact `fr` strings (case/accent-sensitive), grouped under `lN`. Every card `fr` in the assigned lessons should have an entry.

**Page anchors (book→PDF offset +110):** L11→272, L14→306, L16→335, L18→404, L23→461, L26→520, L27→519, L28→521. Lesson titles: L11 "Le copain de Mireille", L14 "Week-end à Paris", L27 "Un client difficile", L28 "Pique-nique". Verify each window against the dump before trusting it (see §5 — the windows were partly wrong).

**Mining protocol that worked (from the one successful agent, sa-3):**
1. Read the whole per-lesson window in ONE `sed -n '/===PAGE X===/,/===PAGE Y===/p'` call (or `awk` range). Do NOT crawl page-by-page.
2. Cap total tool calls (~15–20). No global single-word greps across all 57k lines.
3. If a window doesn't contain the lesson's dialogues, do ONE bounded grep for the lesson title to relocate it, then stop searching.
4. Write the JSON immediately once you have the sentences — don't keep re-reading.

### B. Merge into the deck
1. Back up: `cp /ai/french-flashcards-v1.0.html /opt/data/cache/scratch/french_backup_premerge.html`
2. Point `merge_examples.py` at the new JSON (edit the `enr=` line) and run it. It reports `lines changed` / `matched keys found in file` — must equal the expected count.
3. Verify JS syntax: extract `<script>` blocks → `node --check`.
4. Runtime check (VM stub) — assert total 780, 0 bad, and per-lesson example counts.
5. Sync + commit + push:
   ```
   cp /ai/french-flashcards-v1.0.html /opt/data/projects/italian-lessons/french/index.html
   cd /opt/data/projects/italian-lessons && git add french/index.html && git commit -m "..." && git push origin main
   cd /ai && git add french-flashcards-v1.0.html && git commit -m "..."
   ```

**Merge-script gotchas (already fixed in current `merge_examples.py`, but know them):**
- The strip regexes for removing pre-existing `example:`/`extra:` fields must be `(?:[^"\\]|\\.*?)*` (lazy escape). Using `\\.)*` consumes the closing quote and leaves a dangling `"` → `type:"noun""` syntax error.
- After stripping, normalize the object tail: rstrip, drop trailing comma, fix a stray `,"` before the closer, then insert `, example:"…", extra:"…"` right before the preserved closer (`},` or `}`).
- Match on exact `(set, fr)`; skip if the key already seen (dedupe).

## 5. Why the 4 subagents got stuck (root-cause analysis)

All 5 agents were dispatched together (delegation `deleg_be8611fd`, 2026-10-17 12:14) with the SAME task template. Only **sa-3 (L19–23)** finished cleanly in ~14 min / 14 tool calls. The other 4 ran ~101 min and were killed at the user's "stop all subagents" command, having written **no output JSON**. Distinct failure modes per transcript:

- **task-0 (L7–10):** Wrong starting page window (started scanning the p240s/p250s region instead of L7's true location). Kept relocating with `grep '===PAGE 1[0-3][0-9]==='` and re-reading overlapping ranges. By 13:31 it entered a **tight loop: the identical command `grep -n '===PAGE 12[0-9]===' … + 3 commands` repeated 15× straight through to 13:54** — same query, same result, zero progress, until killed.
- **task-1 (L11–14):** Over-extracted huge dumps (multi-thousand-line `sed` ranges), then **re-read the same temp files over and over** (`l11.txt`, `l13c/d/e/f.txt`, `l14e.txt` each read 2–3×) and re-ran the same node card-listing command repeatedly. Busy, but not converging on sentences.
- **task-2 (L15–18):** Got the window badly wrong and **crawled one page at a time** via `for p in <single page>` loops, marching from ~p329 all the way to **p526** (which is Unit 8 pacing material / L27's region — far past its assignment). One page per tool call × ~100 calls = slow grind with no end in sight.
- **task-4 (L24–28):** Locked onto a single rare word and **grepped `assister` globally across all 57k lines ~12×** with shifting `sed -n` slices (`1,30p`, `20,45p`, `1,60p`…), never finding a usable sentence, looping until killed.

### Common root causes
1. **Rough/wrong page windows.** The offset (+110) and anchors were approximate; several groups' true dialogue pages weren't where the window pointed, so agents spent their budget hunting instead of mining.
2. **No hard tool-call/time budget.** Nothing stopped an agent from making 80–110 calls; the search spirals (re-grep, re-read, page-crawl) were self-sustaining.
3. **Global single-word greps over the full 57k-line dump** (task-4's `assister`, task-0's repeated page-marker greps) — expensive, noisy, and a trap for rare/OCR-mangled words.
4. **Re-doing work already done** (re-reading the same extracted files, re-running the same card list) instead of moving forward.

### Why they didn't recognize they were stuck
- **No self-checkpoint / stopping rule.** Nothing told them "after N calls with no new sentence written, stop and report what you have." So partial progress felt like forward motion.
- **Local success masked global stall.** Each individual grep/sed/read returned plausible-looking content, so the model kept concluding "almost there" even though the aggregate wasn't converging.
- **The spiral was self-reinforcing and looked productive.** Repeated near-identical commands each produced fresh (but redundant) output, which read as activity rather than a loop — the model had no external signal that it was repeating itself.
- **No deadline pressure inside the child.** Subagents have no internal timer; absent an explicit "cap ~20 calls, then emit best-effort JSON," they optimize for completeness and drift.
- **Best-effort output wasn't required.** The task implied "produce complete correct JSON," so agents kept searching for the perfect sentence instead of writing down good-enough ones and finishing.

## 6. Proposed solutions (for the re-run — NOT yet applied)

1. **Verify/correct the page windows first** (parent does this, cheaply): for each of the 4 remaining groups, grep the lesson TITLE in the dump, confirm the true dialogue page range, and bake the corrected window into the prompt. This kills root cause #1.
2. **Hard budget in the prompt:** "Read each lesson's window in ONE sed/awk range call. Max ~15–20 tool calls total. Then write the JSON with what you have." Kills #2.
3. **Ban global greps:** "Never grep a single word across the whole dump. Grep only within your confirmed page window (use `sed -n 'start,endp' file | grep …`)." Kills #3.
4. **Require incremental/best-effort writes:** "Write the JSON file as soon as you have ≥1 sentence per lesson; refine only if budget remains. A partial valid file beats no file." Kills the "completeness trap."
5. **Self-stall checkpoint:** "If two consecutive tool calls return essentially the same information, stop searching and emit your best JSON." Directly addresses why they didn't notice the loop.
6. **Smaller batches:** dispatch 1–2 lessons per agent (not 4–5) so a wrong window wastes less budget and the agent can't wander as far (task-2 crawled 200 pages because its batch was big).
7. **Parent-side watchdog:** poll the live transcripts (as we did) and `steer`/`stop` any agent that exceeds ~25 calls or repeats a command, instead of letting all 5 run to a common kill-time.
8. **(Optional) Do it inline in-session** for the remaining 4 groups rather than delegating — given the workflow is now well-understood and verified, a single sequential pass with the corrected windows may be faster and lower-risk than another fan-out.

## 7. Immediate next steps (when user says go)
1. ~~Confirm go-ahead~~ — windows already corrected (see §9).
2. ~~Correct the page windows~~ — done; see `enrich_windows_v2.json`.
3. Execute inline sequential pass (recommended — see §9.2).
4. Mine → merge (per §4) → verify → commit → push for each completed group.
5. Update this table (§2) and the deck's example coverage as each group lands.

## 8. Open items / notes
- TTS audio is complete for all 742 words (7.1 MB); adding `example`/`extra` text does **not** require regenerating audio (audio is keyed to `fr`, not `example`).
- Both repos currently clean and in sync at the post-L19–23 state.
- The recurring status-ping cronjob (`french-enrich-status-ping`, id `84a1402fd514`) was already removed.
- If re-dispatching, the old transcripts remain at the path in §3 for comparison.
- **`/ai` git repo removed** (2026-10-17): deck now lives only at `french/index.html` in this repo. Merge script still targets `/ai/french-flashcards-v1.0.html` — either restore that file as a copy or point the script at `french/index.html` directly before first merge.

## 9. Corrected page windows (verified 2026-10-17, second pass)

Source: `pdf_dump_full.txt` (648 pages). Each window below was verified by locating the `Lecon NN` title header and confirming content start/end against the next lesson's start. The TE (Teacher Edition) dump interleaves pacing guides, audio scripts, and classroom-management pages with actual lesson content — the windows point at the **lesson content** (dialogues, vocab exercises, "A votre tour" activities), which is where usable example sentences live.

| Lesson | Title (actual) | PDF pages | Old window | Error |
|--------|---------------|-----------|------------|-------|
| L7 | Une boum (activities/parties) | 196–207 | 226–237 | Was Entracte 3 reading material; also wrong title ("Le sport") |
| L8 | Finding out information | 208–217 | 173–184 | Was L5 content + TE audio scripts |
| L9 | Les personnes et les objets | 246–259 | 242–253 | Started too early (TE scripts/pacing on p242–245) |
| L10 | Vive la différence! | 260–271 | 244–255 | Overlapped L9 entirely |
| L11 | Le copain de Mireille | 272–281 | 272–283 | Close; trimmed end (L12 starts p282) |
| L12 | La voiture de Roger | 282–291 | 243–254 | Was in L9/L10 region |
| L13 | Mon quartier / Getting around | 338–347 | 282–293 | Was in L12 region |
| L14 | Week-end à Paris | 348–359 | 306–317 | Was Reprise/diagnostic material |
| L15 | Au café de l'Univers | 360–369 | 314–325 | Was middle-school review |
| L16 | Mes voisins | 370–379 | 335–346 | Was in L13 territory |
| L17 | L'achat des vêtements | 406–415 | 343–354 | Was L13/L14 |
| L18 | Rien n'est parfait! | 416–425 | 404–415 | Overlapped L17 |
| L24 | Qui a de la chance? | 496–505 | 461–472 | Was L23! |
| L25 | Les repas et la nourriture | 524–535 | 490–501 | Was L23/L24; TE pages p519–523 precede |
| L26 | À la cantine | 536–547 | 520–531 | Overlapped L25/TE pages |
| L27 | Un client difficile | 548–557 | 519–530 | Included TE pages; actual content p548+ |
| L28 | Pique-nique | 558–569 | 521–532 | Overlapped L27 |

Machine-readable: `/opt/data/cache/scratch/enrich_windows_v2.json`

### 9.1 Why the old windows were so wrong
The original offset heuristic ("book page ≈ PDF page − 110") assumed a uniform offset. In reality the TE dump has variable-width front matter, unit openers, Reprise/diagnostic sections, and pacing-guide blocks that shift each lesson by a different amount. L12 was off by ~39 pages; L24 by ~35. The subagents inherited these windows verbatim and spent their entire budget hunting for content that wasn't there.

### 9.2 Recommended execution plan (updated)
Given the workflow is proven, the windows are now verified, and the `/ai` repo is gone (simpler — one repo to update), the recommended approach is:

**Inline sequential pass by the parent session** (not fan-out delegation):
- 17 lessons × ~10–14 pages each = ~200 pages of source to read
- Batch 3–4 lessons per mining call (one `sed -n '/===PAGE X===/,/===PAGE Y===/p'` range per batch)
- Write one JSON file per group (matching original grouping: L7–10, L11–14, L15–18, L24–28)
- Merge → node --check → runtime VM check → commit → push per group
- Estimated: 12–18 total tool calls, ~30–45 min wall time

The §6 guardrails (hard budget, no global greps, best-effort writes) are still good practice if delegating, but for an inline pass they're less critical since the parent controls the loop directly.