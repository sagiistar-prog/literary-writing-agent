# Literary Writing Agent 独立前向测试

测试日期：2026-09-18。使用仓库内 `skills/literary-writing-agent/SKILL.md` 完成一次合成的作者轻修请求。本报告记录真实 CLI 执行和文件核验；作者的后续选择是预先声明的模拟输入，不是真实用户反馈。

## 结果

本次路径通过：请求准备 → 独立撰写建议 → 插件校验 → 保持零采纳 → 模拟仅采纳 E1 → 核对原文其余部分。三个保留完整输出的 CLI 命令均退出 0；独立核验脚本完成 18 项断言。另一次最初的输入哈希获取命令同样退出 0，其输出未另存为文件，后续 `prepared.stdout.json` 保存了同一路径的完整结果。

生成建议前只读取技能、两份 schema、`docs/plugin.md` 和 `requirements.txt`；没有读取任何示例建议包。没有访问网络、私人文件或账号。所有测试文件都位于 `output/forward-test/`；没有编辑产品源码。执行 Python 时设置 `PYTHONDONTWRITEBYTECODE=1`。

## 独立建议与语义复核

作者明确要求第一人称、保留两次“明天再说”、不替人物原谅父亲、不说明信件作者、最多三处建议。原文保留两个换行，不做空白归一化。

本次只提出两处建议，完整包为 `proposal.json`：

| ID | 原文 | 建议 | 取舍 |
| --- | --- | --- | --- |
| E1 | 我觉得特别难过，像一个非常悲伤的人 | 我觉得很难过 | 收紧重复的情绪说明；原句可能表现叙述者生硬的自我观察，理由中明确允许保留。 |
| E2 | 窗上的雾越来越厚，我没有开门。 | 窗上的雾越来越厚。我没有开门。 | 仅提供句读选择，让末句有独立停顿；没有把它描述为必改错误。 |

两处建议均无新增道具、背景、动机或事实。第一人称和信件来源的留白不变，没有添加父亲应被理解或被原谅的判断。父亲仍在门外，叙述者仍没有开门。E2 的句号可能使拒绝显得更坚决，所以应由作者决定；测试中的作者明确没有选择它。

## 执行证据

在仓库根目录执行了下列命令，工作环境已有所需依赖，无须安装：

```text
python scripts/plugin_run.py --input output/forward-test/input.json --output-dir output/forward-test/prepared
python scripts/plugin_run.py --input output/forward-test/input.json --proposal output/forward-test/proposal.json --output-dir output/forward-test/unselected
python scripts/plugin_run.py --input output/forward-test/selected-input.json --proposal output/forward-test/proposal.json --output-dir output/forward-test/selected
```

真实调用由 `verify.py` 通过当前 Python 解释器执行，命令、退出码和断言结果保存在 `verification.json`。每次原始 stdout 与 stderr 分别保存为 `<阶段>.stdout.json` 和 `<阶段>.stderr.txt`，stderr 均为空。

| 检查 | 实测结果 | 文件证据 |
| --- | --- | --- |
| 初始请求没有建议或采纳 | `phase=needs_proposal`；`accepted_edits=[]` | `prepared.stdout.json` |
| 建议包绑定原始输入 | 返回哈希与建议包完全一致 | `proposal.json`、`verification.json` |
| 校验建议不等于采纳建议 | E1、E2 均显示“未采纳” | `unselected/result.md` |
| 零采纳正文忠实保存 | UTF-8 字节与原稿完全一致，无附加换行 | `unselected/manuscript.txt`、`verification.json` |
| 后续作者只选一处 | 模拟“只选择 E1，E2 保留原文”；输入选择为 `["E1"]` | `simulated-author-choice.md`、`selected-input.json` |
| 采纳只作用于所选位置 | 仅原文字符区间 `[36,53)` 被 E1 替换；前后片段分别相等 | `verification.json` |
| 未选建议不生效 | E2 原逗号保留，记录为“未采纳” | `selected/result.md`、`selected/manuscript.txt` |
| 关键约束保留 | 两次“明天再说”、段落换行、父亲在门外、没有开门均保留 | `verification.json` |
| 选择不改变输入绑定 | 准备、零采纳、仅 E1 三个阶段的输入哈希一致 | `verification.json` |

输入哈希：`f9c4f7b74f241e776d2afd96d323f1fed038fed1248cbca655c3d93763abc707`。

原稿 UTF-8 SHA-256：`30acd9d60b4e509ae8a44e54f9d5e07557549e93dc81a37ca8a881b008a972a3`。

仅 E1 稿件 UTF-8 SHA-256：`e5fab1ca7da5d94f711104d351219f81d5978cf3f7898f826eca047aea344b43`。

## 仅采纳 E1 的实际结果

> 我把信压在茶杯下。父亲在门外说，明天再说。
>
> 我说，明天再说。杯子很烫，我觉得很难过。窗上的雾越来越厚，我没有开门。

## 产品与技能摩擦

1. **文档不一致，建议修正。** 技能清楚说明由 AI 宿主提供创作判断、本地工具负责校验与应用选择，本次执行符合这一机制；但技能末尾链接的 `docs/plugin.md` 仍写“固定模板展示写作框架”，列举旧 `examples/plugin-input.json`，且只提 `result.json`、`result.md`。实际本次每阶段都生成四个文件，还包括 `writing-request.json` 和 `manuscript.txt`。读者顺着技能链接阅读 API 文档，可能误以为运行 CLI 会得到模板稿，或漏掉请求与稿件文件。建议同步该文档的能力边界、`--proposal` 流程、选择字段和产物清单。此问题未阻断本次测试。
2. **空问题列表仍渲染空标题。** `questions=[]` 时，`unselected/result.md` 和 `selected/result.md` 均保留空的“待确认”小节。没有需要作者补充的事项时，可省略标题或显示“无”。这是小幅展示问题，不影响稿件保真。
3. **CLI 的单独采纳步骤仍需手动组装。** 技能明确要求 `accepted_edits` 只包含作者选择的 ID，但没有给出从已有输入构造仅单项选择文件的短例子。本次从 schema 正确推得要复制输入并将该字段改为 `["E1"]`；其余字段不变，哈希保持一致。建议增加一个极短选择示例，减少宿主自行推断。这是文档可用性建议，未观察到执行故障。

## 证据边界

这次证明该合成请求的 schema、定位、零采纳保护和单项选择路径可以运行，且未选原文被精确保留。语义约束的判断来自本次人工式内容复核与明确文本核验，不能由 schema 校验单独保证。

未测试本地网页导入按钮、撤销交互、浏览器持久化或安装到 Codex App；没有采集真实作者满意度、完成率、效率、创作水平变化或商业结果。未把两处建议的文学质量视为客观评分，也没有虚构作者接受意愿。

`verify.py` 的输出目录固定用于保留这次证据，重复运行会因目录已存在而被产品拒绝；复测应使用新的输出目录。这里不删除既有证据。
