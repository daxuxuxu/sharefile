# 思维导图生成套件（XMind 风格 PNG + 可编辑 .xmind）

> 本仓库是一套**从「树状结构数据」一键生成两种产物**的脚本：
> 1. **XMind 风格 PNG 图片**（HTML + SVG 自动排版 → 浏览器截图）
> 2. **可编辑的 `.xmind` 文件**（新旧格式双打包，XMind 8 / XMind 2020+ 都能打开）
>
> 当前示例内容是「海外整合营销中台」组织脑图，但**换任意树状内容都能复用**。

---

## 🤖 给 AI Model 的 30 秒上手指南

要改内容，你**只需要动两个文件里的一个数据对象**，其余全自动：

| 想改什么 | 改哪里 |
|---|---|
| PNG 图片的内容 | [`xmind_doc.html`](xmind_doc.html) 里的 `const DATA = { ... }` |
| `.xmind` 文件的内容 | [`make_xmind.py`](make_xmind.py) 里的 `TREE = { ... }` |

两个数据结构**完全对应**，改内容时请**同步改这两处**（见下方「保持同步」）。改完按「重新生成」章节各跑一次即可。

---

## 文件清单

| 文件 | 作用 | 产物 |
|---|---|---|
| `xmind_doc.html` | 数据 `DATA` → SVG 自动树布局 + 锥形曲线分支 | 在浏览器里渲染，截图得 PNG |
| `make_xmind.py` | 数据 `TREE` → 打包 `.xmind`（zip） | `海外整合营销中台.xmind` |
| `parse_docx.py` | 解析 `.docx`，打印段落/样式/表格，用于从文档提结构 | 终端输出 |
| `xmind_doc.png` | 标准分辨率成品图（1590×1481） | — |
| `xmind_doc@2x.png` | 2× 高清成品图（3180×2962） | — |
| `海外整合营销中台.xmind` | 可编辑思维导图文件 | — |

---

## 数据结构（两文件通用）

一个节点 = `{ name/title, 可选 color, 可选 children[] }`。三层含义：

- **根节点**：整张图的中心主题
- **一级子节点**（depth 1）：主分支，**在这里设 `color`**，颜色会自动沿子孙传播
- **更深层**：分组 / 叶子

`xmind_doc.html` 用 `name`，`make_xmind.py` 用 `title`，字段名不同但结构一致：

```js
// xmind_doc.html
const DATA = {
  name: "根主题",
  children: [
    { name: "分支A", tag: "A", color: "#2F80ED", children: [
      { name: "分组", children: [ {name:"叶子1"}, {name:"叶子2"} ] }
    ]},
  ]
};
```

```python
# make_xmind.py
TREE = {
  "title": "根主题",
  "note": "根节点备注（可选，会写进 .xmind 的 notes）",
  "children": [
    {"title": "分支A", "color": "#2F80ED", "children": [
      {"title": "分组", "children": [ {"title": "叶子1"}, {"title": "叶子2"} ]}
    ]},
  ],
}
```

### 保持同步
两份数据要表达同一棵树。改内容时：
- `name` ↔ `title` 一一对应
- `color` 只加在一级分支上（两边都加，颜色才一致）
- `xmind_doc.html` 里的 `tag`（如 BUILD/GROWTH）仅用于图片显示，`.xmind` 不需要

---

## 重新生成 PNG 图片

`xmind_doc.html` 打开即用 JS 自动测量文字宽度、计算树布局、画出 SVG，无需构建。

**方式一（手动）**：用浏览器打开 `xmind_doc.html`，对 `#wrap` 元素截图。

**方式二（自动，Playwright）**：
```js
// 标准图：截 #wrap 元素
const el = await page.$('#wrap');
await el.screenshot({ path: 'xmind_doc.png' });

// 2× 高清图：整页缩放后全页截图（勿用 element.screenshot，超大+transform 会 not stable 超时）
await page.reload();
const d = await page.evaluate(() => {
  const w = document.getElementById('wrap');
  const sw = w.scrollWidth, sh = w.scrollHeight;
  w.style.transform = 'scale(2)'; w.style.transformOrigin = 'top left';
  document.body.style.width = sw*2+'px'; document.body.style.height = sh*2+'px';
  return { w: sw*2, h: sh*2 };
});
await page.setViewportSize({ width: Math.min(d.w, 4000), height: 1000 });
await page.screenshot({ path: 'xmind_doc@2x.png', fullPage: true });
```

### 布局原理（想改样式时看这里）
- **y 坐标**：叶子按行依次排（`ROW` 行高）；父节点 y = 首尾子节点 y 的中点
- **x 坐标**：按 `depth` 在 `COLS` 数组里取固定列
- **分支线**：XMind 手感来自「锥形填充路径」——父端粗（~10px）、子端细（~2.4px），贝塞尔控制点在两端中点 `midX`
- **框宽**：用 canvas `measureText` 实测文字宽度 + 内边距，自动定宽
- 想调间距/字号/配色：改顶部的 `COLS / ROW / H / FS / PADX` 常量

---

## 重新生成 .xmind

```powershell
# Windows / uv（推荐，隔离环境）
uv run --python 3.12 python make_xmind.py
# 或任意装了标准库的 Python 3 即可（脚本只用 json/zipfile/os/html，无第三方依赖）
python make_xmind.py
```

输出 `海外整合营销中台.xmind`，脚本末尾会自动读回校验（列出 zip 条目 + 解析 content.json）。

### .xmind 格式原理（给 model 的关键知识）
`.xmind` 本质是个 **zip**。为兼容新旧版本，本脚本在同一个 zip 里**同时打包两套格式**：

- **现代格式（XMind 2020+）**：`content.json` + `metadata.json` + `manifest.json`
- **旧版格式（XMind 8）**：`content.xml` + `meta.xml` + `META-INF/manifest.xml`

`content.json` 是一个 sheet 数组，核心结构：
```jsonc
[{
  "id": "...", "class": "sheet", "title": "根主题",
  "rootTopic": {
    "id": "...", "class": "topic", "title": "根主题",
    "structureClass": "org.xmind.ui.map.unbalanced",   // 经典 map 布局
    "style": { "id": "...", "properties": { "svg:fill": "#33475B", "fo:color": "#FFFFFF" } },
    "notes": { "plain": { "content": "备注文字" } },
    "children": { "attached": [ /* 递归的 topic */ ] }
  }
}]
```

**分支配色**：给 topic 加 `style.properties`：
```jsonc
"style": { "id": "<唯一id>", "properties": {
  "svg:fill": "#2F80ED",        // 填充色
  "fo:color": "#FFFFFF",        // 文字色
  "border-line-color": "#2F80ED",
  "line-color": "#2F80ED"       // 分支线色
}}
```
> XMind 会**忽略不认识的属性**，所以加样式很安全，不会导致文件打不开。颜色应沿主分支往子孙传播。

---

## 从 .docx / 图片提取结构

- **docx**：改 `parse_docx.py` 里的路径后运行，它会按段落打印文本 + 样式名 + 列表层级（`ilvl`）+ 表格，方便你把文档还原成 `TREE`。依赖 `python-docx`：
  ```powershell
  uv run --python 3.12 --with python-docx python parse_docx.py
  ```
- **GitHub 上的中文文件名**：用 `raw.githubusercontent.com/<user>/<repo>/<branch>/<URL编码后的文件名>` 下载。

---

## 常见坑（踩过的）

- **`element.screenshot` 超时 `not stable`**：内容超大或带 `transform` 时会卡。→ 改用整页 `page.screenshot({fullPage:true})`。
- **`git push` 返回 exit code 1 但其实成功**：PowerShell 把 git 的进度输出（stderr）当报错。看到 `-> main` 就是成功了，用 `git ls-remote --heads origin` 核对 commit 号确认。
- **中文 `print` 崩 UnicodeEncodeError**：终端先设 `$env:PYTHONUTF8=1`。
- **改了内容图片没变**：`xmind_doc.html` 是纯前端渲染，浏览器需重新加载页面（`page.reload()`）。

---

## License / 用途

内容示例仅供演示，脚本可自由复用、修改、二次生成。
