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


def build_revision(scene: str, rules_path: str, ethics_path: str, preferences_path: str, dry_run: bool) -> str:
    mode = "deterministic safe demo" if dry_run else "local template generation"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    revised_scene = """Lin Qiao entered the archive after sunset with the storm chart held flat against her ribs. Damp rope, old glue, and the mineral smell of rainwater rose from the tables. Director Han looked up first. The clerks followed, their silence arranging itself around the doorway.

She noticed the measuring before she noticed their faces: the pause, the quick inventory, the way the room tried to turn her arrival into evidence against her. Lin Qiao shifted the map case higher under her arm and let the brass latch bite into her palm. The pain steadied her.

She placed the chart on the table. No one touched it.

"You restored the missing reef," Director Han said.

"I restored what was under the ink," Lin Qiao said.

The youngest clerk smiled, too lightly, as if accuracy were a mood she might be coaxed out of. Lin Qiao kept her hand on the case. Outside, rainwater threaded through the stone gutters toward the empty wells, carrying grit, leaves, and the sound of something returning by a route the town had stopped naming."""
    return f"""# Generated Revision

Mode: {mode}
Generated at: {generated_at}
Source rules: `{rules_path}`
Ethics: `{ethics_path}`
Preferences: `{preferences_path}`

## Source Scene

{scene.strip()}

## Revised Scene

{revised_scene}

## Revision Notes

- Clarified the scene purpose: Lin Qiao brings contested evidence into a hostile civic room.
- Shifted the room's attention from simple visual inspection to social pressure.
- Strengthened Lin Qiao's embodied perception through the brass latch, rain smell, and archive materials.
- Preserved the original conflict around the restored reef and hidden ink.
- Added a final image that connects rainwater, erased routes, and returning testimony.

## Craft Choices

- Used selective sensory details instead of dense description.
- Varied sentence length to create a quieter pressure before dialogue.
- Kept dialogue minimal so the power struggle stays under the surface.
- Made the protagonist's perception active rather than decorative.
- Honored the preference for memory, secrecy, sensory pressure, and restrained confession only as abstract craft methods.

## Risk Notes

- A full manuscript version should verify cultural, civic, and historical details.
- The map magic should remain bounded by character choice.
- Further revision should check whether each secondary character has a clear motive.

## Originality Note

This revision is newly written from the repository's fictional sample scene. It does not quote protected source text or imitate a living author's concrete style.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Revise a fictional scene with deterministic craft notes.")
    parser.add_argument("--input", default="examples/sample_scene.md")
    parser.add_argument("--output", default="examples/generated_revision.md")
    parser.add_argument("--rules", default="configs/writing_rules.yaml")
    parser.add_argument("--ethics", default="configs/style_ethics.yaml")
    parser.add_argument("--preferences", default="configs/user_preferences.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scene = read_text(args.input)
    read_text(args.rules)
    read_text(args.ethics)
    read_text(args.preferences)
    content = build_revision(scene, args.rules, args.ethics, args.preferences, args.dry_run)
    write_text(args.output, content)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
