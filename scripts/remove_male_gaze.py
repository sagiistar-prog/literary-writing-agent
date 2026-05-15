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


def build_male_gaze_revision(scene: str, rules_path: str, dry_run: bool) -> str:
    mode = "deterministic safe demo" if dry_run else "local template generation"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    revised_scene = """Lin Qiao entered the archive after sunset, carrying the storm chart with both hands so the softened paper would not buckle. The room smelled of damp rope and old glue. Director Han looked up first, then the clerks. Their pause told her what kind of meeting this would be: not a review of evidence, but a weighing of whether she had the right to bring it.

Rainwater slid from her sleeves onto the floor. Lin Qiao did not wipe it away. She crossed to the table, set down the chart, and turned the map case so the damaged edge faced the light.

"You restored the missing reef," Director Han said.

"I restored what was under the ink," Lin Qiao said.

The youngest clerk smiled as though the distinction were harmless. Lin Qiao pressed her palm against the brass latch and felt its narrow line of pain. It kept her attention where she wanted it: on the scraped ink, the false reef, the route hidden beneath both. Outside, water ran through the stone gutters toward the empty wells."""
    return f"""# Generated Male Gaze Revision

Mode: {mode}
Generated at: {generated_at}
Source rules: `{rules_path}`

## Source Scene

{scene.strip()}

## Problematic Patterns

- The original doorway moment lets the room measure Lin Qiao visually before the scene restores her interior experience.
- The description risks making her arrival feel like display rather than action.
- The clerk's smile can reduce her answer to charm unless the narration clarifies the power dynamic.

## Revised Scene

{revised_scene}

## Agency Restoration Notes

- Lin Qiao enters with a concrete task: protecting the softened storm chart.
- Her attention moves toward evidence, light, ink, and the damaged edge of the map.
- The narration names the social pressure without making her value depend on it.
- She chooses how to position the map and where to keep her attention.

## Language Changes

- Replaced visual measuring of her body with institutional weighing of her authority.
- Turned wet clothing into weather context and action pressure.
- Reframed the brass latch as a grounding sensation connected to her resolve.
- Kept the scene quiet and literary while reducing objectifying emphasis.

## Revision Rationale

The revision shifts the point of view from observer-centered appraisal to Lin Qiao's subject-centered experience. It keeps tension, sensory detail, and restraint, while making her action and judgment the center of the scene.

## Manual Review Notes

- Check whether later scenes continue to give Lin Qiao decisions with consequences.
- Review every appearance description for purpose, context, and point of view.
- Preserve ambiguity, but do not use ambiguity to hide objectification.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Revise a scene to reduce objectifying perspective.")
    parser.add_argument("--input", default="examples/sample_scene.md")
    parser.add_argument("--output", default="examples/generated_male_gaze_revision.md")
    parser.add_argument("--rules", default="configs/male_gaze_rules.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scene = read_text(args.input)
    read_text(args.rules)
    content = build_male_gaze_revision(scene, args.rules, args.dry_run)
    write_text(args.output, content)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

