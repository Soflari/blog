r"""Hugo 构建产物 → MkDocs 文章迁移脚本（一次性，留档可复跑）。

用法：TMPDIR 指向 clone 根目录的环境变量形式：
    uv run --with beautifulsoup4,markdownify python migrate.py <clone目录> <博客仓库根>
产物：docs/blog/posts/<date>-<slug>.md、docs/assets/<slug>/、本目录 audit.json

设计要点（全部来自 2026-09-08 实测，详见同目录 plan.md）：
- 公式占位符法：DOM 文本节点上抠 $..$/$$..$$（跳过 code/pre 等），markdownify 后回填，
  公式零经过转换器，防 markdownify 的转义与空白规整损伤 LaTeX。
- li 内块公式：实测本站 arithmatex 不处理列表内 $$（裸残留），改写为
  $\displaystyle ...$（行内通道保真渲染，换行压平为空格——LaTeX 语义等价）。
- 段落级块公式：$$..$$ 独立成段（前后空行），实测 \\ 与 & 保真。
"""
import json
import os
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString
from markdownify import MarkdownConverter

WHITE_LIST = [
    "卷积模块的张量表示及梯度推导",
    "mlp的张量表示及梯度推导",
    "注意力模块的张量表示及梯度推导",
    "esl第五章基展开和正则化",
    "深度学习理论笔记",
]
IGNORE_TAGS = {"script", "noscript", "style", "textarea", "pre", "code", "option"}
BASE_PREFIX = "/hugo_dev"

BLOCK_RE = re.compile(r"[$][$].*?[$][$]", re.S)
INLINE_RE = re.compile(r"(?<![$])[$][^$\n]+[$](?![$])")

FAILS = []


def normalize_href(href: str) -> str | None:
    """RSS/正文里混杂的链接 → 仓库相对路径；不识别返回 None。"""
    if not href or href.startswith("#") or href.startswith("mailto:"):
        return None
    path = urllib.parse.urlsplit(href).path
    path = urllib.parse.unquote(path)
    if path.startswith(BASE_PREFIX):
        path = path[len(BASE_PREFIX):]
    return path


def post_url(path: str) -> str | None:
    """归一化后形如 /p/<slug>/ 的文章链接 → slug。"""
    m = re.fullmatch(r"/p/([^/]+)/?", path)
    return m.group(1) if m else None


def code_language(el):
    for c in el.get("class") or []:
        if c.startswith("language-"):
            return c[len("language-"):]
    return ""


def extract_math(art, raw_html: str):
    """占位替换正文文本节点里的公式，返回占位表 [(token, formula, kind, in_li)]。"""
    placeholders = []
    seq = 0

    def sub_blocks(text):
        nonlocal seq

        def repl(m):
            nonlocal seq
            formula = m.group(0)
            tok = f"zMATHz{seq:04d}zMATHz"
            seq += 1
            assert tok not in raw_html, f"token 碰撞: {tok}"
            placeholders.append((tok, formula, "block", in_li))
            return f" {tok} "

        return BLOCK_RE.sub(repl, text)

    def sub_inline(text):
        nonlocal seq

        def repl(m):
            nonlocal seq
            formula = m.group(0)
            tok = f"zMATHz{seq:04d}zMATHz"
            seq += 1
            assert tok not in raw_html, f"token 碰撞: {tok}"
            placeholders.append((tok, formula, "inline", in_li))
            return f" {tok} "

        return INLINE_RE.sub(repl, text)

    strings = [
        s for s in art.descendants
        if isinstance(s, NavigableString)
        and not any(p.name in IGNORE_TAGS for p in s.parents if p.name)
    ]
    for s in strings:
        in_li = s.find_parent("li") is not None
        s.replace_with(sub_inline(sub_blocks(str(s))))
    return placeholders


def expected_math_count(art) -> tuple[int, int]:
    """占位前的全文公式计数（跨节点视角），用于与节点级抠出数对账。"""
    text = art.get_text()
    blocks = len(BLOCK_RE.findall(text))
    stripped = BLOCK_RE.sub(lambda m: " ", text)
    inlines = len(INLINE_RE.findall(stripped))
    return blocks, inlines


def flatten_deep_lists(art):
    """嵌套深度 ≥2 的子列表（列表的列表的列表）拍平为父项内段落序列。

    实测 Python-Markdown 对 markdownify 输出的深层嵌套列表缩进解析不可靠
    （注意力篇 Case 1 区被误判为缩进代码块，且好坏与缩进量的关系是路径
    依赖的，无法靠调缩进根治）。拍平后是「列表项内的普通段落」，解析稳定；
    子项文本（Case 1: 等前缀）保留，信息无损。"""
    from bs4 import Tag
    changed = True
    while changed:
        changed = False
        for lst in art.find_all(["ul", "ol"]):
            anc, depth = lst.parent, 0
            while anc is not None and getattr(anc, "name", None):
                if anc.name in ("ul", "ol"):
                    depth += 1
                anc = anc.parent
            if depth < 2:
                continue
            new_paras = []
            for li in lst.find_all("li", recursive=False):
                inline = [c.extract() for c in list(li.children)
                          if not (isinstance(c, Tag) and c.name in
                                  ("p", "ul", "ol", "pre", "div", "blockquote", "table"))]
                if inline and any(getattr(c, "strip", lambda: True)() for c in inline):
                    p = BeautifulSoup("<p></p>", "html.parser").p
                    for c in inline:
                        p.append(c)
                    new_paras.append(p)
                for c in li.children:
                    new_paras.append(c.extract())
            for p in new_paras:
                lst.insert_before(p)
            lst.decompose()
            changed = True
            break


def convert_article(clone: Path, slug: str, dates: dict, posts_dir: Path, assets_dir: Path, audit: dict):
    page = clone / "p" / slug / "index.html"
    raw_html = page.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw_html, "html.parser")

    title = soup.title.get_text(strip=True)
    og = soup.find("meta", property="og:title")
    og_title = og.get("content") if og else None
    assert og_title in (None, title), f"{slug}: og:title 不一致: {og_title!r} vs {title!r}"
    assert not re.search(r"[·|—]", title), f"{slug}: title 疑似带站名后缀: {title!r}"

    time_el = soup.find("time", class_="article-time--published")
    assert time_el is not None, f"{slug}: 无 time.article-time--published"
    date = time_el.get_text(strip=True)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", date), f"{slug}: 日期异常: {date!r}"

    art = soup.find("section", class_="article-content")
    assert art is not None, f"{slug}: 无 article-content"

    # 深层嵌套列表拍平（防 Python-Markdown 误判为代码块）
    flatten_deep_lists(art)

    # 代码块：Chroma 行号布局（div.highlight>table.lntable 双 td）整体占位，
    # 取代码列内容，markdownify 后回填 fenced 原文（代码零经过转换器）
    code_ph = []
    for n, hl in enumerate(list(art.find_all("div", class_="highlight"))):
        lnt = hl.find("table", class_="lntable")
        if lnt is not None:
            tds = lnt.find_all("td")
            code_el = (tds[-1].find("code") if tds else None) or hl.find("code")
        else:
            code_el = hl.find("code")
        assert code_el is not None, f"{slug}: highlight 结构异常"
        lang = code_language(code_el)
        code_text = code_el.get_text().rstrip("\n")
        fenced = f"```{lang}\n{code_text}\n```"
        tok = f"zCODEz{n:04d}zCODEz"
        assert tok not in raw_html, f"token 碰撞: {tok}"
        code_ph.append((tok, fenced))
        hl.replace_with(NavigableString(f"\n{tok}\n"))

    # 图片：拷贝 page bundle 资源、改写引用、删多分辨率属性
    img_count = 0
    for im in art.find_all("img"):
        src = normalize_href(im.get("src") or "")
        assert src, f"{slug}: img src 无法归一化: {im.get('src')!r}"
        repo_file = clone / src.lstrip("/")
        assert repo_file.is_file(), f"{slug}: 图片不存在: {repo_file}"
        dest = assets_dir / slug
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo_file, dest / repo_file.name)
        im["src"] = f"../../assets/{slug}/{repo_file.name}"
        if not im.get("alt"):
            im["alt"] = ""
        for attr in ("srcset", "sizes", "loading", "decoding", "onerror"):
            if attr in im.attrs:
                del im[attr]
        img_count += 1

    # 正文内链：白名单内互链 → 指向目标 .md 源文件（MkDocs 自动重写 URL）
    link_rewrites = []
    for a in art.find_all("a"):
        slug2 = post_url(normalize_href(a.get("href") or ""))
        if slug2 and slug2 in dates:
            a["href"] = f"{dates[slug2]}-{slug2}.md"
            link_rewrites.append(slug2)

    # 公式占位（在链接/图片处理之后，对最终 DOM 做）
    exp_block, exp_inline = expected_math_count(art)
    placeholders = extract_math(art, raw_html)
    act_block = sum(1 for _, _, k, _ in placeholders if k == "block")
    act_inline = sum(1 for _, _, k, _ in placeholders if k == "inline")
    assert (exp_block, exp_inline) == (act_block, act_inline), (
        f"{slug}: 公式对账不符 期望块{exp_block}/行内{exp_inline} "
        f"实际块{act_block}/行内{act_inline}（可能有跨标签公式，转人工）")

    md = MarkdownConverter(
        heading_style="ATX", bullets="-",
        escape_asterisks=False, escape_underscores=False, escape_misc=False,
        code_language=code_language,
    ).convert_soup(art).strip()

    # 回填
    flatten_count = 0
    warnings = []
    for tok, formula, kind, in_li in placeholders:
        if kind == "block":
            content = formula[2:-2]
            if in_li:
                flat = re.sub(r"\s*\n\s*", " ", content).strip()
                if flat != content.strip():
                    flatten_count += 1
                new = "$\\displaystyle " + flat + "$"
            else:
                new = formula
                idx = md.find(tok)
                assert idx >= 0, f"{slug}: token 丢失: {tok}"
                if idx > 0 and not md[:idx].endswith("\n\n"):
                    new = "\n\n" + new
                tail = idx + len(tok)
                if tail < len(md) and not md[tail:].startswith("\n\n"):
                    new = new + "\n\n"
            check = flat if in_li else content
            md = md.replace(tok, new)
        else:
            content = formula[1:-1]
            if content != content.strip():
                warnings.append(f"行内公式内侧有空白: {formula[:40]}…")
            check = formula
            md = md.replace(tok, formula)
        assert check in md, f"{slug}: 公式串不在最终 Markdown: {check[:50]}…"

    left = sum(md.count(t) for t, _, _, _ in placeholders)
    assert left == 0, f"{slug}: token 回填残留 {left} 处"

    # 深缩进悬空段落顶格：PM 对 ≥4 空格缩进、未被列表吸收的行一律判为
    # 缩进代码块（拍平段落会被打成代码块），顶格后是普通段落，公式可渲染。
    # 在代码块回填前执行，fenced 内容（还是 token）不受影响。
    fence = False
    fixed = []
    for line in md.split("\n"):
        if "zCODEz" in line:
            fixed.append(line)
            continue
        if not line.strip():
            fixed.append(line)
            continue
        if not re.match(r"\s*([-*+]|\d{1,3}[.)])\s", line):
            ind = len(line) - len(line.lstrip())
            fixed.append(line.lstrip() if ind >= 4 else line)
        else:
            fixed.append(line)
    md = "\n".join(fixed)

    # 代码块回填（fenced 必须独立成块：前后空行）
    for tok, fenced in code_ph:
        idx = md.find(tok)
        assert idx >= 0, f"{slug}: 代码 token 丢失: {tok}"
        new = fenced
        if idx > 0 and not md[:idx].endswith("\n\n"):
            new = "\n\n" + new
        tail = idx + len(tok)
        if tail < len(md) and not md[tail:].startswith("\n\n"):
            new = new + "\n\n"
        md = md.replace(tok, new)
        assert fenced in md, f"{slug}: fenced 代码不在最终 Markdown"
    assert not any(md.count(t) for t, _ in code_ph), f"{slug}: 代码 token 残留"

    # 表格行内公式检测（| 是 Markdown 表格语法，会切断表格）
    for line in md.splitlines():
        if line.lstrip().startswith("|") and re.search(r"[$]\\displaystyle|[$][$]", line):
            warnings.append(f"表格行含公式（可能切断表格，需人工过目）: {line[:60]}…")

    front = (
        "---\n"
        f"date: {date}\n"
        f"slug: {slug}\n"
        "authors:\n"
        "  - me\n"
        f"source_permalink: 'hugo_dev:p/{slug}/'\n"
        "---\n\n"
    )
    out = posts_dir / f"{date}-{slug}.md"
    out.write_text(front + f"# {title}\n\n{md}\n", encoding="utf-8")

    audit[slug] = {
        "date": date, "title": title, "file": out.name,
        "公式_块": act_block, "公式_块_li内": sum(1 for _, _, k, li in placeholders if k == "block" and li),
        "公式_行内": act_inline, "换行压平数": flatten_count,
        "图片": img_count, "内链改写": link_rewrites, "代码块": len(code_ph), "warnings": warnings,
    }
    print(f"OK {slug}: date={date} 块{act_block}(li内{audit[slug]['公式_块_li内']}) 行内{act_inline} "
          f"图{img_count} 链{len(link_rewrites)} 码{len(code_ph)} 压平{flatten_count} warn{len(warnings)}")


def main():
    clone = Path(sys.argv[1]).resolve()
    repo = Path(sys.argv[2]).resolve()
    here = Path(__file__).parent
    posts_dir = repo / "docs" / "blog" / "posts"
    assets_dir = repo / "docs" / "assets"

    # 第一遍：收集白名单日期（内链改写需要目标文件名）
    dates = {}
    for slug in WHITE_LIST:
        soup = BeautifulSoup((clone / "p" / slug / "index.html").read_text(encoding="utf-8"), "html.parser")
        dates[slug] = soup.find("time", class_="article-time--published").get_text(strip=True)

    audit = {}
    for slug in WHITE_LIST:
        convert_article(clone, slug, dates, posts_dir, assets_dir, audit)

    (here / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\naudit.json 已写入，共 {len(audit)} 篇")


if __name__ == "__main__":
    main()
