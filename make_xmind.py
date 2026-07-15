"""Generate an editable .xmind file (modern JSON + legacy XML for max compatibility)."""
import json, zipfile, os, html

OUT = r"C:\Users\xuchen12\mindmap_overseas\海外整合营销中台.xmind"

# ---- tree (matches the source docx); color is set on the 3 main branches ----
TREE = {
    "title": "海外整合营销中台",
    "note": "目标：持续提升海外品牌影响力、渠道经营能力及业务增长",
    "children": [
        {"title": "Build · 体系建设", "color": "#2F80ED", "children": [
            {"title": "全球营销体系建设", "children": [
                {"title": "营销体系标准化"},
                {"title": "工具包与方法论"},
                {"title": "项目管理机制"},
                {"title": "跨部门协同"},
            ]},
        ]},
        {"title": "Growth · 业务增长", "color": "#EB5757", "children": [
            {"title": "IMC 整合营销与资源管理", "children": [
                {"title": "新品上市策略"},
                {"title": "品牌 Campaign"},
                {"title": "新店开业营销"},
                {"title": "营销预算管理"},
                {"title": "营销资源整合"},
            ]},
            {"title": "渠道增长与经营管理", "children": [
                {"title": "渠道体系搭建"},
                {"title": "增长策略制定"},
                {"title": "数据分析 & ROI 优化"},
                {"title": "运营方法论沉淀"},
            ]},
        ]},
        {"title": "Enable · 能力赋能", "color": "#27AE60", "children": [
            {"title": "会员体系建设", "children": [
                {"title": "APP 会员体系"},
                {"title": "数字化能力"},
                {"title": "会员机制规划"},
            ]},
            {"title": "营销能力建设", "children": [
                {"title": "海外业务支持"},
                {"title": "营销资源建设"},
                {"title": "跨部门协同赋能"},
            ]},
        ]},
    ],
}

_c = [0]
def nid():
    _c[0] += 1
    return f"topic{_c[0]:04d}xmindnode"

# ---------- modern content.json ----------
def style_for(depth, color):
    """Return an XMind topic style dict for the given depth/branch color."""
    if depth == 0:
        props = {"svg:fill": "#33475B", "fo:color": "#FFFFFF", "border-line-width": "0pt"}
    elif depth == 1:
        props = {"svg:fill": color, "fo:color": "#FFFFFF",
                 "border-line-color": color, "line-color": color, "fo:font-weight": "bold"}
    elif depth == 2:
        props = {"svg:fill": "#FFFFFF", "fo:color": "#1F2430",
                 "border-line-color": color, "border-line-width": "2pt", "line-color": color}
    else:
        props = {"svg:fill": "#F4F7FC", "fo:color": "#2A2F3A",
                 "border-line-color": color, "line-color": color}
    return {"id": nid(), "properties": props}

def to_json(node, depth=0, color=None):
    color = node.get("color", color)
    t = {"id": nid(), "class": "topic", "title": node["title"]}
    if color:
        t["style"] = style_for(depth, color)
    if node.get("note"):
        t["notes"] = {"plain": {"content": node["note"]},
                      "realHTML": {"content": f"<html><body><p>{html.escape(node['note'])}</p></body></html>"}}
    kids = node.get("children")
    if kids:
        t["children"] = {"attached": [to_json(k, depth + 1, color) for k in kids]}
    return t

root_json = to_json(TREE)
root_json["style"] = style_for(0, None)
root_json["structureClass"] = "org.xmind.ui.map.unbalanced"
content_json = [{
    "id": nid(), "class": "sheet", "title": "海外整合营销中台",
    "rootTopic": root_json,
    "theme": {"id": nid(), "class": "theme"},
}]

metadata_json = {"creator": {"name": "GitHub Copilot", "version": "1.0.0"}}
manifest_json = {"file-entries": {"content.json": {}, "metadata.json": {}, "Thumbnails/thumbnail.png": {}}}

# ---------- legacy content.xml (XMind 8) ----------
_c[0] = 0
def to_xml(node):
    tid = nid()
    title = html.escape(node["title"])
    inner = f"<title>{title}</title>"
    if node.get("note"):
        inner += f"<notes><plain>{html.escape(node['note'])}</plain></notes>"
    kids = node.get("children")
    if kids:
        inner += "<children><topics type=\"attached\">" + "".join(to_xml(k) for k in kids) + "</topics></children>"
    return f"<topic id=\"{tid}\">{inner}</topic>"

# root topic needs structure-class attr
_c[0] = 0
def root_to_xml(node):
    tid = nid()
    title = html.escape(node["title"])
    inner = f"<title>{title}</title>"
    if node.get("note"):
        inner += f"<notes><plain>{html.escape(node['note'])}</plain></notes>"
    kids = node.get("children")
    if kids:
        inner += "<children><topics type=\"attached\">" + "".join(to_xml(k) for k in kids) + "</topics></children>"
    return f"<topic id=\"{tid}\" structure-class=\"org.xmind.ui.map.unbalanced\">{inner}</topic>"

content_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
    '<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" '
    'xmlns:fo="http://www.w3.org/1999/XSL/Format" '
    'xmlns:svg="http://www.w3.org/2000/svg" '
    'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
    'xmlns:xlink="http://www.w3.org/1999/xlink" version="2.0">'
    f'<sheet id="{nid()}">{root_to_xml(TREE)}<title>海外整合营销中台</title></sheet>'
    '</xmap-content>'
)

meta_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
            '<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0"/>')

manifest_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
    '<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">'
    '<file-entry full-path="content.xml" media-type="text/xml"/>'
    '<file-entry full-path="content.json" media-type="application/json"/>'
    '<file-entry full-path="metadata.json" media-type="application/json"/>'
    '<file-entry full-path="META-INF/" media-type=""/>'
    '<file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/>'
    '</manifest>'
)

# ---------- write zip ----------
if os.path.exists(OUT):
    os.remove(OUT)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("content.json", json.dumps(content_json, ensure_ascii=False, indent=2))
    z.writestr("metadata.json", json.dumps(metadata_json, ensure_ascii=False, indent=2))
    z.writestr("manifest.json", json.dumps(manifest_json, ensure_ascii=False, indent=2))
    z.writestr("content.xml", content_xml)
    z.writestr("meta.xml", meta_xml)
    z.writestr("META-INF/manifest.xml", manifest_xml)

print("WROTE", OUT, os.path.getsize(OUT), "bytes")
# validate
with zipfile.ZipFile(OUT) as z:
    print("ENTRIES:", z.namelist())
    json.loads(z.read("content.json"))
    print("content.json OK, sheets:", len(content_json))
