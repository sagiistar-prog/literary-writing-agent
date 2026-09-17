---
name: Literary Writing Agent
description: 保留作者草稿与选择权的紫灰写作工作台
colors:
  ink: "#202833"
  muted: "#5c6177"
  paper: "#f6f6fb"
  surface: "#ffffff"
  surface-cool: "#f0f0fa"
  line: "#dcdde9"
  teal: "#5d54ae"
  teal-dark: "#423b87"
  wine: "#783f4d"
  graphite: "#292d46"
typography:
  body:
    fontFamily: 'Inter, "Segoe UI", "Microsoft YaHei", "PingFang SC", Arial, sans-serif'
    letterSpacing: "0em"
  headline:
    fontSize: "30px"
    lineHeight: 1.15
  title:
    fontSize: "17px"
  input:
    fontSize: "16px"
    lineHeight: "32px"
  label:
    fontSize: "13px"
    fontWeight: 800
rounded:
  control: "8px"
  code: "6px"
spacing:
  page: "28px"
  panel-gap: "18px"
  field: "16px"
components:
  button-primary:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "0 14px"
  button-primary-hover:
    backgroundColor: "{colors.teal-dark}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 14px"
---

# Design System: Literary Writing Agent

## Overview

**Creative North Star: "作者的安静书桌"**

深紫灰任务区围合浅色稿纸，紫色选择态帮助作者知道当前在做什么。草稿、札记、插图与生成稿各自独立，避免让辅助生成夺走写作主体位置。

本文件根据 web/styles.css、web/index.html 和 web/app.js 合并当前设计。冷灰纸面与蓝紫动作是主线；现有暖白稿纸、酒红细节和绿色字段 focus 仍存在，不描述为已完成全站统一。

## Colors

现有 token 名 teal、teal-dark 的实际颜色为紫色和深紫色，保留代码键名以免产生两套来源。Graphite 承载导航背景，paper 承载主区，line 分隔字段与结果；wine 保留报告三级标题及侧栏渐变色调。

正文面板实际使用暖白半透明背景，稿纸底色也是暖白。输入 focus 的绿色半透明轮廓属于现有实现，不能在文档中擅自写成紫色。

## Typography

正文使用本机无衬线栈；Inter 并无当前样式中的自托管定义。任务主标题为 headline，640px 以下 24px；品牌标题为 18px。稿纸输入按 input 行高与横线对齐，生成稿正文行高 1.68，标题另用 1.25。

标题与操作保持简短，修订理由与草稿内容在各自工作区呈现，避免将大段说明塞入导航。

## Layout

桌面侧栏宽 310px，主区留白 28px。创作台与右侧札记/插图区使用双栏，间距 18px；生成稿独占下方区域，正文最大高 620px 后滚动。

1100px 以下侧栏移至上方；900px 以下创作台转单列，右侧两面板并排；640px 以下右侧面板也转单列。760px 以下任务入口最终保留四列紧凑排列，项目区可折叠，隐藏品牌副文案和侧栏边界卡。该最终覆盖优先于较早的单列任务样式。

## Elevation & Depth

工作板使用统一柔影（0 24px 70px rgba(32, 40, 51, 0.13)）；侧栏项目卡以半透明底与 14px 模糊形成次级层次。稿纸横线是轻微背景纹理，不是内容分隔器。

按钮背景与阴影过渡为 160ms ease-out，按下位移 1px；reduced-motion 关闭动画与过渡。不为本地模板生成加入虚构模型思考动画。

## Shapes

工作板、按钮、标签、插图卡采用 control 圆角；行内代码使用更小圆角。边框界定可编辑区域，空插图板以虚线表示待添加内容。

## Components

- 主动作与选中任务使用紫色，次按钮使用白底细边框。主/次按钮及上传按钮的类规则最小高 38px；通用 44px 声明不会覆盖它们，不能声称全站统一尺寸。
- 桌面任务入口最小高 50px，760px 以下为 44px；当前任务拥有明确选中态。
- 稿纸与札记按任务保存输入。处理中相关字段、任务切换和生成控件禁用，避免跨任务结果串位。
- 创作库可折叠；替换未保存内容需确认。保存失败仍应提供导出路径，状态行以实际文本说明结果。
- 生成稿始终显示离线模板性质；输入保留在原工作面，不把生成内容自动当作作者已接受的改稿。
- 按钮和折叠摘要有 focus-visible 轮廓，上传标签有 focus-within 提示；它们是当前交互实现，不构成完整可访问性认证。

## Do's and Don'ts

- **Do** 让原稿、建议和已保存作品可区分，保留作者选择权。
- **Do** 用留白和稿纸节奏支持阅读，以状态文字说明保存、失败和生成。
- **Don't** 增加间隔点、无用眉题、假模型进度或虚构创作成果。
- **Don't** 将旧 token 的名称误当色相，或把未统一的控件尺寸写成既成规范。
