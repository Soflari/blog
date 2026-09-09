# 迁移清单（checklist）

任务：Hugo 博客文章迁移（2026-09-08）。迁移源 `Soflari/hugo_dev`（纯构建产物仓库）。详见同目录 intent.md / plan.md / audit.json。

## 一、跳过的文章及理由（p/ 全集 17 = 迁移 5 + 跳过 12）

用户指定主要迁移 5 篇（白名单），其余 12 篇未列入即跳过。日后想补：找到对应 `p/<slug>/index.html`，把 slug 加进 `migrate.py` 的 `WHITE_LIST` 重跑即可（已迁移篇按 `source_permalink` 锚点幂等覆盖）。

| 篇目 | 处理 | 说明 |
|---|---|---|
| 卷积模块的张量表示及梯度推导 | 迁移 | 2025-11-17，块 21 / 行内 131 公式，1 图 |
| mlp的张量表示及梯度推导 | 迁移 | 2025-11-17，块 21 / 行内 31 公式，1 代码块 |
| 注意力模块的张量表示及梯度推导 | 迁移 | 2025-11-16，块 39 / 行内 131 公式，2 代码块；缺席所有索引源，已点名核验防漏 |
| esl第五章基展开和正则化 | 迁移 | 2025-06-13，块 2 / 行内 11 公式 |
| 深度学习理论笔记 | 迁移 | 2025-06-12，块 2 / 行内 7 公式 |
| hugo个人博客搭建 / hugo博客的数学公式问题 / datamanagement / 主页目录 / mainpage / myfirstblog / test-chinese | 跳过 | 未列入用户指定清单（其中 mainpage 与 主页目录 互为重复） |
| markdown-syntax-guide / placeholder-text / math-typesetting / emoji-support / migrate-from-jekyl | 跳过 | Hugo 主题自带示例文章 |

## 二、待人工处理项

无阻塞项。执行中的断言全部通过（公式逐字节在场、token 清零、标题一致、日期格式）。以下为知悉类：

- [知悉] 旧站标签（tags/categories）在产物页面无 meta、无 RSS 字段、页脚标签区无链接可挖，迁移文章的 `tags`/`categories` 留空——想加的话编辑各篇 front matter。
- [知悉] 逆向必有损耗：建议抽空浏览器过目 5 篇（本地 `uv run mkdocs serve`），与旧站 https://soflari.github.io/hugo_dev/ 对拍。
- [知悉] 卷积篇正文有一处孤字「扩」（第 69 行附近），旧站源 HTML 即如此（未写完的句子），按内容保真原则保留，可自行补全或删除。

## 三、需过目篇目 + provenance（全部 5 篇均来自 `p/<slug>/index.html` 页面解析）

| 篇目 | provenance | 转换要点 |
|---|---|---|
| 卷积模块的张量表示及梯度推导 | 页面 HTML | 图片 1 张（pics/Pasted_image_20251113124916.png → docs/assets/卷积…/） |
| mlp的张量表示及梯度推导 | 页面 HTML | 15 处列表内块公式转 `$\displaystyle …$` 行内形态（换行压平 10 处，LaTeX 语义等价）；代码块 1 个（python） |
| 注意力模块的张量表示及梯度推导 | 页面 HTML | 33 处列表内块公式转 displaystyle 形态；「Softmax 雅可比」一节的 Case 1/2/组合 子列表拍平为段落（Python-Markdown 对深层嵌套列表解析不可靠，拍平防公式变代码块）；代码块 2 个（python） |
| esl第五章基展开和正则化 | 页面 HTML | 无特殊处理 |
| 深度学习理论笔记 | 页面 HTML | 无特殊处理 |

排版说明：列表内的块公式以行内 displaystyle 形态渲染——但经 2026-09-08 公式排版优化后，「纯公式段落居中」CSS 规则使其居中独占行（观感等同块公式），公式内容逐字节未动。曾评估 raw HTML div 路线（让 li 内公式走原生块通道），实测 Python-Markdown 松散列表存在解析窗口死锁：div 缩进相对列表内容列 <4 时作为懒惰续行并入前段（公式被 inline 处理器二次解析损毁，实测 11 处）；≥4 时又落进缩进代码块——53 处无一安全窗口，放弃该路线（详见对话记录与 2026-09-08 公式排版方案评审）。最终方案：md 保持 displaystyle 形态 + 公式行前后补空行独立成段 + `docs/stylesheets/extra.css` 的 `p:has(> span.arithmatex:only-child)` 居中规则。

## 四、待补日期与标签

无待补日期（5 篇 time 标签均为纯日期 `YYYY-MM-DD`，直接采用）。标签见「二」。

## 附：源稿探测留档（为什么走网页逆向）

- GitHub API：hugo_dev 默认分支 34 个提交的 path 探测（content/、config.toml、hugo.toml、archetypes/、assets/）计数全 0——仓库历史上从未提交过源稿；首提交（2025-06-07）树 286 条路径全为构建产物。
- `git ls-remote --heads --tags`：仅 `refs/heads/main`，无额外分支/tag。
- 用户公开 events（90 天窗口）、gists：无源码仓库信号（窗口不覆盖活跃期，仅无正向信号）。
- 本机：`C:\Program Files\programme\` 同级目录、Desktop/Documents/Downloads、hugo 命令均无源稿。全阴性 → 走网页逆向。批准门已问过用户源稿位置，未提供。
