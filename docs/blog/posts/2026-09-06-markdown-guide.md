---
date: 2026-09-06
slug: markdown-guide
categories:
  - 教程
tags:
  - Markdown
  - 写作
authors:
  - me
---

# 写作语法指南

这篇文章演示本站支持的主要写作语法，写新文章时可以当模板抄。

## 文字格式

**加粗**、*斜体*、`行内代码`、~~删除线~~、==高亮==、H~2~O 下标、x^2^ 上标。

[外部链接](https://squidfunk.github.io/mkdocs-material/)会自动识别，站内链接示例：[回到首页](../../index.md)。

## 列表

无序列表：

- 第一项
- 第二项
    - 嵌套项

有序列表：

1. 第一步
2. 第二步

任务列表：

- [x] 已完成的事
- [ ] 待办的事

## 表格

| 列一 | 列二 | 列三 |
|---|---|---|
| 内容 | 内容 | 内容 |
| 内容 | 内容 | 内容 |

## 代码块

带语法高亮和行号，右上角有一键复制按钮：

```python
def fibonacci(n: int):
    """生成斐波那契数列前 n 项。"""
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

print(fibonacci(10))
```

行内高亮：`print("hello")` 中的 `print` 也可以写成 `:::python print`。

## 提示框

!!! note "说明"
    这是一条说明。类似的还有 `tip`（技巧）、`warning`（警告）、`danger`（危险）。

??? tip "可折叠内容（点击展开）"
    折叠块适合放长代码或补充细节，默认收起，不占版面。

## 选项卡

=== "方法一"

    第一种做法的说明或代码。

=== "方法二"

    第二种做法的说明或代码。

## 数学公式

行内公式：质能方程 $E = mc^2$ 出现在句子中间。

块级公式单独成行并居中：

$$
\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}
$$

多行对齐环境：

$$
\begin{aligned}
\nabla \cdot \mathbf{E} &= \frac{\rho}{\varepsilon_0} \\
\nabla \cdot \mathbf{B} &= 0
\end{aligned}
$$

写法要点：行内用 `$...$`，块级用 `$$...$$`，都由 MathJax 渲染。

## 图片

图片语法如下（本站未内置示例图片，实际使用时把 `图片路径或URL` 换成真实地址，站内图片建议放在 `docs/assets/` 下）：

```markdown
![图片替代文字](图片路径或URL)
```

## 脚注与其他

脚注示例[^1]。

[^1]: 脚注内容出现在页面底部。

缩写示例（鼠标悬停看提示）：HTML 是一种标记语言。

*[HTML]: HyperText Markup Language
