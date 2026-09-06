# 后续需求：接入 giscus 评论区（2026-09-06）

- 分级：L1（原博客任务的直接延伸；用户在对话中批准方案：giscus + 官方 partial 配方）
- 结果：完成并上线验证

## 做了什么

1. API 开通 `Soflari/blog` 的 Discussions（评论数据存放地，选 Announcements 分类防灌水）；GraphQL 实查 repo ID 与分类 ID
2. 博客侧 4 处改动（commit `7c7d62c`）：`mkdocs.yml` 加 `custom_dir: overrides` 与 `meta` 插件；新建 `overrides/partials/comments.html`（Material 官方配方：giscus 脚本 + 亮暗色联动）；新建 `docs/blog/posts/.meta.yml` 批量开评论；README 补说明
3. 用户在网页安装 giscus app 并授权仓库（唯一无法代办的 OAuth 步骤）
4. 推送后 Actions 成功，线上验证：文章页 giscus iframe 正常渲染、评论区标题「评论」、组件不出现在非文章页

## 验证证据

- `uv run mkdocs build --strict` 退出码 0；giscus 脚本仅在两篇文章页出现（首页/列表页为 0）
- 独立复核 PASS（官方配方逐字对照、参数合理性、meta 机制、构建隔离五项全过）
- 线上：https://soflari.github.io/blog/blog/2026/09/06/hello-world/ 页面 `.giscus-frame` iframe 存在且已加载（zh-CN widget）
