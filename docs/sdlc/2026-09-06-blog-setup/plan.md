# 实施计划：搭建个人博客（MkDocs Material + GitHub Pages）

> 评审结论：经 3 轮只读子代理评审收敛（L1 轮审上限），主要修改：MathJax 需 `extra_javascript` 双挂载、启用 `tags` 插件、中文界面键为 `theme.language: zh`、`.gitignore` 前置到 uv 命令之前、Pages 开通须等 Actions 生成 `gh-pages` 分支之后、推送前显式 commit 全部源码等。第三轮发现的 P0（缺 commit 步骤）已按评审建议修复；因轮次达上限未做第四轮复核，此点已请用户知悉。

本计划在空目录 `C:\Program Files\programme\Blog` 用 MkDocs Material 搭建传统博客型站点骨架，并配置 GitHub Actions 实现推送后自动发布到 GitHub Pages。除「推送到 GitHub 发布」（下文统一称**部署门**）需用户另行授权外，其余改动全部本地完成、完全可逆。

## 改动文件

| 文件 | 改动 |
|---|---|
| `pyproject.toml`、`uv.lock` | uv 项目定义与依赖锁定 |
| `.gitignore` | 忽略 `.venv/`、`site/`、`__pycache__/` |
| `mkdocs.yml` | 站点配置（明细见下文配置清单） |
| `docs/index.md` | 首页欢迎页 |
| `docs/blog/.authors.yml` | 作者信息（占位，用户后续自行修改） |
| `docs/blog/posts/2026-09-06-hello-world.md` | 示例文章一：开博说明 |
| `docs/blog/posts/2026-09-06-markdown-guide.md` | 示例文章二：写作语法指南 |
| `docs/javascripts/mathjax.js` | MathJax 渲染参数脚本（官方配方） |
| `.github/workflows/ci.yml` | 自动构建发布工作流 |
| `README.md` | 使用说明 |

`mkdocs.yml` 配置清单：`site_name`（占位「我的博客」）、`site_url`（占位，部署门时修正）、`theme.language: zh`（Material 用 `language` 键）、亮暗色切换、plugins 三项（`blog` 关阅读时长估算、`tags`、`search`）、`pymdownx.arithmatex`（generic 模式）、`extra_javascript` 双挂载（本地配置脚本 + CDN MathJax v3 库）、`exclude_docs: [sdlc/]`。

`ci.yml` 工作流：推送 `main` 触发；`contents: write` 权限；完整检出（`fetch-depth: 0`）→ `astral-sh/setup-uv` → `uv sync --locked` → `uv run mkdocs gh-deploy --force`。

## 步骤

- [ ] 1. 初始化：先写 `.gitignore`（必含 `.venv/`、`site/`、`__pycache__/`，先于任何 uv 命令）；`git init -b main`（本机默认 `master` 而工作流监听 `main`）；`uv init --bare`；`uv add mkdocs-material`
- [ ] 2. 把 intent.md 与 plan.md 写入 `docs/sdlc/2026-09-06-blog-setup/`，首次 commit（`.gitignore` + uv 项目文件 + SDLC 产物）
- [ ] 3. 写 `mkdocs.yml`（按配置清单）
- [ ] 4. 写首页、作者文件、MathJax 脚本、两篇示例文章（文章二的图片语法只以代码块展示、不实际引用，避免死链）
- [ ] 5. 写 `.github/workflows/ci.yml`
- [ ] 6. 写 `README.md`（怎么写新文章：目录/命名/front matter；本地预览命令；发布流程；中文搜索局限）
- [ ] 7. 自测：`uv run mkdocs build --strict`；后台 `uv run mkdocs serve`（等端口就绪再 curl），首页、`/blog/`、任一文章页均 200，验证后停掉后台进程；`find site -path '*sdlc*' | wc -l` 为 0；浏览器确认中文界面、文章流、公式渲染并截图
- [ ] 8. 自测通过后 `git add -A && git commit` 提交全部站点源码与工作流（关键：确保推送的 `main` 包含完整站点，否则 Actions 不触发、`gh-pages` 永不生成）
- [ ] 9. 独立复核：改动文件 >3，另派未参与实施的只读子代理，只凭本计划逐项对照并亲自运行验证命令、贴输出
- [ ] 10. 部署门（唯一需另行授权环节）：
  1. 与用户确认 GitHub 用户名、仓库名，确认建公开仓库（GitHub 免费版私有仓库不支持 Pages）
  2. 按实际地址修正 `mkdocs.yml` 的 `site_url` 并 commit
  3. 用户授权后 `gh repo create` 建远端仓库并推送 `main`
  4. 等待 Actions 成功：`gh run list --branch main --limit 1` 看状态；`git ls-remote --heads origin gh-pages` 非空作为分支已生成的直接证据
  5. 开通 Pages：`gh api -X POST repos/{owner}/{repo}/pages -f 'source[branch]=gh-pages' -f 'source[path]=/'`（须 POST 且分支已存在，故排在 4 之后）
  6. curl Pages 地址确认 200；非 200 则等 30-60 秒重试再判失败（Pages 有传播延迟）
- [ ] 11. 收尾：复核结论与完成标记追加进本文件并单独 commit 该更新；`C:\Users\Lenovo\.sdlc\log.md` 追加一行；向用户提示事后抽查方式

## 验证方式

- `uv run mkdocs build --strict`：退出码 0，无警告
- `uv run mkdocs serve` 后：`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/`、`http://127.0.0.1:8000/blog/`、任一文章页（以列表页实际链接为准），均为 200
- `find site -path '*sdlc*' | wc -l` 为 0
- 浏览器截图：中文界面、博客文章流、MathJax 公式渲染正常
- 部署后（授权后执行）：`curl https://<用户名>.github.io/<仓库名>/` 返回 200

## 完成标记

（每完成一步把 `[ ]` 改成 `[x]` 并简注结果；跨会话续作从这里恢复）
