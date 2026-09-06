# 需求意图：搭建个人博客（MkDocs Material + GitHub Pages）

- 日期：2026-09-06
- 分级：L1｜判定理由：单一功能（全新博客脚手架）、目标目录为空、无存量代码可破坏、本地部分完全可逆；唯一外部副作用（推送 GitHub 发布）由部署门单独管控，故不升 L2。用户可随时改判。

## 问题背景

用户想要一个类似 https://yuhangzhou88.github.io/ESL_Solution/ 的个人站点（该站是 MkDocs Material 文档手册型）。经澄清，用户要的是传统博客型：按日期发文、带归档和分类标签，仍用 MkDocs Material 搭建，部署到 GitHub Pages，初始为空架子加示例页。

## 目标

1. 用 MkDocs Material 搭好博客骨架：Markdown 写作、MathJax 数学公式、代码高亮、搜索、中文界面
2. 本地可预览、可严格构建（零警告）
3. 推送到 GitHub 后由 Actions 自动构建发布到 GitHub Pages

## 非目标

- 不迁移历史笔记
- 不写正式博文（只放示例文章）
- 不做评论/统计/多语言
- 不做文档手册型目录树（后续想要可另提需求）

## 成功标准

- `uv run mkdocs build --strict` 退出码 0（无警告无错误）
- 本地 serve 后首页、博客列表、文章页均返回 HTTP 200，浏览器中 MathJax 公式渲染正常（截图为证）
- 授权部署后 GitHub Actions 发布成功，Pages 地址返回 200

## 约束

- 本机 Python 一律通过 uv 调用，禁止裸 python/pip
- Windows 10 + Git Bash 环境
- 工作目录位于 `C:\Program Files\` 下，若遇写入权限错误立即上报用户裁定，不自行换位置
