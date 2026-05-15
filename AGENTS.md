# AGENTS.md

## Scope

- Only work inside this repository.
- Do not access parent directories.
- Do not scan the wider user profile or unrelated folders.
- Do not read private accounts, private notes, private chats, or unpublished personal writing.

## Public Portfolio Safety

- Do not upload real private text, real diary material, real business material, client material, or internal material.
- Do not introduce real company names, real collaborators, real customers, or private operational details.
- Do not introduce the restricted commercial entities named by the project owner in the task boundary.
- All examples must be original fictional writing created for this repository.

## Writing Ethics

- Do not imitate the concrete style of any living author.
- Do not use copyrighted source text.
- All generated output must be original.
- If a user asks for the style of a living author, provide high-level craft analysis and an original alternative instead.
- Do not create plagiaristic text.

## Male Gaze Revision

- Revisions should reduce objectifying description while preserving literary texture.
- Restore the character's action, desire, judgment, context, and interior experience.
- Do not turn revision into mechanical deletion or slogans.
- Always include a revision rationale when changing point of view or body-focused language.

## Required Checks

- After changes, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\portfolio_audit.ps1
```

- If the audit reports `AUDIT RESULT: FAIL`, do not commit or push.
- Run the Safe Demo commands before publishing changes.

