# Hugo 博客文章迁移计划（L1，2026-09-08 批准）

> 评审记录：经 3 轮只读评审轮审收敛（第 1 轮双视角 2 代理、第 2/3 轮互审各 1 代理）+ 2 处难点分片深审（公式防护、源稿判定）+ 2 次链尾终检（第 1 次抓出内链改写规则 FAIL、已修正，第 2 次 PASS）。主要修改：公式改用占位符法绕开转换器、以 `p/` 目录为唯一全集（RSS 作主源会漏掉「注意力模块」这篇 70KB 长文）、链接匹配前加归一化、移除对不存在的 gh 命令的依赖。
> 本版变更：迁移范围按用户指示收窄为 5 篇（白名单制），其余 12 篇默认跳过并留档——日后想补，按 `source_permalink` 锚点重跑脚本即可。

## 一、要做什么，为什么

把 GitHub 上旧 Hugo 博客（`Soflari/hugo_dev`）里用户指定的 5 篇文章，搬进现在这个 MkDocs 博客的 `docs/blog/posts/`：格式自动转换、构建验证通过后本地提交；经用户确认后再 push 上线（push 触发 CI 自动发布，时机由用户定）。

关键事实：hugo_dev 里只有 Hugo 构建产物（渲染好的 HTML 网页，没有 Markdown 原稿）。本机、GitHub 公开仓库、hugo_dev 的默认分支 git 历史都查过没有源稿（探测记录留档）。所以走**网页逆向**——从产物网页反向提取内容重组成 Markdown。以后找到源稿，按锚点字段（`source_permalink`）重跑脚本覆盖升级。旧站本身不动，老链接不失效。

这 5 篇全是数学公式重灾区（张量推导、统计学习推导），方案的重心就在公式保真。

## 二、执行步骤

### 准备 1 · 源稿探测留档
- [x] 问用户一次源稿位置（批准门确认，用户未提供 → 走网页逆向）。
- [x] curl GitHub API：hugo_dev 提交历史 path 计数（content/config.toml/hugo.toml/archetypes/assets 全 0）；用户公开 events/gists 无信号。
- [x] `git ls-remote --heads --tags`：仅 `refs/heads/main`，无额外分支/tag（2026-09-08 执行时确认）。
- [x] 本机只读探测：Desktop/Documents/Downloads、无其他盘、hugo 不在 PATH，全阴性。

### 准备 2 · 拿产物
- [ ] clone hugo_dev 到临时目录；以 `p/` 目录枚举为唯一全集（现场重算数量）；`en/`、`ar/` 一次性确认无重复文章。

### 链接统一预处理
产物链接形态混杂（RSS 是 `http://localhost:1313/hugo_dev/p/<编码slug>/`、正文是 `https://soflari.github.io/hugo_dev/...`、中文百分号编码）。所有匹配前先三步归一化：剥 scheme+host、剥 `/hugo_dev` 前缀、percent-decode，再按 `^/p/[^/]+/$` 判形状。

### 转换（一次性脚本）
脚本放本目录（不进构建，留档可复跑），`uv run --with beautifulsoup4,markdownify python 脚本.py` 跑；不给项目加依赖（CI `uv sync --locked` 锁死，动 `uv.lock` 会挂部署）。
- 每篇解析 `p/<slug>/index.html` 本身（正文/标题/日期）；RSS 只作元数据交叉。
- **公式占位符法**（零经过转换器）：DOM 文本节点按 KaTeX 同款定界符抠公式（先块 `$$` 后行内 `$`），跳过 script/noscript/style/textarea/pre/code/option 节点（KaTeX auto-render 默认忽略集），替换为纯字母数字 token → markdownify（关闭三个 escape 选项）转 Markdown → 回填原文。替换前断言 token 不在原文。
- 断言清单（全量跑，不抽样）：①公式串逐字节在场；②token 回填后清零；③块公式独立成段（列表内不自动改转人工）；④行内定界符内侧非空白；⑤表格内 `\|` 报警；⑥`<title>` 无站名分隔符（·、|、—）且与 og:title/h1 一致。任一 FAIL 中断该篇转人工。
- front matter 映射：页面标题→正文首行 `#`（已有则不插）；发布时间→`date`（实测 time 时区后统一 `YYYY-MM-DD`）；目录名→`slug`（中文保留）；旧站标签→`tags`（categories 留空待用户定）；固定 `authors: [me]`；锚点 `source_permalink: hugo_dev:p/<slug>/`。零值/缺失日期不猜，进待补清单。
- 图片：img 的 src/srcset 非 http(s) 即站内资源，归一化剥 `/hugo_dev` 前缀后按仓库相对路径取（page bundle 形态、与页面同目录），拷 `docs/assets/<slug>/`，引用改 `../../assets/<slug>/文件名`；外链原样。
- 正文内链：归一化后命中迁移集（5 篇之间）→ 改指目标文章 `.md` 源文件同目录相对路径（以实际输出文件名为准），MkDocs 构建时自动重写 URL；不在迁移集或旧站专有页 → 保留外链进 checklist。
- 输出 `YYYY-MM-DD-<slug>.md` 到 `docs/blog/posts/`。

### 验证
- [ ] `uv run mkdocs build --strict` 退出码 0 无 WARNING（CI 不做 strict，本地是唯一闸门；内链失效在这报——图片资源存在性 strict 不查，靠浏览器过目兜底）。
- [ ] 双向对账：正向 `p/` 全集数 = 迁移 5 + 跳过 12；反向 RSS/sitemap（下钻三个子 sitemap）/search JSON/archives/分页目录里归一化后的文章链接 ⊆ `p/` 枚举（差集非空报警转人工）。
- [ ] 公式冒烟：grep `site/` 里 5 篇的 arithmatex span 完整性（`\begin{cases}`、`\\`、`\mathbf`、`\operatorname` 原样）；注意力篇加计数对账（源公式数 = span 数）。
- [ ] 浏览器过目：`uv run mkdocs serve` 抽查 5 篇，与旧站对拍一篇（KaTeX→MathJax 命令集有差异）。

### 独立复核（改动超 3 个文件，必触发）
- [ ] 另起未参与实现的只读子代理：给本计划 + 验证命令 + 新增文件路径清单 + checklist.md，逐项打勾并亲自跑 strict 构建贴输出。

### 交付
- [ ] 本目录落盘 checklist.md（跳过及理由/待人工项/需过目篇目+provenance/待补日期标签 四合一）。
- [ ] `git commit`（不 push；push 由用户授权后执行，CI 自动发布，然后线上抽查）。
- [ ] `C:\Users\Lenovo\.sdlc\log.md` 追加索引行（不存在则创建）。
- [ ] 交付时告知：迁移文自动开 giscus 评论（不想要单篇加 `comments: false`）；列表排序会变；中文分类链接是百分号编码。

## 三、17 篇归类定稿（执行时现场重算核对）

| 篇目 | 处理 | 依据 |
|---|---|---|
| 卷积模块的张量表示及梯度推导 | **迁移** | 用户指定；张量推导长文 |
| mlp的张量表示及梯度推导 | **迁移** | 用户指定；张量推导长文 |
| 注意力模块的张量表示及梯度推导 | **迁移** | 用户指定；70KB 长文，缺席所有索引源，点名核验防漏 |
| esl第五章基展开和正则化 | **迁移** | 用户指定；统计学习笔记 |
| 深度学习理论笔记 | **迁移** | 用户指定；学习笔记 |
| 其余 12 篇（hugo个人博客搭建、hugo博客的数学公式问题、datamanagement、主页目录、mainpage、myfirstblog、test-chinese + 5 篇主题示例） | 跳过 | 未列入用户指定的主要迁移清单；留档 checklist，想补随时重跑脚本 |

## 四、成功标准

strict 构建通过；5 篇全部出现在博客列表且日期正确；公式渲染正常（对拍旧站）；`p/` 全集双向对账无遗漏；checklist 留档完整。
