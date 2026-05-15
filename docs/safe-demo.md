# Safe Demo

The Safe Demo uses only public, fictional example files in this repository. It does not call external models, does not read private files, and does not require any account credentials.

## Standard Commands

```powershell
python scripts\generate_outline.py --input examples\sample_story_brief.md --output examples\generated_outline.md --rules configs\writing_rules.yaml --preferences configs\user_preferences.yaml --dry-run
python scripts\generate_inspiration.py --brief examples\sample_story_brief.md --character examples\sample_character_seed.md --output examples\generated_inspirations.md --rules configs\writing_rules.yaml --preferences configs\user_preferences.yaml --dry-run
python scripts\revise_scene.py --input examples\sample_scene.md --output examples\generated_revision.md --rules configs\writing_rules.yaml --ethics configs\style_ethics.yaml --preferences configs\user_preferences.yaml --dry-run
python scripts\remove_male_gaze.py --input examples\sample_scene.md --output examples\generated_male_gaze_revision.md --rules configs\male_gaze_rules.yaml --dry-run
```

## Windows Compatible Commands

```powershell
py -3 scripts\generate_outline.py --input examples\sample_story_brief.md --output examples\generated_outline.md --rules configs\writing_rules.yaml --preferences configs\user_preferences.yaml --dry-run
py -3 scripts\generate_inspiration.py --brief examples\sample_story_brief.md --character examples\sample_character_seed.md --output examples\generated_inspirations.md --rules configs\writing_rules.yaml --preferences configs\user_preferences.yaml --dry-run
py -3 scripts\revise_scene.py --input examples\sample_scene.md --output examples\generated_revision.md --rules configs\writing_rules.yaml --ethics configs\style_ethics.yaml --preferences configs\user_preferences.yaml --dry-run
py -3 scripts\remove_male_gaze.py --input examples\sample_scene.md --output examples\generated_male_gaze_revision.md --rules configs\male_gaze_rules.yaml --dry-run
```

## Expected Result

After running the commands, the generated files in `examples/` should be refreshed. Then run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\portfolio_audit.ps1
```

Expected audit line:

```text
AUDIT RESULT: PASS
```

