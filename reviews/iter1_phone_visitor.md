# Review: phone visitor from the poster QR code (iteration 1)

Persona: scanned the QR code in a conference corridor, on a phone, in daylight,
about two minutes of attention. Has not read either paper. Judging README.md as
it now stands, plus the first screens of `docs/figures/README.md` and
`data/carla_configs/README.md`.

Overall verdict: **the honest, careful voice of this README builds trust, but the
first phone screen is spent on the title twice and on paper bookkeeping, and the
one thing a poster visitor wants — what did you find, in one plain sentence, with
a picture — is either below the fold or absent entirely. I would probably scroll
once, hit a directory tree, and close the tab.**

---

## 1. The first screenful (HIGH severity)

What I actually see on the first phone screen, in order:

1. `# Integrating Cybersecurity into the AI Safety Assurance Argument: A GSN Pattern for AI-Based Perception Components in Highly Automated Driving` — a 21-word title that wraps to 3–4 lines on a phone.
2. "Supplementary material for:"
3. The **exact same 21-word title again**, verbatim, as a blockquote.
4. "Milin Patel and Rolf Jung (Kempten University of Applied Sciences)"
5. The start of the "Two papers" block.

That is the whole first screen. The title is rendered twice back-to-back and
consumes roughly half the visible area. Nothing on this screen tells me what the
work claims. The actual claim sentence —

> "The integrated pattern extends ISO/PAS 8800 Annex B from 6 to 9 goals,
> identifies 7 decision points where the standards defer to application context,
> and classifies 5 assurance gaps — 2 of which are only visible through
> constructive integration."

— is line 28, in `## Overview`, at least two swipes down, behind the Colab badge
and a horizontal rule. That sentence is the best thing in the README and it is
hidden.

Fix that would satisfy me: delete the duplicated blockquote title (the H1
already says it), and put a one-or-two-sentence claim summary directly under the
authors, before the "Two papers" block.

## 2. The "Two papers" block (MEDIUM severity)

It is bookkeeping before orientation. Before I know what the work *is*, I am
told:

- which LaTeX class each paper uses ("(LLNCS)", "(IEEEtran)") — I do not care,
  and on a phone these read as noise tokens;
- which paper the code backs ("The code in `src/` backs this paper: the 9-goal
  integrated pattern, the seven decision points, the five findings.") — three
  counted things I have no referent for yet;
- "It is argued at clause level. No file in `src/` supports it, and none is
  meant to." — out of context, "no file supports it" reads for a second like a
  confession that the paper is unsupported. I understand on re-read that it
  means "the position paper needs no code", but a corridor reader does not
  re-read.

Also a terminology slip: the block says "the five findings", the Overview says
"5 assurance gaps". Same objects, two names, ten lines apart. A newcomer cannot
know they are the same.

The block is genuinely useful — two papers in one repo is exactly the kind of
thing a visitor needs disambiguated — but it should come *after* one sentence
saying what the work is, and could drop the format tags entirely.

## 3. Jargon before explanation (HIGH severity)

Terms a newcomer meets before (or without) any explanation:

- **GSN** — in the title, never expanded anywhere in the README. "Goal
  Structuring Notation" appears nowhere. This is the single most important
  expansion missing; the whole repo is named after it.
- **decision points** — line 13 ("the seven decision points"), before the
  Overview's partial gloss "decision points where the standards defer to
  application context". The intro use is bare.
- **constructive integration** — used in the Overview claim sentence as if
  known; never defined in reader terms.
- **G5 and G6** — "These are the kinds of evidence G5 and G6 call for" in the
  three-layer section. I have not seen the goal list; G5 means nothing.
- **SOTIF** — repo tree comment "CARLA evaluation under SOTIF triggering
  conditions", unexpanded.
- **ISO 26262 / 21448 / 21434 / PAS 8800** stacked in one sentence — a
  standards person parses this instantly; a poster visitor from an adjacent
  field gets alphabet soup with no gloss like "(functional safety, SOTIF,
  cybersecurity, AI safety)".

To the README's credit, **ASIL, TARA, DP-1, F-3, I-2 do not appear** — those
internal IDs stayed out, which is right.

Is there a one-sentence plain statement of the finding? Almost. The Overview
sentence quoted above is close, but it is a methods sentence, not a findings
sentence. The plain version a corridor visitor wants — something like "when you
merge the four standards' safety and security arguments into one, two assurance
gaps appear that no single standard makes visible" — exists nowhere in plain
words, and it is the poster's whole point.

## 4. The 193-vs-192 note and the Windows gsn2x note (LOW severity — mostly fine)

Both read as **honesty, and both are in the right place** (Tests section and GSN
Diagrams section, well below the fold, where only someone about to run things
will meet them). "The WAISE paper reports 193 tests. That count was correct when
the paper was written… no test was added here to make it agree" is the kind of
sentence that makes me trust the rest of the repo. Same for "On Windows or macOS
it will download a binary that cannot run" — blunt, slightly funny, useful.

Minor tightening only: the 193/192 note is four sentences where two would do,
and "a binary that cannot run" would be clearer as "a Linux binary that will not
run on Windows/macOS". Neither would make me close the tab. Do not move these
higher up; they are correctly buried.

## 5. Navigation from the README (MEDIUM severity)

- **Papers**: I can infer `paper/waise2026/` and `paper/safecomp2026-position/`,
  but they are backticked paths, not links — on GitHub mobile they are not
  tappable. And they are *sources* (.tex); there is no link to a PDF or to the
  published version, so a visitor who wants to read the paper (the most likely
  QR-code intent) has no path to it at all.
- **Diagrams**: the 9-goal GSN pattern — the poster's centrepiece — is not shown
  in the README and not linked. `docs/figures/` is mentioned only inside the
  ASCII tree. There is a committed `integrated_gsn.png` sitting in
  `docs/figures/` whose README explicitly says it exists "so that a reader can
  see the outputs without installing anything" — and the top-level README never
  embeds or links it. That is the single cheapest, highest-value fix available:
  one `![...](docs/figures/integrated_gsn.png)` under the Overview.
- **Numbers**: `data/empirical_results/README.md` and
  `data/synthetic_illustrations/README.md` are named as backticked paths, again
  not links.
- The **Colab badge is the one tappable thing** on the page and it is good —
  but it sits orphaned between the paper block and a horizontal rule, with no
  caption saying what I would get by tapping it.

## 6. What would make me close the tab

In order of danger:

1. Seeing the same long title twice and no claim on screen one (I assume the
   page is boilerplate and leave).
2. Swiping down into a 25-line ASCII directory tree as the first large block
   after the Overview — on a phone this is a wall.
3. Zero images. A repo about a *graphical* notation, reached from a *poster*,
   shows me no graphic.
4. "No file in `src/` supports it" on first read.

## The two secondary READMEs (positive)

Both are better than the top-level README at the thing the top-level README
struggles with: leading with provenance in plain declarative sentences.

- `docs/figures/README.md` opens "Provenance: seeded-synthetic and derived.
  Nothing here is a measurement." — exemplary. First screen fully orients.
- `data/carla_configs/README.md` opens "Provenance: hand-written. These two
  files record parameters. They are not measurements, they are not generated,
  and no code reads them." — equally exemplary, and the "Documented here / Used
  by" table is exactly right.

A first-time visitor will never reach either file, but if they do, these pages
raise trust rather than spend it.

## Severity-ranked fix list

| # | Severity | Fix |
|---|---|---|
| 1 | HIGH | Remove the duplicated blockquote title; put a 1–2 sentence plain-language claim (what was found, not just what was done) directly under the authors, above the "Two papers" block. |
| 2 | HIGH | Embed or link `docs/figures/integrated_gsn.png` near the Overview so a phone visitor sees the 9-goal pattern without installing anything. |
| 3 | HIGH | Expand GSN once ("Goal Structuring Notation") on first use; add a parenthetical gloss for the four standards; gloss or defer SOTIF and G5/G6. |
| 4 | MEDIUM | In the "Two papers" block: drop "(LLNCS)"/"(IEEEtran)", reword "No file in `src/` supports it" to something like "it is a conceptual argument and intentionally has no code behind it", and use one name consistently ("five gaps", not "five findings"). |
| 5 | MEDIUM | Make paper/data/figure paths actual markdown links; add a link to the published/preprint PDF of each paper if one exists. |
| 6 | LOW | Tighten the 193/192 note to two sentences and say "Linux binary" in the gsn2x warning. Keep both where they are. |
