from __future__ import annotations

import argparse
from pathlib import Path


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str, content: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")


def build_inspirations(brief: str, character: str, rules_path: str, preferences_path: str, dry_run: bool) -> str:
    from writing_session import run_session
    return run_session({"task":"inspiration", "brief":brief, "character":character})["markdown"]


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

