---
date: 2026-09-06
categories:
  - 公告
tags:
  - 开始
authors:
  - me
slug: hello-world
---

# 你好，世界

这是本博客的第一篇示例文章，用来说明文章的基本写法。写正式文章时可以直接把它替换掉。

## 文章放在哪里

所有文章放在 `docs/blog/posts/` 目录下，文件名建议用「日期-标题缩写」的格式，例如：

```
docs/blog/posts/2026-09-06-hello-world.md
```

## 文章开头的元数据

每篇文章顶部有一段 YAML「front matter」，用来声明日期、分类、标签和作者：

```yaml
---
date: 2026-09-06
categories:
  - 公告
tags:
  - 开始
authors:
  - me
---
```

- `date`：发布日期，博客首页按它倒序排列
- `categories`：分类，出现在归档与分类视图
- `tags`：标签，点击可跳到同标签文章列表
- `authors`：作者，对应 `docs/blog/.authors.yml` 里定义的条目

## 公式演示

行内公式这样写：$e^{i\pi} + 1 = 0$。

块级公式这样写：

$$
\hat{\theta} = \arg\min_{\theta} \sum_{i=1}^{n} \left( y_i - f_\theta(x_i) \right)^2
$$

更多写法（代码块、提示框、表格、选项卡等）见下一篇文章《写作语法指南》。
