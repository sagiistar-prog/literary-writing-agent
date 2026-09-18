# Maintenance log

## 0.3.0 — 2026-09-18

- Removed fixed story outputs; host-authored proposals now bind to the exact active input and instructions.
- Added precise, non-overlapping edits, independent author selections, undo, stale-input rejection and manuscript export.
- Added four complete fictional proposal fixtures and an independently authored forward-test fixture.
- Added real desktop/mobile browser regression and strengthened publishable-file auditing.
- Protocol output changes to 2.0 / author_review; proposal format is 1.0. Legacy CLI names remain as request preparation commands.

## 0.2.0 — 2026-09-17

- Added a versioned Codex plugin manifest with the existing Skill.
- Added validated JSON input/output, a fictional input fixture and an explicit artifact export path.
- Documented the actual offline capability and its limitations.
- Added executable contract and regression checks; see `tests/`.
- Product decision: 创作工具首先保护草稿。切换和载入不能默默覆盖未保存文字；检查输出与生成稿分离，每种任务保留自己的结果。

The version labels a repository iteration, not a hosted product launch or a marketplace release.

## 2026-09-17 Product reliability release

保留作者控制的创作台。补齐产品案例、能力证据、指标契约、开源取舍与持续检查。验证范围和未验收项见 docs/validation.md。
