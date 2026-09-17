#!/usr/bin/env python3
"""A dependency-free, single-file HTTP file browser."""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import shutil
import sys
import tempfile
import urllib.parse
from datetime import datetime
from email.parser import BytesParser
from email.policy import default as email_policy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

VERSION = "1.1.1"

INDEX_HTML = r'''<!doctype html>
<html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Simple File Browser</title><style>
:root{--bg:#f3f6fa;--panel:#fff;--line:#dbe3ec;--text:#17212b;--muted:#687787;--blue:#1677ff;--blue2:#eaf3ff;--danger:#d9363e;--shadow:0 7px 28px #24405d18}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}button,input{font:inherit}.app{min-height:100vh}.top{height:58px;background:#172b4d;color:#fff;display:flex;align-items:center;padding:0 22px;gap:12px;box-shadow:0 2px 10px #0003}.logo{width:31px;height:31px;border-radius:8px;background:linear-gradient(145deg,#40a9ff,#096dd9);display:grid;place-items:center;font-size:18px}.top strong{font-size:16px}.top .status{margin-left:auto;color:#cbd7e7;font-size:12px}.layout{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:calc(100vh - 58px)}aside{padding:16px 10px;background:#fff;border-right:1px solid var(--line);overflow:auto;max-height:calc(100vh - 58px)}.tree{min-width:0}.tree-row{display:flex;align-items:center;height:34px;border-radius:7px;white-space:nowrap}.tree-row:hover{background:#f5f9ff}.tree-row.active{background:var(--blue2);color:var(--blue);font-weight:650}.tree-toggle,.tree-name{border:0;background:none;cursor:pointer;color:inherit;padding:0}.tree-toggle{width:22px;min-width:22px;height:30px;color:var(--muted)}.tree-spacer{width:22px;min-width:22px}.tree-name{min-width:0;overflow:hidden;text-overflow:ellipsis;text-align:left;padding:6px 8px 6px 2px;flex:1}.main{padding:22px 26px;min-width:0}.crumbs{display:flex;align-items:center;gap:5px;min-height:33px;overflow:auto;white-space:nowrap}.crumbs button{border:0;background:none;color:var(--blue);cursor:pointer;padding:4px}.bar{display:flex;gap:8px;align-items:center;margin:12px 0}.btn{border:1px solid var(--line);background:#fff;border-radius:7px;padding:8px 12px;cursor:pointer;color:var(--text)}.btn:hover{border-color:#8abfff;color:var(--blue)}.primary{background:var(--blue);border-color:var(--blue);color:white}.primary:hover{color:white;background:#096dd9}.search{margin-left:auto;min-width:220px;border:1px solid var(--line);border-radius:7px;padding:8px 11px;outline:none}.search:focus{border-color:var(--blue)}.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow);overflow:hidden}.head,.row{display:grid;grid-template-columns:minmax(260px,1fr) 110px 170px 82px;align-items:center}.head{background:#f7f9fc;color:var(--muted);font-size:12px;border-bottom:1px solid var(--line);padding:9px 14px}.head span{cursor:pointer}.row{padding:8px 14px;min-height:49px;border-bottom:1px solid #edf1f5}.row:last-child{border-bottom:0}.row:hover{background:#f5f9ff}.name{display:flex;align-items:center;min-width:0;gap:11px}.name button{border:0;background:none;padding:0;text-align:left;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;color:var(--text)}.name button:hover{color:var(--blue)}.icon{font-size:23px;width:26px;text-align:center}.meta{color:var(--muted);font-size:12px}.actions{display:flex;gap:4px;justify-content:flex-end}.iconbtn{border:0;background:none;color:#718096;cursor:pointer;padding:5px}.iconbtn:hover{color:var(--blue)}.empty{padding:70px 20px;text-align:center;color:var(--muted)}.drop{position:fixed;inset:0;background:#1677ff24;z-index:9;display:none;place-items:center;border:4px dashed var(--blue);font-size:24px;color:var(--blue);font-weight:700}.drop.on{display:grid}.toast{position:fixed;right:24px;bottom:24px;max-width:380px;padding:11px 16px;background:#17212beF;color:#fff;border-radius:8px;box-shadow:var(--shadow);opacity:0;transform:translateY(12px);pointer-events:none;transition:.2s}.toast.on{opacity:1;transform:none}.danger{color:var(--danger)}dialog{border:0;border-radius:11px;box-shadow:0 18px 70px #0005;padding:0;min-width:340px}dialog::backdrop{background:#14203377}.modal{padding:20px}.modal h3{margin:0 0 15px}.modal input{width:100%;padding:9px;border:1px solid var(--line);border-radius:7px}.modal .foot{display:flex;justify-content:flex-end;gap:8px;margin-top:18px}@media(max-width:760px){.layout{grid-template-columns:1fr}aside{display:none}.main{padding:14px}.head,.row{grid-template-columns:minmax(130px,1fr) 80px 72px}.date{display:none}.search{min-width:0;width:130px}.bar{flex-wrap:wrap}}
</style></head><body><div class="app"><header class="top"><div class="logo">📁</div><strong id="title">Simple File Browser</strong><span class="status" id="status"></span></header><div class="layout"><aside><div class="tree" id="tree"></div></aside><main class="main"><div class="crumbs" id="crumbs"></div><div class="bar"><button class="btn primary write" onclick="pickFiles()" data-i18n="upload">↑ Upload</button><button class="btn write" onclick="newFolder()" data-i18n="newFolder">＋ New folder</button><button class="btn" onclick="load()" data-i18n="refresh">↻ Refresh</button><input class="search" id="search" data-i18n-placeholder="search" placeholder="Search this folder" oninput="render()"></div><section class="panel"><div class="head"><span onclick="sortBy('name')" data-i18n="name">Name</span><span onclick="sortBy('size')" data-i18n="size">Size</span><span class="date" onclick="sortBy('mtime')" data-i18n="modified">Date modified</span><span></span></div><div id="files"></div></section></main></div></div><input id="picker" type="file" multiple hidden><div class="drop" id="drop" data-i18n="drop">Drop files here to upload</div><div class="toast" id="toast"></div><dialog id="dialog"><div class="modal"><h3 id="dlgTitle"></h3><input id="dlgInput"><div class="foot"><button class="btn" onclick="dialog.close()" data-i18n="cancel">Cancel</button><button class="btn primary" id="dlgOk" data-i18n="confirm">Confirm</button></div></div></dialog>
<script>
const M={
 'en-US':{allFiles:'▣ All files',upload:'↑ Upload',newFolder:'＋ New folder',refresh:'↻ Refresh',search:'Search this folder',name:'Name',size:'Size',modified:'Date modified',drop:'Drop files here to upload',cancel:'Cancel',confirm:'Confirm',readWrite:'Read / write',readOnly:'Read only',home:'🏠 Home',noResults:'No matching files.',empty:'This folder is empty.',download:'Download',rename:'Rename',delete:'Delete',newFolderName:'New folder name',folderCreated:'Folder created.',renamed:'Name changed.',deleteAsk:n=>`Permanently delete “${n}”? If it is a folder, all files and subfolders inside it will also be deleted.`,deleted:'Deleted.',uploading:'Uploading…',uploaded:n=>`${n} file(s) uploaded.`,requestFailed:'The request could not be completed.'},
 'es-ES':{allFiles:'▣ Todos los archivos',upload:'↑ Subir',newFolder:'＋ Nueva carpeta',refresh:'↻ Actualizar',search:'Buscar en esta carpeta',name:'Nombre',size:'Tamaño',modified:'Fecha de modificación',drop:'Suelta aquí los archivos para subirlos',cancel:'Cancelar',confirm:'Confirmar',readWrite:'Lectura / escritura',readOnly:'Solo lectura',home:'🏠 Inicio',noResults:'No hay archivos que coincidan.',empty:'Esta carpeta está vacía.',download:'Descargar',rename:'Cambiar nombre',delete:'Eliminar',newFolderName:'Nombre de la nueva carpeta',folderCreated:'Carpeta creada.',renamed:'Nombre cambiado.',deleteAsk:n=>`¿Eliminar “${n}” permanentemente? Si es una carpeta, también se eliminarán todos sus archivos y subcarpetas.`,deleted:'Eliminado.',uploading:'Subiendo…',uploaded:n=>`${n} archivo(s) subido(s).`,requestFailed:'No se pudo completar la solicitud.'},
 'ja-JP':{allFiles:'▣ すべてのファイル',upload:'↑ アップロード',newFolder:'＋ 新しいフォルダー',refresh:'↻ 更新',search:'このフォルダーを検索',name:'名前',size:'サイズ',modified:'更新日時',drop:'ここにドロップしてアップロード',cancel:'キャンセル',confirm:'確認',readWrite:'読み取り / 書き込み',readOnly:'読み取り専用',home:'🏠 ホーム',noResults:'一致するファイルがありません。',empty:'このフォルダーは空です。',download:'ダウンロード',rename:'名前を変更',delete:'削除',newFolderName:'新しいフォルダー名',folderCreated:'フォルダーを作成しました。',renamed:'名前を変更しました。',deleteAsk:n=>`「${n}」を完全に削除しますか？フォルダーの場合、中のファイルとサブフォルダーもすべて削除されます。`,deleted:'削除しました。',uploading:'アップロード中…',uploaded:n=>`${n}個のファイルをアップロードしました。`,requestFailed:'リクエストを完了できませんでした。'},
 'ko-KR':{allFiles:'▣ 모든 파일',upload:'↑ 업로드',newFolder:'＋ 새 폴더',refresh:'↻ 새로고침',search:'현재 폴더 검색',name:'이름',size:'크기',modified:'수정한 날짜',drop:'여기에 놓아 업로드',cancel:'취소',confirm:'확인',readWrite:'읽기 / 쓰기',readOnly:'읽기 전용',home:'🏠 홈',noResults:'검색 결과가 없습니다.',empty:'이 폴더는 비어 있습니다.',download:'다운로드',rename:'이름 변경',delete:'삭제',newFolderName:'새 폴더 이름',folderCreated:'폴더를 만들었습니다.',renamed:'이름을 변경했습니다.',deleteAsk:n=>`“${n}”을(를) 영구 삭제할까요? 폴더인 경우 내부의 파일과 하위 폴더도 모두 삭제됩니다.`,deleted:'삭제했습니다.',uploading:'업로드 중…',uploaded:n=>`${n}개 파일을 업로드했습니다.`,requestFailed:'요청을 완료할 수 없습니다.'}
};
const LANG_MAP={en:'en-US',es:'es-ES',ja:'ja-JP',ko:'ko-KR'};
const LOCALE=(navigator.languages||[navigator.language||'en']).map(x=>LANG_MAP[x.toLowerCase().split('-')[0]]).find(Boolean)||'en-US';
const t=(key,...args)=>typeof M[LOCALE][key]==='function'?M[LOCALE][key](...args):M[LOCALE][key];
document.documentElement.lang=LOCALE;document.querySelectorAll('[data-i18n]').forEach(e=>e.textContent=t(e.dataset.i18n));document.querySelectorAll('[data-i18n-placeholder]').forEach(e=>e.placeholder=t(e.dataset.i18nPlaceholder));
let path='', items=[], writable=false, sortKey='name', sortAsc=true, treeCache=new Map(), treeOpen=new Set(['']);
const $=s=>document.querySelector(s), enc=p=>p.split('/').map(encodeURIComponent).join('/');
function toast(s,bad=false){let e=$('#toast');e.textContent=s;e.style.background=bad?'#b4232b':'#17212b';e.classList.add('on');setTimeout(()=>e.classList.remove('on'),2600)}
async function api(url,opt){let r=await fetch(url,opt),data;try{data=await r.json()}catch{data={error:r.statusText}}if(!r.ok)throw Error(data.error||r.statusText);return data}
async function load(p=path){try{let d=await api('/api/list?path='+encodeURIComponent(p));path=d.path;items=d.items;writable=d.writable;treeCache.set(path,folderNames(d.items));$('#title').textContent=d.title;$('#status').textContent=writable?t('readWrite'):t('readOnly');document.querySelectorAll('.write').forEach(x=>x.hidden=!writable);crumbs();render();await syncTree(path)}catch(e){toast(e.message,true)}}
function folderNames(list){return list.filter(x=>x.dir).map(x=>x.name).sort((a,b)=>a.localeCompare(b,LOCALE,{numeric:true,sensitivity:'base'}))}
async function ensureTree(p){if(treeCache.has(p))return;let d=await api('/api/list?path='+encodeURIComponent(p));treeCache.set(p,folderNames(d.items))}
async function syncTree(p){let cur='';treeOpen.add('');await ensureTree('');for(let part of (p?p.split('/'):[])){cur+=(cur?'/':'')+part;treeOpen.add(cur);await ensureTree(cur)}renderTree()}
async function toggleTree(p,e){if(e)e.stopPropagation();if(treeOpen.has(p)){treeOpen.delete(p);renderTree();return}treeOpen.add(p);try{await ensureTree(p);renderTree()}catch(err){treeOpen.delete(p);toast(err.message,true)}}
function treeToggle(p){if(treeCache.has(p)&&treeCache.get(p).length===0)return '<span class="tree-spacer"></span>';return '<button class="tree-toggle" aria-label="Toggle" onclick="toggleTree('+JSON.stringify(p).replaceAll('\"','&quot;')+',event)">'+(treeOpen.has(p)?'▾':'▸')+'</button>'}
function treeBranch(parent,depth){return (treeCache.get(parent)||[]).map(name=>{let p=parent+(parent?'/':'')+name,q=JSON.stringify(p).replaceAll('\"','&quot;'),open=treeOpen.has(p);return '<div class="tree-row '+(p===path?'active':'')+'" style="padding-left:'+(4+depth*14)+'px">'+treeToggle(p)+'<button class="tree-name" title="'+esc(name)+'" onclick="load('+q+')">📁 '+esc(name)+'</button></div>'+(open?treeBranch(p,depth+1):'')}).join('')}
function renderTree(){let rootOpen=treeOpen.has('');$('#tree').innerHTML='<div class="tree-row '+(path===''?'active':'')+'" style="padding-left:4px">'+treeToggle('')+'<button class="tree-name" onclick="load(\'\')">'+t('allFiles')+'</button></div>'+(rootOpen?treeBranch('',1):'')}
function crumbs(){let e=$('#crumbs'),parts=path?path.split('/'):[];e.innerHTML='<button onclick="load(\'\')">'+t('home')+'</button>';let p='';parts.forEach((x,i)=>{p+=(p?'/':'')+x;e.innerHTML+=' <span>›</span> <button onclick="load('+JSON.stringify(p).replaceAll('"','&quot;')+')">'+esc(x)+'</button>'})}
function esc(s){let d=document.createElement('div');d.textContent=s;return d.innerHTML}
function human(n){if(n==null)return '—';let u=['B','KB','MB','GB','TB'],i=0;while(n>=1024&&i<4){n/=1024;i++}return (i?n.toFixed(n<10?1:0):n)+' '+u[i]}
function sortBy(k){sortAsc=sortKey===k?!sortAsc:true;sortKey=k;render()}
function render(){let q=$('#search').value.toLocaleLowerCase(LOCALE),a=items.filter(x=>x.name.toLocaleLowerCase(LOCALE).includes(q));a.sort((x,y)=>{if(x.dir!==y.dir)return x.dir?-1:1;let v=sortKey==='name'?x.name.localeCompare(y.name,LOCALE,{numeric:true,sensitivity:'base'}):(x[sortKey]||0)-(y[sortKey]||0);return sortAsc?v:-v});let e=$('#files');if(!a.length){e.innerHTML='<div class="empty">'+(q?t('noResults'):t('empty'))+'</div>';return}e.innerHTML=a.map(x=>{let p=path+(path?'/':'')+x.name,n=JSON.stringify(x.name).replaceAll('"','&quot;');return '<div class="row"><div class="name"><span class="icon">'+(x.dir?'📁':'📄')+'</span><button title="'+esc(x.name)+'" onclick="openItem('+JSON.stringify(p).replaceAll('"','&quot;')+','+x.dir+')">'+esc(x.name)+'</button></div><div class="meta">'+human(x.size)+'</div><div class="meta date">'+new Date(x.mtime*1000).toLocaleString(LOCALE)+'</div><div class="actions">'+(!x.dir?'<button class="iconbtn" title="'+t('download')+'" onclick="download('+JSON.stringify(p).replaceAll('"','&quot;')+')">↓</button>':'')+(writable?'<button class="iconbtn" title="'+t('rename')+'" onclick="renameItem('+n+')">✎</button><button class="iconbtn danger" title="'+t('delete')+'" onclick="removeItem('+n+')">×</button>':'')+'</div></div>'}).join('')}
function openItem(p,d){d?load(p):download(p)}function download(p){location.href='/api/download?path='+encodeURIComponent(p)}
function promptBox(title,value,cb){$('#dlgTitle').textContent=title;$('#dlgInput').value=value||'';$('#dlgOk').onclick=()=>{let v=$('#dlgInput').value.trim();if(v){dialog.close();cb(v)}};dialog.showModal();setTimeout(()=>{$('#dlgInput').focus();$('#dlgInput').select()},30)}
function newFolder(){promptBox(t('newFolderName'),'',async n=>{try{await api('/api/mkdir',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path,name:n})});toast(t('folderCreated'));load()}catch(e){toast(e.message,true)}})}
function renameItem(old){promptBox(t('rename'),old,async n=>{try{await api('/api/rename',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path,name:old,new_name:n})});toast(t('renamed'));load()}catch(e){toast(e.message,true)}})}
async function removeItem(name){if(!confirm(t('deleteAsk',name)))return;try{await api('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path,name})});toast(t('deleted'));load()}catch(e){toast(e.message,true)}}
function pickFiles(){$('#picker').click()}$('#picker').onchange=e=>upload(e.target.files);
async function upload(files){if(!writable||!files.length)return;let f=new FormData();f.append('path',path);for(let x of files)f.append('files',x,x.name);try{toast(t('uploading'));let d=await api('/api/upload',{method:'POST',body:f});toast(t('uploaded',d.count));$('#picker').value='';load()}catch(e){toast(e.message,true)}}
let drag=0;addEventListener('dragenter',e=>{e.preventDefault();if(writable){drag++;$('#drop').classList.add('on')}});addEventListener('dragleave',e=>{e.preventDefault();if(--drag<=0){drag=0;$('#drop').classList.remove('on')}});addEventListener('dragover',e=>e.preventDefault());addEventListener('drop',e=>{e.preventDefault();drag=0;$('#drop').classList.remove('on');upload(e.dataTransfer.files)});load();
</script></body></html>'''


def safe_name(name: str) -> str:
    if not name or name in {".", ".."} or "/" in name or "\\" in name or "\0" in name:
        raise ValueError("Invalid file name.")
    return name


class FileBrowserHandler(BaseHTTPRequestHandler):
    server_version = f"SimpleFileBrowser/{VERSION}"

    @property
    def config(self):
        return self.server.config  # type: ignore[attr-defined]

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def send_json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(raw)

    def fail(self, status, message):
        self.send_json({"error": message}, status)

    def resolve(self, relative="", must_exist=True):
        relative = urllib.parse.unquote(relative).replace("\\", "/").lstrip("/")
        root = self.config["root"]
        target = (root / relative).resolve(strict=False)
        try:
            target.relative_to(root)
        except ValueError:
            raise PermissionError("Access outside the configured root folder is not allowed.")
        if must_exist and not target.exists():
            raise FileNotFoundError("The file or folder does not exist.")
        return target

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        try:
            if parsed.path == "/":
                raw = INDEX_HTML.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src 'self' data:")
                self.send_header("X-Frame-Options", "DENY")
                self.end_headers(); self.wfile.write(raw)
            elif parsed.path == "/api/list":
                target = self.resolve(query.get("path", [""])[0])
                if not target.is_dir(): raise ValueError("The requested path is not a folder.")
                items = []
                for p in target.iterdir():
                    if not self.config["show_hidden"] and p.name.startswith("."): continue
                    try:
                        st = p.stat(); is_dir = p.is_dir()
                        items.append({"name": p.name, "dir": is_dir, "size": None if is_dir else st.st_size, "mtime": st.st_mtime})
                    except (OSError, PermissionError): pass
                rel = target.relative_to(self.config["root"]).as_posix()
                self.send_json({"path": "" if rel == "." else rel, "items": items, "writable": self.config["upload"], "title": self.config["title"]})
            elif parsed.path == "/api/download":
                target = self.resolve(query.get("path", [""])[0])
                if not target.is_file(): raise ValueError("The requested path is not a file.")
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
                self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + urllib.parse.quote(target.name))
                self.send_header("Content-Length", str(target.stat().st_size)); self.end_headers()
                with target.open("rb") as f: shutil.copyfileobj(f, self.wfile)
            else: self.fail(404, "Not found.")
        except PermissionError as e: self.fail(403, str(e))
        except FileNotFoundError as e: self.fail(404, str(e))
        except (ValueError, OSError) as e: self.fail(400, str(e))

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1024 * 1024: raise ValueError("The request is too large.")
        return json.loads(self.rfile.read(length) or b"{}")

    def require_write(self):
        if not self.config["upload"]: raise PermissionError("Write operations are disabled.")

    def do_POST(self):
        parsed = urllib.parse.urlsplit(self.path)
        try:
            self.require_write()
            if parsed.path == "/api/upload": self.handle_upload(); return
            data = self.read_json(); parent = self.resolve(data.get("path", ""))
            if not parent.is_dir(): raise ValueError("The destination folder is invalid.")
            if parsed.path == "/api/mkdir":
                (parent / safe_name(data.get("name", ""))).mkdir()
            elif parsed.path == "/api/rename":
                old = self.resolve((parent.relative_to(self.config["root"]) / safe_name(data.get("name", ""))).as_posix())
                new = parent / safe_name(data.get("new_name", ""))
                if new.exists(): raise FileExistsError("An item with the same name already exists.")
                old.rename(new)
            elif parsed.path == "/api/delete":
                target = parent / safe_name(data.get("name", ""))
                if target.is_symlink():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)
                elif target.exists():
                    target.unlink()
                else:
                    raise FileNotFoundError("The file or folder does not exist.")
            else: self.fail(404, "Not found."); return
            self.send_json({"ok": True})
        except PermissionError as e: self.fail(403, str(e))
        except FileNotFoundError as e: self.fail(404, str(e))
        except FileExistsError as e: self.fail(409, str(e))
        except (ValueError, OSError, json.JSONDecodeError) as e: self.fail(400, str(e))

    def handle_upload(self):
        length = int(self.headers.get("Content-Length", "0"))
        max_bytes = self.config["max_upload_mb"] * 1024 * 1024
        if length <= 0 or length > max_bytes: raise ValueError(f"Uploads are limited to {self.config['max_upload_mb']} MB per request.")
        ctype = self.headers.get("Content-Type", "")
        if not ctype.startswith("multipart/form-data") or "boundary=" not in ctype: raise ValueError("A multipart/form-data request is required.")
        with tempfile.SpooledTemporaryFile(max_size=8 * 1024 * 1024) as body:
            remaining = length
            while remaining:
                chunk = self.rfile.read(min(1024 * 1024, remaining))
                if not chunk: raise ValueError("The upload was interrupted.")
                body.write(chunk); remaining -= len(chunk)
            body.seek(0)
            msg = BytesParser(policy=email_policy).parsebytes(("Content-Type: " + ctype + "\r\nMIME-Version: 1.0\r\n\r\n").encode() + body.read())
        fields, files = {}, []
        for part in msg.iter_parts():
            name = part.get_param("name", header="content-disposition")
            filename = part.get_filename()
            if filename is not None: files.append((safe_name(Path(filename).name), part.get_payload(decode=True) or b""))
            elif name: fields[name] = (part.get_payload(decode=True) or b"").decode("utf-8")
        parent = self.resolve(fields.get("path", ""))
        if not parent.is_dir(): raise ValueError("The destination folder is invalid.")
        overwrite = self.config["overwrite"]
        targets = []
        for name, _ in files:
            relative = (parent.relative_to(self.config["root"]) / name).as_posix()
            target = self.resolve(relative, must_exist=False)
            if target.exists() and (target.is_dir() or not overwrite):
                raise FileExistsError(f"{name}: an item with the same name already exists.")
            targets.append(target)
        for (name, payload), target in zip(files, targets):
            with target.open("wb") as out: out.write(payload)
        self.send_json({"ok": True, "count": len(files)})


def load_config(path: Path):
    if not path.exists(): return {}
    with path.open(encoding="utf-8") as f: data = json.load(f)
    if not isinstance(data, dict): raise ValueError("The top-level value in the configuration file must be an object.")
    return data


def main():
    parser = argparse.ArgumentParser(description="A dependency-free, single-file HTTP file browser")
    parser.add_argument("--config", default="config.json", help="JSON configuration file (default: config.json)")
    parser.add_argument("--port", type=int, help="server port")
    parser.add_argument("--host", help="bind address (default: 0.0.0.0)")
    parser.add_argument("--root", help="root folder to expose")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--upload", action="store_true", default=None, help="allow uploads, renaming, and deletion")
    group.add_argument("--read-only", action="store_false", dest="upload", help="disable write operations")
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args()
    try: file_cfg = load_config(Path(args.config))
    except (OSError, ValueError, json.JSONDecodeError) as e: parser.error(f"configuration error: {e}")
    defaults = {"host": "0.0.0.0", "port": 8000, "root": ".", "upload": False, "title": "Simple File Browser", "show_hidden": False, "max_upload_mb": 512, "overwrite": False}
    cfg = defaults | file_cfg
    for key in ("host", "port", "root", "upload"):
        value = getattr(args, key)
        if value is not None: cfg[key] = value
    cfg["root"] = Path(cfg["root"]).expanduser().resolve()
    if not cfg["root"].is_dir(): parser.error(f"root folder does not exist: {cfg['root']}")
    if not 1 <= int(cfg["port"]) <= 65535: parser.error("port must be between 1 and 65535")
    server = ThreadingHTTPServer((str(cfg["host"]), int(cfg["port"])), FileBrowserHandler)
    server.config = cfg
    print(f"Simple File Browser {VERSION}")
    print(f"Root: {cfg['root']}")
    print(f"URL:  http://{'localhost' if cfg['host'] in ('0.0.0.0', '::') else cfg['host']}:{cfg['port']}")
    print(f"Mode: {'read/write' if cfg['upload'] else 'read-only'} (Ctrl+C to stop)")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nStopped.")
    finally: server.server_close()


if __name__ == "__main__":
    main()
