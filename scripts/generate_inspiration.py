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


def build_inspirations(brief: str, character: str, rules_path: str, preferences_path: str, dry_run: bool) -> str:
    mode = "deterministic safe demo" if dry_run else "local template generation"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""# Generated Inspirations

Mode: {mode}
Generated at: {generated_at}
Source rules: `{rules_path}`
Preferences: `{preferences_path}`

## Source Brief Snapshot

{brief.strip()}

## Character Seed Snapshot

{character.strip()}

## Premise Variations

1. Every map Lin Qiao repairs restores one erased civic memory, but the town loses one comfortable lie in exchange.
2. The rain wells are not empty; they are holding back the names removed from official records.
3. A storm chart becomes a contested witness when its repaired coastline contradicts the town's founding ceremony.
4. Lin Qiao can save the town from a coming typhoon only by revealing why the last rescue route was buried.

## Image Seeds

- Ink spreading like rain through cotton paper.
- Brass map weights shaped like small sleeping fish.
- A dry well with wet fingerprints around its stone rim.
- Tide bells ringing on a windless afternoon.
- A street sign whose letters rearrange after midnight.
- A notebook page showing pressure marks but no visible ink.

## Setting Seeds

1. A municipal archive built above an old boat shed.
2. A market street where gutters lead to ceremonial wells.
3. A harbor office with maps locked behind cloudy glass.
4. A roofed footpath used only during typhoon drills.

## Character Contradictions

- Lin Qiao avoids public speech but keeps uncovering evidence that requires witnesses.
- She distrusts rumor yet depends on fragments of oral memory.
- She wants to protect her family but cannot protect them with silence.
- She restores damaged paper while refusing to repair certain family relationships too quickly.

## Conflict Seeds

- The committee asks her to label the restored route as an artistic error.
- A neighbor remembers being carried through a hidden tunnel but fears being mocked.
- The restored map changes property lines, exposing who benefited from forgetting.
- Lin Qiao's mother asks her to stop before the family name is dragged into hearings.
- A new storm warning forces the town to test the disputed route before anyone is ready.

## Opening Scene Ideas

1. Lin Qiao opens the archive shutters and finds rain falling upward from a dry well in the courtyard.
2. A courier delivers the storm chart wrapped in oilcloth and refuses to sign the receipt.
3. During a civic ceremony, a public map drops from the wall because its frame no longer fits.
4. Lin Qiao repairs a tiny tear and wakes to find a missing alley outside her window.

## Symbolic Motifs

- Wells as memory chambers.
- Maps as negotiated truth.
- Rain as delayed testimony.
- Brass latches as pressure and restraint.
- Scraped ink as evidence of deliberate forgetting.

## Questions for the Writer

1. What does Lin Qiao fear losing if the town believes her?
2. Which person benefits most from the erased route staying hidden?
3. What did her grandmother choose not to say while alive?
4. How should the map magic limit itself so choices still matter?
5. What public ritual best reveals the town's edited memory?
6. What final image proves Lin Qiao has changed without explaining the change?

## Originality Note

These prompts are generated from the repository's fictional sample materials and should be developed into new scenes rather than treated as borrowed plot.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deterministic fiction inspiration prompts.")
    parser.add_argument("--brief", default="examples/sample_story_brief.md")
    parser.add_argument("--character", default="examples/sample_character_seed.md")
    parser.add_argument("--output", default="examples/generated_inspirations.md")
    parser.add_argument("--rules", default="configs/writing_rules.yaml")
    parser.add_argument("--preferences", default="configs/user_preferences.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    brief = read_text(args.brief)
    character = read_text(args.character)
    read_text(args.rules)
    read_text(args.preferences)
    content = build_inspirations(brief, character, args.rules, args.preferences, args.dry_run)
    write_text(args.output, content)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

