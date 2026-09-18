from __future__ import annotations

import argparse
from pathlib import Path


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str, content: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")


def build_male_gaze_revision(scene: str, rules_path: str, dry_run: bool) -> str:
    from writing_session import run_session
    return run_session({"task":"male_gaze", "scene":scene})["markdown"]


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

