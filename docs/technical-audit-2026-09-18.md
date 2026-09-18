> 历史记录：对应 0.2 版；当前能力和验收见 validation.md。

# 技术验收 2026-09-18

修复本地 HTTP 来源与 Host 校验、负请求长度、服务从其他工作目录启动时读取配置失败，以及异常泄漏本地路径的问题。新增真实 HTTP 请求回归测试。输出仍是确定性写作辅助模板，未宣称模型文学创作质量。

## 复现

`python -m pip install -r requirements-plugin.txt`

`python -m unittest discover -s tests -v`

`python scripts/plugin_run.py --input examples/plugin-input.json`

所有示例为虚构测试资料。没有真实用户参与，本轮仅为技术验收。
