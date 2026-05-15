# Workflow

## 1. Intake

The user provides one of three public-safe inputs:

- a story brief
- a character seed
- a scene draft

The Agent treats the input as raw creative material, not as finished text.

## 2. Rule Loading

The scripts accept rule files from `configs/`:

- `writing_rules.yaml`
- `style_ethics.yaml`
- `male_gaze_rules.yaml`
- `user_preferences.yaml`

The Safe Demo reads these files as context references and records their paths in the generated output.

## 3. Generation

Each task produces a structured artifact:

- outline generation
- inspiration generation
- scene revision
- male gaze revision

The generated files are intentionally reviewable and sectioned.

## 4. Explanation

Every revision-oriented output includes notes about craft choices, risk notes, and originality. This makes it easier for a writer or reviewer to understand what changed and why.

## 5. Audit

Before publishing, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\portfolio_audit.ps1
```

The audit checks tracked files when a Git index exists. Before the first commit, it scans candidate project files inside the repository only and excludes generated work folders.

