from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str, content: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")


def build_outline(brief: str, rules_path: str, preferences_path: str, dry_run: bool) -> str:
    mode = "deterministic safe demo" if dry_run else "local template generation"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""# Generated Outline

Mode: {mode}
Generated at: {generated_at}
Source rules: `{rules_path}`
Preferences: `{preferences_path}`

## Source Brief Snapshot

{brief.strip()}

## Title Options

1. The Rain Collector
2. The Storm Chart
3. Wells Without Rain
4. The Map Under the Ink

## Logline

When a map restorer discovers that repaired maps alter her coastal town by morning, she must choose between protecting an official history and revealing the erased route that once saved women the town refused to remember.

## Theme

Memory becomes dangerous when a community depends on forgetting, and truth becomes intimate when it asks one person to risk belonging.

## Main Character

Lin Qiao, a patient map restorer who reads stains, tears, and scraped ink as evidence. She is practical, guarded, and more comfortable with damaged paper than public confrontation.

## Character Desire

Visible desire: restore the storm chart accurately.

Deeper desire: prove that the missing women, including those connected to her grandmother's past, were not mistakes in the town record.

## Central Conflict

Lin Qiao's restoration threatens the harbor committee's official story. Each corrected map changes the town slightly, making the conflict material rather than symbolic: roads shift, plaques alter, wells remember names, and public rituals become unstable.

## World Texture

- Salt-stiff ledgers and swollen paper fibers.
- Empty rain wells used as civic monuments.
- A harbor committee that treats weather records as political property.
- Families that speak through repairs, recipes, and omissions.
- Monsoon light, stone gutters, brass latches, tide bells, and ink that blooms after midnight.

## Three Act Structure

### Act I: The Map Changes Back

Lin Qiao repairs a minor harbor map and notices a street marker has changed by morning. The storm chart arrives under official supervision, and her grandmother's missing notebook pages become relevant.

### Act II: The Town Edits Itself

Each restoration reveals a suppressed evacuation route. The committee pressures Lin Qiao to preserve the accepted version. Neighbors begin remembering contradictory details, and the empty wells collect rain for the first time in years.

### Act III: The Route Opens

Lin Qiao restores the final layer of the storm chart during a new typhoon warning. The town must decide whether to follow the restored route or repeat the old denial. Lin Qiao chooses public testimony over private safety.

## Chapter Outline

1. The archive receives the storm chart after sunset.
2. Lin Qiao finds scraped ink beneath the official reef marks.
3. A repaired alley appears beside the dry market well.
4. Her grandmother's notebook reveals torn page edges matching the chart paper.
5. The harbor committee offers a public commendation in exchange for silence.
6. A clerk admits that old evacuation records were renamed as inventory lists.
7. Rain gathers in one well and brings up a carved nameplate.
8. Lin Qiao reconstructs the missing route from paper damage and oral fragments.
9. The town ritual fails when the official map no longer matches the streets.
10. During a typhoon warning, Lin Qiao releases the restored chart.
11. Residents follow the erased route and confront the history beneath it.
12. The archive reopens with blank shelves reserved for returned testimony.

## Scene Seeds

- Lin Qiao drying a map with bowls of rice while rain hammers the shutters.
- A committee meeting where every wall map shows a slightly different harbor.
- A child lowering a cup into a dry well and hearing tide bells below.
- Lin Qiao finding her grandmother's pressure marks on a page with no writing.
- A storm-night procession where people carry maps instead of lanterns.

## Risk Notes

- Keep the magical map behavior tied to character choice, not spectacle.
- Avoid making community memory too neat; allow contradiction.
- Preserve Lin Qiao's agency in every major reveal.
- Do not borrow from protected works or imitate a living author's voice.
- Review cultural and historical details before expanding into a full manuscript.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a deterministic fiction outline demo.")
    parser.add_argument("--input", default="examples/sample_story_brief.md")
    parser.add_argument("--output", default="examples/generated_outline.md")
    parser.add_argument("--rules", default="configs/writing_rules.yaml")
    parser.add_argument("--preferences", default="configs/user_preferences.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    brief = read_text(args.input)
    read_text(args.rules)
    read_text(args.preferences)
    content = build_outline(brief, args.rules, args.preferences, args.dry_run)
    write_text(args.output, content)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

