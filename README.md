# Literary Writing Agent

Literary Writing Agent 是一个原创文学写作辅助 Agent 作品集项目，用于帮助作者从早期灵感走到可修改的大纲、人物、场景和章节计划。它强调原创写作支持，而不是风格复制。

## 面试官 30 秒版

这个项目展示了一个面向原创小说创作的 Agent 工作流：输入故事简述、人物种子或场景草稿，输出小说大纲、灵感池、润色版本和去男性凝视改写建议。项目包含结构化写作规则、伦理边界、可运行的 Safe Demo、原创示例文本和公开仓库审计脚本，适合作为 AI Agent 产品思维、提示工程、安全边界和内容生成流程的作品集样例。

## 项目解决什么问题

许多写作者在小说早期会卡在四类问题上：

- 只有气氛或主题，但缺少可展开的叙事结构。
- 有角色设定，但角色欲望、冲突和章节推进不够清晰。
- 场景文字有信息，但缺少感官细节、情绪暗流和文学节奏。
- 女性角色容易被写成被观看、被评价、被功能化的对象。

本项目把这些问题拆成可审阅、可迭代的 Agent 工作流，并用规则文件约束输出边界。

## 输入和输出

输入可以是：

- `examples/sample_story_brief.md`：原创故事简述。
- `examples/sample_character_seed.md`：原创人物种子。
- `examples/sample_scene.md`：原创场景草稿。
- `configs/*.yaml`：写作规则、伦理规则和偏好设置。

输出包括：

- `examples/generated_outline.md`：标题候选、logline、主题、人物欲望、三幕结构、章节大纲、场景种子和风险提示。
- `examples/generated_inspirations.md`：前提变体、意象种子、场景种子、人物矛盾、冲突种子、开场方案、象征母题和追问。
- `examples/generated_revision.md`：润色后的场景、修改说明、工艺选择、风险提示和原创性说明。
- `examples/generated_male_gaze_revision.md`：问题模式、改写文本、主体性恢复说明、语言变化和 revision rationale。

## 工作流阶段

1. 读取故事简述、人物种子或场景草稿。
2. 载入写作规则、伦理规则和用户偏好。
3. 按任务生成结构化草案：大纲、灵感、场景润色或主体视角改写。
4. 输出 revision notes，说明为什么这样改，而不只给出改写结果。
5. 运行 Safe Demo 和作品集审计，确认公开仓库内容安全。

## 原创小说大纲编撰能力

`scripts/generate_outline.py` 会把故事简述整理为可继续创作的小说骨架，包括：

- title options
- logline
- theme
- main character
- character desire
- central conflict
- world texture
- three act structure
- chapter outline
- scene seeds
- risk notes

## 灵感生成能力

`scripts/generate_inspiration.py` 会基于故事简述和人物种子生成非侵权、非复制式灵感池：

- premise variations
- image seeds
- setting seeds
- character contradictions
- conflict seeds
- opening scene ideas
- symbolic motifs
- questions for the writer

## 场景润色能力

`scripts/revise_scene.py` 会在保留原创意图的基础上强化：

- 场景目的
- 感官细节
- 情绪潜台词
- 叙事节奏
- 散文化表达
- 修订说明

## 去男性凝视表达能力

`scripts/remove_male_gaze.py` 会识别并改写把女性角色写成被观看对象的表达，重点恢复角色的行动、欲望、判断和主体经验。改写目标是保留文学性，而不是把文本变成机械口号。

## 写作伦理边界

- 不模仿任何在世作家的具体文风。
- 不复制、改写或搬运受版权保护文本。
- 不做风格克隆。
- 只使用高层写作维度，例如叙事节奏、意象组织、自然描写、人物观察、情感留白、荒诞现实感、口语感、散文化表达、女性主体视角。
- 如果用户要求模仿具体在世作者，Agent 应改为提供高层写作特征分析和原创替代方案。
- 如果用户提供外部文本作为参考，仓库只保存抽象写作方法，不保存源段落、近似句式或独特比喻。

## 公开仓库隐私说明

本仓库是公开作品集项目，不包含真实私人文本、真实日记、真实商业资料、客户资料或内部项目资料。`examples/` 中的所有文本均为原创虚构示例，只用于演示 Agent 工作流。

## Safe Demo

这些命令不调用外部模型，也不读取私人材料。`--dry-run` 表示使用本地确定性模板生成公开演示输出。

```powershell
python scripts\generate_outline.py --input examples\sample_story_brief.md --output examples\generated_outline.md --rules configs\writing_rules.yaml --preferences configs\user_preferences.yaml --dry-run
python scripts\generate_inspiration.py --brief examples\sample_story_brief.md --character examples\sample_character_seed.md --output examples\generated_inspirations.md --rules configs\writing_rules.yaml --preferences configs\user_preferences.yaml --dry-run
python scripts\revise_scene.py --input examples\sample_scene.md --output examples\generated_revision.md --rules configs\writing_rules.yaml --ethics configs\style_ethics.yaml --preferences configs\user_preferences.yaml --dry-run
python scripts\remove_male_gaze.py --input examples\sample_scene.md --output examples\generated_male_gaze_revision.md --rules configs\male_gaze_rules.yaml --dry-run
```

如果 `python` 不可用，可以使用 Windows Python Launcher：

```powershell
py -3 scripts\generate_outline.py --input examples\sample_story_brief.md --output examples\generated_outline.md --rules configs\writing_rules.yaml --preferences configs\user_preferences.yaml --dry-run
py -3 scripts\generate_inspiration.py --brief examples\sample_story_brief.md --character examples\sample_character_seed.md --output examples\generated_inspirations.md --rules configs\writing_rules.yaml --preferences configs\user_preferences.yaml --dry-run
py -3 scripts\revise_scene.py --input examples\sample_scene.md --output examples\generated_revision.md --rules configs\writing_rules.yaml --ethics configs\style_ethics.yaml --preferences configs\user_preferences.yaml --dry-run
py -3 scripts\remove_male_gaze.py --input examples\sample_scene.md --output examples\generated_male_gaze_revision.md --rules configs\male_gaze_rules.yaml --dry-run
```

运行作品集审计：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\portfolio_audit.ps1
```

审计通过时会输出：

```text
AUDIT RESULT: PASS
```
