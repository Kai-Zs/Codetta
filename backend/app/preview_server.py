"""临时数据库预览服务器 — python backend/app/preview_server.py"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import uvicorn
from app.database import get_conn

app = FastAPI()

HTML = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>练笔小筑 — 数据库预览</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Noto Sans SC",sans-serif;background:#FAF5FF;color:#1e1b4b;padding:16px}
h1{color:#7C3AED;margin-bottom:8px}
.bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.bar select,.bar input,.bar button{padding:6px 10px;border:1px solid #d4d4d8;border-radius:6px;font-size:14px}
.bar button{background:#7C3AED;color:#fff;border:none;cursor:pointer}
.stats{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.stat{background:#fff;border-radius:8px;padding:10px 16px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.stat b{color:#7C3AED}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.06)}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid #f4f4f5;font-size:13px}
th{background:#7C3AED;color:#fff;font-weight:600;position:sticky;top:0}
tr:hover{background:#faf5ff}
.tag{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600}
.tag-danxuan{background:#ede9fe;color:#7C3AED}
.tag-panduan{background:#dbeafe;color:#2563eb}
.tag-tiankong{background:#fef3c7;color:#d97706}
.tag-biancheng{background:#d1fae5;color:#059669}
.na{color:#a1a1aa}
pre{white-space:pre-wrap;max-width:400px;max-height:80px;overflow-y:auto;font-size:12px}
.pg{display:flex;gap:8px;align-items:center;margin-top:12px}
.pg button{padding:4px 12px}
.inactive{opacity:.4}
</style>
</head>
<body>
<h1>练笔小筑</h1>
<p style="color:#71717a;margin-bottom:12px">题库预览 · {{total}} 题（活跃 {{active}}）</p>
<div class="stats">
{{stats}}
</div>
<div class="bar">
<select onchange="apply()" id="type">
<option value="">全部题型</option>
<option value="单选题">单选题</option>
<option value="判断题">判断题</option>
<option value="填空题">填空题</option>
<option value="编程题">编程题</option>
</select>
<select onchange="apply()" id="chapter">
<option value="">全部章节</option>
</select>
<select onchange="apply()" id="active">
<option value="">全部状态</option>
<option value="1">仅活跃</option>
<option value="0">仅停用</option>
</select>
<input id="search" placeholder="搜索标题..." oninput="apply()">
<button onclick="reset()">重置</button>
</div>
<table>
<thead><tr>
<th>题号</th><th>题型</th><th>标题</th><th>答案/选项</th><th>代码</th>
</tr></thead>
<tbody id="tbody"></tbody>
</table>
<div class="pg">
<button onclick="go(-1)">上一页</button>
<span id="pageInfo"></span>
<button onclick="go(1)">下一页</button>
</div>

<script>
let page=1, totalPages=1;
const base="/api/rows";

function typeTag(t){
 const m={单选题:"danxuan",判断题:"panduan",填空题:"tiankong",编程题:"biancheng"};
 return `<span class="tag tag-${m[t]||'danxuan'}">${t}</span>`;
}
async function apply(p=1){page=p;
 let p2=document.getElementById("type").value;
 let q=document.getElementById("search").value;
 let ch=document.getElementById("chapter").value;
 let ac=document.getElementById("active").value;
 let url=`${base}?page=${page}&type=${encodeURIComponent(p2)}&q=${encodeURIComponent(q)}&chapter=${encodeURIComponent(ch)}&active=${encodeURIComponent(ac)}`;
 let r=await fetch(url); let d=await r.json();
 totalPages=d.pages;
 document.getElementById("pageInfo").textContent=`${d.total} 条 · 第 ${page}/${totalPages||1} 页`;
 let h="";
 for(let row of d.rows){
  let ans=row.answer||"";
  if(row.options){try{let o=JSON.parse(row.options);ans="<b>"+ans+"</b> · "+o.map(x=>x.replace(/</g,"&lt;")).join(" · ")}catch(e){}}
  else if(row.answer_parts){try{let p=JSON.parse(row.answer_parts);ans=p.join(" | ")}catch(e){}}
  let code="";
  if(row.template||row.answer_code){
   code=(row.template?"<b>模板（预填编辑器）:</b><pre>"+row.template.replace(/</g,"&lt;").substring(0,200)+"</pre>":"")+
        (row.answer_code?"<b>完整代码（判题用）:</b><pre>"+row.answer_code.replace(/</g,"&lt;").substring(0,300)+"</pre>":"");
  }
  let cls=row.is_active?"":" class=inactive";
  h+=`<tr${cls}><td>${row.q_number}</td><td>${typeTag(row.type)}</td><td>${row.title.replace(/</g,"&lt;")||"<span class=na>(无)</span>"}</td><td>${ans||"<span class=na>(无)</span>"}</td><td>${code||"<span class=na>-</span>"}</td></tr>`;
 }
 document.getElementById("tbody").innerHTML=h||"<tr><td colspan=5 style=text-align:center;color:#a1a1aa>无匹配结果</td></tr>";
}
function go(d){let np=page+d; if(np>=1&&np<=totalPages) apply(np);}
function reset(){document.getElementById("type").value="";document.getElementById("chapter").value="";document.getElementById("search").value="";document.getElementById("active").value="";apply(1);}
(async function(){
 let r=await fetch("/api/chapters"); let chs=await r.json();
 let sel=document.getElementById("chapter");
 for(let c of chs){let o=document.createElement("option");o.value=c;o.textContent="第"+c+"章";sel.appendChild(o)}
 let params=new URLSearchParams(location.search);
 if(params.get("type")) document.getElementById("type").value=params.get("type");
 apply(1);
})();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM questions WHERE is_active=1").fetchone()[0]
    types = conn.execute("SELECT type, COUNT(*) FROM questions WHERE is_active=1 GROUP BY type").fetchall()
    conn.close()
    stats = "".join(
        f'<div class="stat"><b>{t}</b> {c} 道</div>'
        for t, c in types
    )
    return HTML.replace("{{total}}", str(total)).replace("{{active}}", str(active)).replace("{{stats}}", stats)


@app.get("/api/rows")
def api_rows(
    page: int = Query(1),
    type: str = Query(""),
    chapter: str = Query(""),
    active: str = Query(""),
    q: str = Query(""),
):
    conn = get_conn()
    where = ["1=1"]
    params = []
    if type:
        where.append("type=?")
        params.append(type)
    if chapter:
        where.append("chapter=?")
        params.append(chapter)
    if active:
        where.append("is_active=?")
        params.append(int(active))
    if q:
        where.append("title LIKE ?")
        params.append(f"%{q}%")

    w = " AND ".join(where)
    total = conn.execute(f"SELECT COUNT(*) FROM questions WHERE {w}", params).fetchone()[0]
    per = 20
    pages = (total + per - 1) // per
    offset = (page - 1) * per
    rows = conn.execute(
        f"SELECT q_number, type, title, answer, options, answer_parts, template, answer_code, is_active FROM questions WHERE {w} ORDER BY id LIMIT ? OFFSET ?",
        params + [per, offset]
    ).fetchall()
    conn.close()
    return {
        "total": total,
        "pages": pages,
        "rows": [
            {
                "q_number": r["q_number"],
                "type": r["type"],
                "title": r["title"],
                "answer": r["answer"],
                "options": r["options"],
                "answer_parts": r["answer_parts"],
                "template": r["template"],
                "answer_code": r["answer_code"],
                "is_active": r["is_active"],
            }
            for r in rows
        ],
    }


@app.get("/api/chapters")
def api_chapters():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT chapter FROM questions ORDER BY CAST(chapter AS INTEGER)").fetchall()
    conn.close()
    return [r["chapter"] for r in rows]


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
