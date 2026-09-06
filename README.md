# 我的博客

基于 [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) 的个人博客，托管在 GitHub Pages。

## 快速开始

```bash
uv sync                # 安装依赖（本机 Python 一律通过 uv 使用）
uv run mkdocs serve    # 本地预览，浏览器打开 http://127.0.0.1:8000
```

修改或新增文章后，serve 会自动刷新，无需重启。

## 怎么写新文章

1. 在 `docs/blog/posts/` 下新建 Markdown 文件，命名建议 `YYYY-MM-DD-标题缩写.md`
2. 文件开头写 front matter（YAML 元数据头）：

   ```yaml
   ---
   date: 2026-09-06        # 发布日期，首页按它倒序
   categories:             # 分类（可多个）
     - 教程
   tags:                   # 标签（可多个）
     - Markdown
   authors:                # 作者，对应 docs/blog/.authors.yml 中的条目
     - me
   ---
   ```

3. 正文用 Markdown 写，支持公式、代码高亮、提示框、选项卡等，完整写法参考示例文章《写作语法指南》
4. 发布见下一节

## 发布流程

```bash
git add -A
git commit -m "新文章：xxx"
git push
```

推送到 `main` 分支后，GitHub Actions 会自动构建并把站点发布到 `gh-pages` 分支（见 `.github/workflows/ci.yml`），约一分钟后 Pages 生效。

## 常用命令

| 命令 | 作用 |
|---|---|
| `uv run mkdocs serve` | 本地实时预览 |
| `uv run mkdocs build --strict` | 严格构建（有警告即报错，发布前自检用） |
| `uv run mkdocs gh-deploy --force` | 手动构建并发布（一般不用，推送即自动发布） |

## 目录结构

```
docs/
├── index.md                  # 首页
├── assets/                    # 图片等素材（按需创建）
├── javascripts/mathjax.js    # 公式渲染配置
└── blog/
    ├── .authors.yml          # 作者信息
    └── posts/                # 所有文章
```

## 需要改的占位内容

- `mkdocs.yml`：`site_name`（站点名）、`site_url`（Pages 地址）、`site_description`
- `docs/blog/.authors.yml`：作者名与介绍（头像当前用 GitHub 头像 `https://github.com/Soflari.png`，可换自定义图片，放 `docs/blog/` 下用相对文件名引用，勿用 `../` 开头路径）
- `docs/index.md`：首页欢迎语

## 评论区

文章页底部带 giscus 评论区，评论数据存在 GitHub Discussions（`Soflari/blog` 仓库的 Announcements 分类），评论者需登录 GitHub 账号。

- 所有文章默认开启（`docs/blog/posts/.meta.yml` 里 `comments: true`）
- 单篇关闭：在该文章 front matter 加 `comments: false`
- 评论主题自动跟随站点亮暗色切换

## 已知局限

- 站内搜索基于 lunr，中文分词能力有限：整词命中可用，模糊/语义检索效果一般；后续如需更好的中文搜索可考虑接入第三方方案
- 公式由 MathJax（CDN 加载）在前端渲染，无网络时公式不显示，其余内容不受影响
