#!/usr/bin/env python3
"""Fridge Roast: One Line, Biggest Laugh.

A smart fridge's one-line roast, written by a small deterministic
generator. The program holds a set of hand-written candidate roasts,
scores each one against the judge's published criteria, and writes the
best-scoring line to /output/entry.txt.

Scoring follows the brief, most important first:
  1. It must roast a smart fridge: the fridge itself, its app, its
     firmware, its ice maker, its screen.
  2. The punchline must land: the line builds to a turn or a surprise
     that gets a laugh on the first read.
  3. The joke must be specific to smart fridges, not a generic gag
     that would work on any gadget.
  4. The wording must be tight: every word earns its place inside
     the 200-character limit.
  5. The angle must be fresh: no ordering-groceries crack, no
     watching-you crack, nothing the obvious writers reach for first.

Fully deterministic: no randomness, no clock, no network, no environment
input. Two runs always write the same file.
"""

import argparse
import sys

# Hand-written candidate roasts. Each is one line, plain text, well under
# the 200-character cap, aimed at the fridge itself.
CANDIDATES = [
    # A firmware update whose big new feature is ads for food it let spoil.
    "Your fridge spent forty minutes updating its firmware, and the big "
    "new feature is a screen that shows ads for the yogurt it already "
    "let expire.",
    # An ice maker that sounds broken and a fridge that needs IT support.
    "Your ice maker has one job and sounds like a blender full of gravel "
    "doing it \u2014 three grand for a fridge that needs IT support to "
    "stay cold.",
    # An app that pushes a notification for what the glass door shows.
    "Your fridge's app sent a push notification that you're out of eggs, "
    "like a $3,000 appliance with a camera needed to tell you what the "
    "glass door already shows.",
    # A fridge full of brains whose only real achievement was an accident.
    "Your fridge has a touchscreen, Wi-Fi, and a voice assistant, yet the "
    "smartest thing it did all year was keep the beer cold \u2014 and "
    "that was an accident.",
    # A frozen touchscreen turns groceries into something you reboot.
    "Your fridge froze \u2014 not the food, the touchscreen \u2014 so now "
    "you reboot your groceries like a router while the ice maker holds "
    "dinner hostage for a firmware patch.",
    # A fridge that knows everything and still cannot just be cold.
    "Your smart fridge knows the milk expired, the ice maker is jammed, "
    "and your diet is a joke \u2014 yet it still can't figure out how "
    "to just be cold.",
    # Moon-landing computing power spent nagging about uneaten kale.
    "Your fridge has more computing power than the rocket that went to "
    "the moon, and it spends it reminding you about the kale you bought "
    "and never ate.",
]

# The obvious angles the brief asks entries to avoid.
STALE_ANGLES = (
    "watching you",
    "watches you",
    "spies on you",
    "ordering groceries",
    "orders your groceries",
    "order your groceries",
)

# Fridge-specific nouns: the joke must be about the fridge, not any gadget.
FRIDGE_TERMS = (
    "fridge",
    "firmware",
    "ice maker",
    "app",
    "touchscreen",
    "yogurt",
    "milk",
    "groceries",
    "freezer",
)

# Words that mark the punchline's turn: the smart feature failing at
# the fridge's one real job, or turning against its owner.
TWIST_WORDS = (
    "ads",
    "accident",
    "hostage",
    "IT support",
    "never ate",
    "just be cold",
    "already shows",
)

# Concrete details that make the joke specific instead of generic.
CONCRETE_WORDS = (
    "forty",
    "three grand",
    "$3,000",
    "yogurt",
    "eggs",
    "beer",
    "kale",
    "milk",
    "blender",
    "gravel",
    "router",
)

MAX_CHARS = 200


def score(line: str) -> float:
    """Score one candidate against the judge's published criteria."""
    points = 0.0
    lower = line.lower()

    # 1. A roast of a smart fridge: fridge-specific nouns carry it.
    for term in FRIDGE_TERMS:
        if term in lower:
            points += 1.0

    # 2. The punchline lands: the final clause carries the turn, and a
    #    twist word anywhere in the line is the laugh.
    last_clause = line.rsplit("\u2014", 1)[-1].rsplit(", and ", 1)[-1]
    if any(word in last_clause.lower() for word in TWIST_WORDS):
        points += 2.0
    for word in TWIST_WORDS:
        if word in lower:
            points += 1.0
            break

    # 3. Specific to smart fridges: concrete details, not vague complaint.
    for word in CONCRETE_WORDS:
        if word in lower:
            points += 0.5
    if any(ch.isdigit() for ch in line) or "forty" in lower:
        points += 1.0

    # 4. Tight wording: the sweet spot is 120-170 characters, every word
    #    earning its place; a line that sprawls toward the cap loses.
    if 120 <= len(line) <= 170:
        points += 1.0
    elif len(line) > 185:
        points -= 1.0

    # 5. A fresh angle: the obvious ordering-groceries / watching-you
    #    cracks lose hard, and so does the worn-out moon-landing
    #    comparison every gadget joke reaches for.
    for stale in STALE_ANGLES:
        if stale in lower:
            points -= 5.0
    if "moon" in lower:
        points -= 2.0

    # The gate: one line, 1-200 characters, not only whitespace.
    if not line or len(line) > MAX_CHARS or "\n" in line or not line.strip():
        points -= 100.0

    return points


def pick_best() -> str:
    """Return the highest-scoring candidate; earliest wins a tie."""
    best_line = None
    best_score = None
    for line in CANDIDATES:
        s = score(line)
        if best_score is None or s > best_score:
            best_line, best_score = line, s
    return best_line


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default="/output/entry.txt",
        help="where to write the entry (default: /output/entry.txt)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="print every candidate with its score and exit",
    )
    args = parser.parse_args(argv)

    if args.list:
        for line in CANDIDATES:
            print(f"{score(line):6.1f}  ({len(line)} chars)  {line}")
        return 0

    line = pick_best()
    if len(line) > MAX_CHARS or "\n" in line or not line.strip():
        print("error: winning line fails the gate", file=sys.stderr)
        return 1

    # Write exactly the line, no trailing newline: the file is the text.
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        f.write(line)
    print(f"wrote {len(line)} chars to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
