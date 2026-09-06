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

- [x] 1. 初始化：先写 `.gitignore`（含 `.venv/`、`site/`、`__pycache__/`，另加 `.zcode/`）；`git init -b main`；`uv init --bare`；`uv add mkdocs-material`（锁定 9.7.7+）
- [x] 2. intent.md 与 plan.md 入 `docs/sdlc/2026-09-06-blog-setup/`，首次 commit `9b94bbf`
- [x] 3. `mkdocs.yml` 按配置清单完成。实施备注：① 该版本 Material 要求作者条目必填 avatar，已生成占位图 `docs/assets/avatar.png` 并在 `.authors.yml` 引用；② 博客插件会自动脚手架 `docs/blog/index.md`（默认英文标题 "Blog"），已改为中文标题；③ 占位 `site_url` 若带子路径会让开发服务器按子路径挂载，故占位值用根路径 `https://example.github.io/`，部署门时再改
- [x] 4. 首页、作者文件、MathJax 脚本、两篇示例文章完成（文章二图片语法仅代码块展示；两篇文章加了英文 `slug` 避免中文 URL）
- [x] 5. `.github/workflows/ci.yml` 完成
- [x] 6. `README.md` 完成
- [x] 7. 自测全部通过：strict 构建 EXIT=0 零警告；serve 后首页/博客/两篇文章/归档/分类页均 200；`find site -path '*sdlc*' | wc -l` = 0；浏览器整页截图经视觉核验：界面全中文、MathJax 行内与块级公式均正确渲染（$e^{i\pi}+1=0$ 与 argmin 求和公式）、无排版问题
- [x] 8. 全部站点源码与工作流已 commit `b8d855b`（10 文件 394 行），工作树干净
- [x] 9. 独立复核 PASS（2026-09-06，全新只读子代理）：文件清单/关键配置/CI/git 状态 4 大项全过，验证命令亲跑贴输出均符合预期。其「avatar.png 不存在」的观察经查为误报（文件存在且被跟踪）
- [ ] 10. 部署门（唯一需另行授权环节）。执行环境偏差：本机未装 `gh` CLI，原计划中 gh 命令不可用，改用等价路径：
  1. 已确认 GitHub 身份：用户名 `Soflari`（SSH 认证实测通过，密钥与代理配置在 `~/.ssh/config`）；已核查其名下无 `blog`、无 `soflari.github.io` 仓库，两名字可用
  2. 与用户确认仓库名与建仓方式（网页建仓或本机凭据 API 建仓）→ 修正 `site_url` 并 commit
  3. 授权后加 SSH remote 推送 `main`
  4. 等待 Actions：轮询 `git ls-remote --heads origin gh-pages`（非空即分支已生成）+ 公开 API `api.github.com/repos/Soflari/<repo>/actions/runs` 看结论
  5. 开通 Pages 指向 `gh-pages` 分支（gh 不可用：用户网页 Settings→Pages 操作，或经授权用本机凭据调 REST API POST）
  6. curl Pages 地址确认 200（非 200 等 30-60 秒重试）
- [ ] 11. 收尾：完成标记与复核结论更新 commit；`C:\Users\Lenovo\.sdlc\log.md` 追加一行；向用户提示事后抽查方式

## 验证方式

- `uv run mkdocs build --strict`：退出码 0，无警告
- `uv run mkdocs serve` 后：`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/`、`http://127.0.0.1:8000/blog/`、任一文章页（以列表页实际链接为准），均为 200
- `find site -path '*sdlc*' | wc -l` 为 0
- 浏览器截图：中文界面、博客文章流、MathJax 公式渲染正常
- 部署后（授权后执行）：`curl https://<用户名>.github.io/<仓库名>/` 返回 200

## 完成标记

（每完成一步把 `[ ]` 改成 `[x]` 并简注结果；跨会话续作从这里恢复）

- 步骤 1-9 已完成，详见上方勾选与备注（2026-09-06）
- 实现复核结论：独立复核 PASS（全新子代理逐项对照 + 亲跑验证）
- 待办：步骤 10 部署门（等用户确认仓库名/建仓方式并授权）、步骤 11 收尾
