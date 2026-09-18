# 开源选择与贡献边界

2026-09-18 检查官方仓库和许可证。星数只用于发现候选，不是是否采用的结论。

| 项目 | 检查与选择 | 实际采用 |
|---|---|---|
| [jsonschema](https://github.com/python-jsonschema/jsonschema) | MIT，Python Draft 2020-12 实现，约 4,983 stars，GitHub 仓库仍维护 | 输入、建议包与输出校验 |
| [ProseMirror](https://github.com/ProseMirror/prosemirror) | 约 8,701 stars；GitHub 聚合仓库已归档，README 指向迁移后的开发站；富文档和协作能力超出本次纯文本审阅需要 | 阅读官方说明，未复制或引入 |
| [CodeMirror](https://github.com/codemirror/dev) | GitHub 开发仓库约 7,818 stars，已归档；不能把旧聚合仓库当作新依赖入口 | 候选比较，未接入代码编辑器 |
| [Playwright](https://github.com/microsoft/playwright) | Apache-2.0，可执行真实浏览器交互，锁定开发依赖版本 | 导入、选择、撤销、保存、下载与响应式检查 |
| [axe-core](https://github.com/dequelabs/axe-core) | MPL-2.0，可自动发现部分无障碍缺陷 | 测试注入指定 WCAG 规则，不进入产品运行资源 |

产品页使用原生文本框、按钮和 details，避免为只读对照和短篇修订引入完整富文本框架。未来需要长篇批注或协作时，再评估文档模型及编辑历史迁移成本。这个取舍来自当前任务，不表示上述编辑器质量不足。

可归属的本项目工作：用户控制流程、输入身份、原文定位协议、逐条决策与撤销、错误恢复和验收设计。没有把通用模型或开源库说成自研能力。Impeccable 用于交互与视觉检查，未复制参考图的图片或品牌素材。
