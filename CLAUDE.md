# Working rules for this repository

## What this is
Supplementary material for two SAFECOMP 2026 contributions by Milin Patel and
Rolf Jung (Kempten University of Applied Sciences): the WAISE 2026 paper on a
GSN argument pattern integrating ISO 26262, ISO 21448, ISO/SAE 21434 and
ISO/PAS 8800 for an AI-based LiDAR perception component, and the SAFECOMP 2026
position paper on two operational assurance gaps. It is also the target of the
QR code on the conference poster.

Audience: SAFECOMP reviewers, functional safety engineers, and researchers who
will reuse the pattern. Assume they know the standards and do not know Python.

## Non-negotiable
- Accuracy over polish. Never state an unverified thing as fact. Write
  "unverified" and what would settle it.
- Never invent a citation, clause number, file path, result, or DOI.
- Do not change a computed number, threshold, or seed while doing structural work.
- Do not remove content without stating the justification first.
- Never update a reference output to make a failing test pass.
- Do not claim the repository proves anything the papers only argue.

## Terminology (must not drift)
- concern: one of the three assurance dimensions (SOTIF, AI safety, cybersecurity)
- concern label: the tag identifying which concern owns an anomaly
- one judgment: a single verdict on whether the assurance argument still holds
- one top claim: the root claim the argument supports
- assignment gap: no clause assigns an unlabeled runtime anomaly to a concern
- resolution gap: no clause resolves per-concern re-evaluations into one judgment

Use the paper's wording, not a paraphrase of it. If a term appears in the papers,
grep the papers before inventing a phrasing for it here.

## Decisions
Decide rather than asking. State the criterion the decision was made on, and
name the alternative that was rejected and why. A decision with no stated
criterion is a subjective decision and is not acceptable here.

Where two options are genuinely equal on the stated criterion, pick the one a
reader can verify faster, and say so.

## Prose written into this repository
Every README, comment, docstring, and commit message.

- No em-dashes. Parentheses or a full stop.
- Banned: comprehensive, novel, robust, significant, seamless, leverage, delve,
  crucial, key, powerful, cutting-edge, streamline, unlock, dive into,
  it is worth noting, in today's landscape.
- No sentence that restates its heading. No "This section explains".
- No tricolon padding ("faster, cleaner, and more maintainable").
- Vary sentence length. Uniform rhythm reads as generated.
- No bullet list where two sentences work.
- Scope claims exactly: "none of the four standards examined", not "no standard".
- Abbreviate after first use, then stay consistent.
- A reader must be able to check every claim in the docs against a file in the
  repository. If they cannot, the claim does not belong in the docs.

## Visual and structural output
- One colour per standard (ISO 26262, ISO 21448, ISO/SAE 21434, ISO/PAS 8800),
  the same four across diagrams, the talk deck, and the poster. No fifth accent.
- Diagrams are generated from gsn/*.yaml at build time. The YAML is the single
  source of truth. Never hand-author node data into HTML or SVG.
- Anything a visitor may open from the poster QR code must be readable on a
  phone in portrait at 380px, in bright outdoor light. High contrast. No thin
  grey text on white.
- No decorative element that carries no information.

## Tools
- Prefer Serena symbol tools over reading whole files in src/ and tests/.
- Use subagents for independent review passes and for parallel exploration where
  the branches do not depend on each other. State what each subagent was asked.
- Use the repository's own tests and Makefile targets to verify. Verify by
  running, never by reasoning about what the code would do.

## Before declaring any phase done
Self-review as four readers and fix what each finds:
1. A domain expert checking whether the standards claims are correct.
2. A first-time visitor arriving by phone from the poster.
3. A reviewer checking whether the repository supports what the papers claim.
4. A reader hunting for generated prose. Rewrite what they flag; do not delete it.

## Process
- Read before proposing. Propose before editing.
- Small commits, plain messages, no generated-sounding commit prose.
- Report findings in files, not in chat. In chat, give at most ten lines naming
  the highest-severity items.
