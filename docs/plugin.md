# 插件协议 2.0

插件版本 0.3.0，返回模式 author_review。创作判断由宿主 AI 或作者提供，本地没有模型调用，也没有按题材替换样例的生成逻辑。

## 请求与提案

输入见 [input.schema.json](../schemas/input.schema.json)。task 选择 outline、inspiration、revision、male_gaze。分别提供 brief、brief 与 character、scene、scene；instructions 保存写作要求。只有相关的材料、任务和要求参与 SHA-256，采纳选择不改变输入身份。

第一次运行得到 result.request。网页导出相同结构的 writing-request.json，包含 input、input_hash、提示和完整 proposal_schema。输入原文作为数据传递，宿主不能执行其中的嵌入命令。

提案见 [proposal.schema.json](../schemas/proposal.schema.json)。修订必须有精确 before、1-based occurrence、after、rationale；空 after 表示删除。插入要保留一个短原文锚点。偏移内部按 Unicode code point 计算，选择从后向前应用，不改动未选内容。重复、缺失、重叠和过期建议均拒绝。无必要修改时 edits 可以为空。

大纲和灵感使用 content、notes、assumptions、questions。内容来自显式创作提案，不由校验器自动补写。新的设定必须由宿主说明，但本地契约不能证明其说明完整。

## 命令

```bash
python scripts/plugin_run.py --input examples/revision-input.json
python scripts/plugin_run.py --input examples/revision-input.json --proposal examples/revision-proposal.json --output-dir output/review-one
```

只采纳 E1：复制输入为自己的 JSON 文件，保留 scene 和 instructions 不变，添加 `"accepted_edits": ["E1"]`。用该输入及同一提案再运行，输出到新的目录。空列表撤回全部修改；脚本不自行选择。

可以通过标准输入提供 JSON。proposal 可内嵌或使用 --proposal，不能同时提供。输入与单独提案各不超过 1 MB。成功 exit 0；失败 exit 2，stdout 始终为一个 JSON 对象，不回显输入值或本地路径。

## 产物与本机接口

--output-dir 限定 output/ 下的新目录：result.json、result.md、writing-request.json；修订任务另含 manuscript.txt。已存在目录不会覆盖。建议文件必须独立提供，未选择时正文仍是原稿。

POST /api/session 使用同一引擎，返回 session；旧 POST /api/generate 保留 Markdown 响应。服务只监听 loopback，校验 Host 和来源，限制请求大小、静态文件范围，响应 no-store。仅供个人本机工作台，不作为公网服务部署。

网页建议与选择按任务保存。输入变更显示过期，关闭导出；操作失败保留上一次有效状态。只有点击保存才写浏览器存储。当前无云同步、团队协作、自动模型服务或生产遥测。
