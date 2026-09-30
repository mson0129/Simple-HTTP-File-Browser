#!/usr/bin/env python3
"""A dependency-free, single-file HTTP file browser."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import shutil
import sys
import tempfile
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

VERSION = "1.5.0"

PREVIEW_TYPES = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
    ".bmp": "image/bmp", ".avif": "image/avif", ".ico": "image/x-icon",
    ".apng": "image/apng",
    ".txt": "text/plain; charset=utf-8", ".text": "text/plain; charset=utf-8",
    ".md": "text/plain; charset=utf-8", ".markdown": "text/plain; charset=utf-8",
    ".mp4": "video/mp4", ".m4v": "video/mp4", ".mov": "video/quicktime",
    ".webm": "video/webm", ".ogv": "video/ogg",
    ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".aac": "audio/aac",
    ".wav": "audio/wav", ".ogg": "audio/ogg", ".oga": "audio/ogg",
    ".flac": "audio/flac",
}

INDEX_HTML = r'''<!doctype html>
<html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Simple File Browser</title><style>
:root{--bg:#f3f6fa;--panel:#fff;--line:#dbe3ec;--text:#17212b;--muted:#687787;--blue:#1677ff;--blue2:#eaf3ff;--danger:#d9363e;--shadow:0 7px 28px #24405d18}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}button,input{font:inherit}.app{min-height:100vh}.top{height:58px;background:#172b4d;color:#fff;display:flex;align-items:center;padding:0 22px;gap:12px;box-shadow:0 2px 10px #0003}.logo{width:31px;height:31px;border-radius:8px;background:linear-gradient(145deg,#40a9ff,#096dd9);display:grid;place-items:center;font-size:18px}.top strong{font-size:16px}.top .status{margin-left:auto;color:#cbd7e7;font-size:12px}.layout{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:calc(100vh - 58px)}aside{padding:16px 10px;background:#fff;border-right:1px solid var(--line);overflow:auto;max-height:calc(100vh - 58px)}.tree{min-width:0}.tree-row{display:flex;align-items:center;height:34px;border-radius:7px;white-space:nowrap}.tree-row:hover{background:#f5f9ff}.tree-row.active{background:var(--blue2);color:var(--blue);font-weight:650}.tree-toggle,.tree-name{border:0;background:none;cursor:pointer;color:inherit;padding:0}.tree-toggle{width:22px;min-width:22px;height:30px;color:var(--muted)}.tree-spacer{width:22px;min-width:22px}.tree-name{min-width:0;overflow:hidden;text-overflow:ellipsis;text-align:left;padding:6px 8px 6px 2px;flex:1}.main{padding:22px 26px;min-width:0}.crumbs{display:flex;align-items:center;gap:5px;min-height:33px;overflow:auto;white-space:nowrap}.crumbs button{border:0;background:none;color:var(--blue);cursor:pointer;padding:4px}.bar{display:flex;gap:8px;align-items:center;margin:12px 0}.btn{border:1px solid var(--line);background:#fff;border-radius:7px;padding:8px 12px;cursor:pointer;color:var(--text)}.btn:hover{border-color:#8abfff;color:var(--blue)}.primary{background:var(--blue);border-color:var(--blue);color:white}.primary:hover{color:white;background:#096dd9}.search{margin-left:auto;min-width:220px;border:1px solid var(--line);border-radius:7px;padding:8px 11px;outline:none}.search:focus{border-color:var(--blue)}.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow);overflow:hidden}.head,.row{display:grid;grid-template-columns:minmax(260px,1fr) 110px 170px 82px;align-items:center}.head{background:#f7f9fc;color:var(--muted);font-size:12px;border-bottom:1px solid var(--line);padding:9px 14px}.head span{cursor:pointer}.row{padding:8px 14px;min-height:49px;border-bottom:1px solid #edf1f5}.row:last-child{border-bottom:0}.row:hover{background:#f5f9ff}.name{display:flex;align-items:center;min-width:0;gap:11px}.name button{border:0;background:none;padding:0;text-align:left;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer;color:var(--text)}.name button:hover{color:var(--blue)}.icon{font-size:23px;width:26px;text-align:center}.meta{color:var(--muted);font-size:12px}.actions{display:flex;gap:4px;justify-content:flex-end}.iconbtn{border:0;background:none;color:#718096;cursor:pointer;padding:5px}.iconbtn:hover{color:var(--blue)}.empty{padding:70px 20px;text-align:center;color:var(--muted)}.drop{position:fixed;inset:0;background:#1677ff24;z-index:9;display:none;place-items:center;border:4px dashed var(--blue);font-size:24px;color:var(--blue);font-weight:700}.drop.on{display:grid}.upload-panel{position:fixed;right:24px;bottom:24px;width:min(390px,calc(100vw - 32px));z-index:8;background:#fff;border:1px solid var(--line);border-radius:11px;box-shadow:0 14px 45px #172b4d35;padding:16px}.upload-panel[hidden]{display:none}.upload-title{font-weight:700;margin-bottom:10px}.upload-list{max-height:min(55vh,420px);overflow:auto}.upload-item{padding:9px 0;border-top:1px solid var(--line)}.upload-item:first-child{border-top:0}.upload-item-head{display:flex;align-items:center;gap:8px;font-size:12px;margin-bottom:6px}.upload-item-name{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}.upload-item-status{color:var(--muted);white-space:nowrap}.upload-item-status.complete{color:#17803d;font-weight:650}.upload-item-status.failed{color:var(--danger);font-weight:650}.upload-track{height:8px;background:#e8edf3;border-radius:99px;overflow:hidden}.upload-fill{height:100%;width:0;background:linear-gradient(90deg,#4096ff,var(--blue));border-radius:99px;transition:width .12s linear}.upload-fill.complete{background:#35a866}.upload-stats{margin-top:5px;color:var(--muted);font-size:11px;text-align:right}.toast{position:fixed;right:24px;bottom:24px;max-width:380px;padding:11px 16px;background:#17212beF;color:#fff;border-radius:8px;box-shadow:var(--shadow);opacity:0;transform:translateY(12px);pointer-events:none;transition:.2s}.toast.on{opacity:1;transform:none}.danger{color:var(--danger)}dialog{border:0;border-radius:11px;box-shadow:0 18px 70px #0005;padding:0;min-width:340px}dialog::backdrop{background:#14203377}.modal{padding:20px}.modal h3{margin:0 0 15px}.modal input{width:100%;padding:9px;border:1px solid var(--line);border-radius:7px}.modal .foot{display:flex;justify-content:flex-end;gap:8px;margin-top:18px}@media(max-width:760px){.layout{grid-template-columns:1fr}aside{display:none}.main{padding:14px}.head,.row{grid-template-columns:minmax(130px,1fr) 80px 72px}.date{display:none}.search{min-width:0;width:130px}.bar{flex-wrap:wrap}}
</style></head><body><div class="app"><header class="top"><div class="logo">📁</div><strong id="title">Simple File Browser</strong><span class="status" id="status"></span></header><div class="layout"><aside><div class="tree" id="tree"></div></aside><main class="main"><div class="crumbs" id="crumbs"></div><div class="bar"><button class="btn primary write" onclick="pickFiles()" data-i18n="upload">↑ Upload</button><button class="btn write" onclick="newFolder()" data-i18n="newFolder">＋ New folder</button><button class="btn" onclick="load()" data-i18n="refresh">↻ Refresh</button><input class="search" id="search" data-i18n-placeholder="search" placeholder="Search this folder" oninput="render()"></div><section class="panel"><div class="head"><span onclick="sortBy('name')" data-i18n="name">Name</span><span onclick="sortBy('size')" data-i18n="size">Size</span><span class="date" onclick="sortBy('mtime')" data-i18n="modified">Date modified</span><span></span></div><div id="files"></div></section></main></div></div><input id="picker" type="file" multiple hidden><div class="drop" id="drop" data-i18n="drop">Drop files here to upload</div><div class="upload-panel" id="uploadPanel" hidden><div class="upload-title" id="uploadTitle">Uploading…</div><div id="uploadList"></div></div><div class="toast" id="toast"></div><dialog id="dialog"><div class="modal"><h3 id="dlgTitle"></h3><input id="dlgInput"><div class="foot"><button class="btn" onclick="dialog.close()" data-i18n="cancel">Cancel</button><button class="btn primary" id="dlgOk" data-i18n="confirm">Confirm</button></div></div></dialog>
<dialog id="previewDialog" class="preview-dialog" aria-labelledby="previewTitle"><div class="preview-head"><strong id="previewTitle"></strong><button class="btn" type="button" onclick="document.querySelector('#previewDialog').close()" data-i18n="close">Close</button></div><div class="preview-body"><img id="previewImage" alt="" hidden><video id="previewVideo" controls playsinline preload="metadata" hidden></video><audio id="previewAudio" controls preload="metadata" hidden></audio><pre id="previewText" hidden></pre><div id="previewMarkdown" hidden></div><p id="previewError" hidden></p></div></dialog>
<style>.head,.row{grid-template-columns:minmax(260px,1fr) 110px 170px 132px}.preview-dialog{width:min(1100px,92vw);max-width:92vw;max-height:92vh}.preview-head{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:12px 16px;border-bottom:1px solid var(--line)}.preview-head strong{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.preview-body{display:grid;place-items:center;min-height:160px;padding:16px;overflow:auto}.preview-body img{display:block;max-width:100%;max-height:calc(92vh - 105px);object-fit:contain}.preview-body img[hidden],.preview-body pre[hidden],.preview-body div[hidden]{display:none}.preview-body pre,.preview-body #previewMarkdown{width:100%;max-height:calc(92vh - 105px);overflow:auto;margin:0}.preview-body pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.6 ui-monospace,SFMono-Regular,Consolas,monospace}.preview-body #previewMarkdown{line-height:1.6;overflow-wrap:anywhere}.preview-body #previewMarkdown h1,.preview-body #previewMarkdown h2{border-bottom:1px solid var(--line);padding-bottom:6px}.preview-body #previewMarkdown pre{background:#f5f7fa;padding:12px;border-radius:7px}.preview-body #previewMarkdown blockquote{border-left:3px solid var(--line);padding-left:12px;color:var(--muted)}.preview-body p{color:var(--danger)}.iconbtn svg{display:block;width:18px;height:18px}@media(max-width:760px){.head,.row{grid-template-columns:minmax(130px,1fr) 80px 120px}}</style>
<style>.preview-body #previewMarkdown p{color:var(--text)}.preview-body #previewError{color:var(--danger)}.preview-body #previewMarkdown a{color:var(--blue);text-decoration:underline}.preview-body #previewMarkdown table{border-collapse:collapse;display:block;max-width:100%;overflow-x:auto;margin:14px 0}.preview-body #previewMarkdown th,.preview-body #previewMarkdown td{border:1px solid var(--line);padding:7px 11px;min-width:70px}.preview-body #previewMarkdown th{background:#f7f9fc;font-weight:650}</style>
<style>.preview-body video{display:block;max-width:100%;max-height:calc(92vh - 105px)}.preview-body audio{display:block;width:min(100%,600px)}.preview-body video[hidden],.preview-body audio[hidden]{display:none}</style>
<script>
const M={
 'en-US':{allFiles:'▣ All files',upload:'↑ Upload',newFolder:'＋ New folder',refresh:'↻ Refresh',search:'Search this folder',name:'Name',size:'Size',modified:'Date modified',drop:'Drop files here to upload',cancel:'Cancel',confirm:'Confirm',readWrite:'Read / write',readOnly:'Read only',home:'🏠 Home',noResults:'No matching files.',empty:'This folder is empty.',download:'Download',rename:'Rename',delete:'Delete',newFolderName:'New folder name',folderCreated:'Folder created.',renamed:'Name changed.',deleteAsk:n=>`Permanently delete “${n}”? If it is a folder, all files and subfolders inside it will also be deleted.`,deleted:'Deleted.',uploading:'Uploading…',processing:'Processing…',queued:'Queued',uploadingFile:'Uploading…',complete:'✓ Complete',failed:'Failed',uploadSummary:(done,total,failed)=>failed?`${done}/${total} uploaded, ${failed} failed.`:`${done} file(s) uploaded.`,uploaded:n=>`${n} file(s) uploaded.`,requestFailed:'The request could not be completed.'},
 'es-ES':{allFiles:'▣ Todos los archivos',upload:'↑ Subir',newFolder:'＋ Nueva carpeta',refresh:'↻ Actualizar',search:'Buscar en esta carpeta',name:'Nombre',size:'Tamaño',modified:'Fecha de modificación',drop:'Suelta aquí los archivos para subirlos',cancel:'Cancelar',confirm:'Confirmar',readWrite:'Lectura / escritura',readOnly:'Solo lectura',home:'🏠 Inicio',noResults:'No hay archivos que coincidan.',empty:'Esta carpeta está vacía.',download:'Descargar',rename:'Cambiar nombre',delete:'Eliminar',newFolderName:'Nombre de la nueva carpeta',folderCreated:'Carpeta creada.',renamed:'Nombre cambiado.',deleteAsk:n=>`¿Eliminar “${n}” permanentemente? Si es una carpeta, también se eliminarán todos sus archivos y subcarpetas.`,deleted:'Eliminado.',uploading:'Subiendo…',processing:'Procesando…',queued:'En cola',uploadingFile:'Subiendo…',complete:'✓ Completado',failed:'Fallido',uploadSummary:(done,total,failed)=>failed?`${done}/${total} subidos, ${failed} fallidos.`:`${done} archivo(s) subido(s).`,uploaded:n=>`${n} archivo(s) subido(s).`,requestFailed:'No se pudo completar la solicitud.'},
 'ja-JP':{allFiles:'▣ すべてのファイル',upload:'↑ アップロード',newFolder:'＋ 新しいフォルダー',refresh:'↻ 更新',search:'このフォルダーを検索',name:'名前',size:'サイズ',modified:'更新日時',drop:'ここにドロップしてアップロード',cancel:'キャンセル',confirm:'確認',readWrite:'読み取り / 書き込み',readOnly:'読み取り専用',home:'🏠 ホーム',noResults:'一致するファイルがありません。',empty:'このフォルダーは空です。',download:'ダウンロード',rename:'名前を変更',delete:'削除',newFolderName:'新しいフォルダー名',folderCreated:'フォルダーを作成しました。',renamed:'名前を変更しました。',deleteAsk:n=>`「${n}」を完全に削除しますか？フォルダーの場合、中のファイルとサブフォルダーもすべて削除されます。`,deleted:'削除しました。',uploading:'アップロード中…',processing:'処理中…',queued:'待機中',uploadingFile:'アップロード中…',complete:'✓ 完了',failed:'失敗',uploadSummary:(done,total,failed)=>failed?`${done}/${total}個をアップロード、${failed}個失敗。`:`${done}個のファイルをアップロードしました。`,uploaded:n=>`${n}個のファイルをアップロードしました。`,requestFailed:'リクエストを完了できませんでした。'},
 'ko-KR':{allFiles:'▣ 모든 파일',upload:'↑ 업로드',newFolder:'＋ 새 폴더',refresh:'↻ 새로고침',search:'현재 폴더 검색',name:'이름',size:'크기',modified:'수정한 날짜',drop:'여기에 놓아 업로드',cancel:'취소',confirm:'확인',readWrite:'읽기 / 쓰기',readOnly:'읽기 전용',home:'🏠 홈',noResults:'검색 결과가 없습니다.',empty:'이 폴더는 비어 있습니다.',download:'다운로드',rename:'이름 변경',delete:'삭제',newFolderName:'새 폴더 이름',folderCreated:'폴더를 만들었습니다.',renamed:'이름을 변경했습니다.',deleteAsk:n=>`“${n}”을(를) 영구 삭제할까요? 폴더인 경우 내부의 파일과 하위 폴더도 모두 삭제됩니다.`,deleted:'삭제했습니다.',uploading:'업로드 중…',processing:'처리 중…',queued:'대기 중',uploadingFile:'업로드 중…',complete:'✓ 완료',failed:'실패',uploadSummary:(done,total,failed)=>failed?`${done}/${total}개 업로드, ${failed}개 실패.`:`${done}개 파일을 업로드했습니다.`,uploaded:n=>`${n}개 파일을 업로드했습니다.`,requestFailed:'요청을 완료할 수 없습니다.'}
};
Object.assign(M['en-US'],{preview:'Preview',close:'Close',previewFailed:'This file could not be previewed.'});
Object.assign(M['es-ES'],{preview:'Vista previa',close:'Cerrar',previewFailed:'No se pudo mostrar el archivo.'});
Object.assign(M['ja-JP'],{preview:'プレビュー',close:'閉じる',previewFailed:'ファイルをプレビューできませんでした。'});
Object.assign(M['ko-KR'],{preview:'미리보기',close:'닫기',previewFailed:'파일을 미리 볼 수 없습니다.'});
M['en-US'].mediaFailed='This media cannot be played. The codec may be unsupported, or the file may be damaged.';
M['es-ES'].mediaFailed='No se puede reproducir este archivo. Es posible que el códec no sea compatible o que el archivo esté dañado.';
M['ja-JP'].mediaFailed='このメディアを再生できません。コーデックが非対応か、ファイルが破損している可能性があります。';
M['ko-KR'].mediaFailed='이 미디어를 재생할 수 없습니다. 코덱이 지원되지 않거나 파일이 손상되었을 수 있습니다.';
const LANG_MAP={en:'en-US',es:'es-ES',ja:'ja-JP',ko:'ko-KR'};
const LOCALE=(navigator.languages||[navigator.language||'en']).map(x=>LANG_MAP[x.toLowerCase().split('-')[0]]).find(Boolean)||'en-US';
const t=(key,...args)=>typeof M[LOCALE][key]==='function'?M[LOCALE][key](...args):M[LOCALE][key];
document.documentElement.lang=LOCALE;document.querySelectorAll('[data-i18n]').forEach(e=>e.textContent=t(e.dataset.i18n));document.querySelectorAll('[data-i18n-placeholder]').forEach(e=>e.placeholder=t(e.dataset.i18nPlaceholder));
let path='', items=[], writable=false, uploadActive=false, sortKey='name', sortAsc=true, treeCache=new Map(), treeOpen=new Set(['']);
const $=s=>document.querySelector(s), enc=p=>p.split('/').map(encodeURIComponent).join('/');
function toast(s,bad=false){let e=$('#toast');e.textContent=s;e.style.background=bad?'#b4232b':'#17212b';e.classList.add('on');setTimeout(()=>e.classList.remove('on'),2600)}
async function api(url,opt){let r=await fetch(url,opt),data;try{data=await r.json()}catch{data={error:r.statusText}}if(!r.ok)throw Error(data.error||r.statusText);return data}
let loadRequest=0;
async function load(p=path,recordHistory=true){let request=++loadRequest;try{let d=await api('/api/list?path='+encodeURIComponent(p)),previous=path;if(request!==loadRequest)return;path=d.path;items=d.items;writable=d.writable;if(recordHistory&&path!==previous)history.pushState({path},'',path?'?path='+encodeURIComponent(path):location.pathname);treeCache.set(path,folderNames(d.items));$('#title').textContent=d.title;$('#status').textContent=writable?t('readWrite'):t('readOnly');document.querySelectorAll('.write').forEach(x=>x.hidden=!writable);crumbs();render();await syncTree(path)}catch(e){if(request===loadRequest)toast(e.message,true)}}
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
const imagePreviewPattern=/\.(?:png|jpe?g|gif|webp|svg|bmp|avif|ico|apng)$/i;
const videoPreviewPattern=/\.(?:mp4|m4v|mov|webm|ogv)$/i;
const audioPreviewPattern=/\.(?:mp3|m4a|aac|wav|ogg|oga|flac)$/i;
const previewPattern=/\.(?:png|jpe?g|gif|webp|svg|bmp|avif|ico|apng|txt|text|md|markdown|mp4|m4v|mov|webm|ogv|mp3|m4a|aac|wav|ogg|oga|flac)$/i;
const eyeIcon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/></svg>';
function render(){let q=$('#search').value.toLocaleLowerCase(LOCALE),a=items.filter(x=>x.name.toLocaleLowerCase(LOCALE).includes(q));a.sort((x,y)=>{if(x.dir!==y.dir)return x.dir?-1:1;let v=sortKey==='name'?x.name.localeCompare(y.name,LOCALE,{numeric:true,sensitivity:'base'}):(x[sortKey]||0)-(y[sortKey]||0);return sortAsc?v:-v});let e=$('#files');if(!a.length){e.innerHTML='<div class="empty">'+(q?t('noResults'):t('empty'))+'</div>';return}e.innerHTML=a.map(x=>{let p=path+(path?'/':'')+x.name,n=JSON.stringify(x.name).replaceAll('"','&quot;'),qp=JSON.stringify(p).replaceAll('"','&quot;');return '<div class="row"><div class="name"><span class="icon">'+(x.dir?'📁':'📄')+'</span><button title="'+esc(x.name)+'" onclick="openItem('+qp+','+x.dir+')">'+esc(x.name)+'</button></div><div class="meta">'+human(x.size)+'</div><div class="meta date">'+new Date(x.mtime*1000).toLocaleString(LOCALE)+'</div><div class="actions">'+(!x.dir?(previewPattern.test(x.name)?'<button class="iconbtn" type="button" title="'+t('preview')+'" aria-label="'+t('preview')+'" onclick="preview('+qp+')">'+eyeIcon+'</button>':'')+'<button class="iconbtn" title="'+t('download')+'" onclick="download('+qp+')">↓</button>':'')+(writable?'<button class="iconbtn" title="'+t('rename')+'" onclick="renameItem('+n+')">✎</button><button class="iconbtn danger" title="'+t('delete')+'" onclick="removeItem('+n+')">×</button>':'')+'</div></div>'}).join('')}
function markdownInto(source,container,documentPath){
 container.replaceChildren();let lines=source.replace(/\r\n?/g,'\n').split('\n'),code=null,list=null,references=new Map();
 for(let line of lines){let definition=line.match(/^\s{0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))(?:\s+"[^"]*")?\s*$/);if(definition)references.set(definition[1].trim().toLowerCase(),definition[2]||definition[3])}
 const addLink=(node,label,address)=>{let link=document.createElement('a');try{if(/^https?:|^mailto:/i.test(address)){let url=new URL(address);if(!['http:','https:','mailto:'].includes(url.protocol))throw Error();link.href=url.href;link.target='_blank';link.rel='noopener noreferrer'}else{if(/^[a-z][a-z0-9+.-]*:/i.test(address)||address.startsWith('//')||address.startsWith('#'))throw Error();let parent=documentPath.split('/').slice(0,-1).map(encodeURIComponent).join('/'),url=new URL(address,location.origin+'/'+parent+'/');if(url.origin!==location.origin)throw Error();let path=decodeURIComponent(url.pathname.slice(1));link.href='/api/download?path='+encodeURIComponent(path);link.onclick=event=>{if(previewPattern.test(path)){event.preventDefault();preview(path)}}}link.textContent=label;node.append(link)}catch{node.append(document.createTextNode(label))}};
 const inline=(node,value)=>{let pattern=/(`[^`]+`|\[([^\]]+)\]\((<[^>]+>|[^)\s]+)(?:\s+"[^"]*")?\)|\[([^\]]+)\]\[([^\]]*)\]|\*\*[^*]+\*\*|\*[^*]+\*)/g,last=0,match;while((match=pattern.exec(value))){node.append(document.createTextNode(value.slice(last,match.index)));let token=match[0];if(match[2])addLink(node,match[2],match[3].replace(/^<|>$/g,''));else if(match[4]){let address=references.get((match[5]||match[4]).trim().toLowerCase());if(address)addLink(node,match[4],address);else node.append(document.createTextNode(token))}else{let tag=token.startsWith('`')?'code':token.startsWith('**')?'strong':'em',part=document.createElement(tag);part.textContent=token.slice(tag==='strong'?2:1,tag==='strong'?-2:-1);node.append(part)}last=pattern.lastIndex}node.append(document.createTextNode(value.slice(last)))};
 const cells=line=>{let value=line.trim();if(value.startsWith('|'))value=value.slice(1);if(value.endsWith('|'))value=value.slice(0,-1);let result=[],cell='';for(let i=0;i<value.length;i++){if(value[i]==='\\'&&value[i+1]==='|'){cell+='|';i++}else if(value[i]==='|'){result.push(cell.trim());cell=''}else cell+=value[i]}result.push(cell.trim());return result};
 for(let i=0;i<lines.length;i++){let line=lines[i],fence=line.match(/^\s*```/);if(fence){if(code){code=null}else{let pre=document.createElement('pre');code=document.createElement('code');pre.append(code);container.append(pre)}list=null;continue}if(code){code.textContent+=line+'\n';continue}if(/^\s{0,3}\[[^\]]+\]:\s*(?:<[^>]+>|\S+)/.test(line))continue;if(!line.trim()){list=null;continue}
  if(i+1<lines.length){let header=cells(line),separator=cells(lines[i+1]);if((line.includes('|')||lines[i+1].includes('|'))&&header.length===separator.length&&separator.every(cell=>/^:?-{3,}:?$/.test(cell))){let table=document.createElement('table'),thead=document.createElement('thead'),headRow=document.createElement('tr'),tbody=document.createElement('tbody'),align=separator.map(cell=>cell.startsWith(':')&&cell.endsWith(':')?'center':cell.endsWith(':')?'right':'left');header.forEach((value,j)=>{let th=document.createElement('th');th.style.textAlign=align[j];inline(th,value);headRow.append(th)});thead.append(headRow);table.append(thead,tbody);i++;while(i+1<lines.length&&lines[i+1].trim()&&lines[i+1].includes('|')){let row=document.createElement('tr'),values=cells(lines[++i]);header.forEach((_,j)=>{let td=document.createElement('td');td.style.textAlign=align[j];inline(td,values[j]||'');row.append(td)});tbody.append(row)}container.append(table);list=null;continue}}
  let heading=line.match(/^(#{1,6})\s+(.+)$/),bullet=line.match(/^\s*[-*+]\s+(.+)$/),quote=line.match(/^>\s?(.*)$/),tag,value;if(heading){tag='h'+heading[1].length;value=heading[2];list=null}else if(bullet){if(!list){list=document.createElement('ul');container.append(list)}tag='li';value=bullet[1]}else if(quote){tag='blockquote';value=quote[1];list=null}else{tag='p';value=line;list=null}let element=document.createElement(tag);inline(element,value);(tag==='li'?list:container).append(element)}
}
let previewRequest=0;
function clearPreviewSources(){let img=$('#previewImage');img.onload=img.onerror=null;img.removeAttribute('src');for(let media of [$('#previewVideo'),$('#previewAudio')]){media.pause();media.onerror=null;media.removeAttribute('src');media.load();media.hidden=true}}
async function preview(p,recordHistory=true){let img=$('#previewImage'),textView=$('#previewText'),markdown=$('#previewMarkdown'),error=$('#previewError'),dialog=$('#previewDialog'),request=++previewRequest;if(recordHistory&&(!dialog.open||history.state?.preview!==p)){let previewDepth=dialog.open?(history.state?.previewDepth||1)+1:1;history.pushState({path,preview:p,previewDepth},'',location.href)}$('#previewTitle').textContent=p.split('/').pop();clearPreviewSources();img.hidden=textView.hidden=markdown.hidden=error.hidden=true;textView.textContent='';markdown.replaceChildren();if(!dialog.open)dialog.showModal();let url='/api/preview?path='+encodeURIComponent(p);if(imagePreviewPattern.test(p)){img.onload=()=>{if(request===previewRequest)img.hidden=false};img.onerror=()=>{if(request===previewRequest){error.textContent=t('previewFailed');error.hidden=false}};img.src=url;return}if(videoPreviewPattern.test(p)||audioPreviewPattern.test(p)){let media=$(videoPreviewPattern.test(p)?'#previewVideo':'#previewAudio');media.onerror=()=>{if(request===previewRequest){media.hidden=true;error.textContent=t('mediaFailed');error.hidden=false}};media.hidden=false;media.src=url;media.load();return}try{let response=await fetch(url);if(!response.ok)throw Error();let body=await response.text();if(request!==previewRequest)return;if(/\.(?:md|markdown)$/i.test(p)){markdownInto(body,markdown,p);markdown.hidden=false}else{textView.textContent=body;textView.hidden=false}}catch{if(request===previewRequest){error.textContent=t('previewFailed');error.hidden=false}}}
$('#previewDialog').addEventListener('close',()=>{previewRequest++;clearPreviewSources();if(history.state?.preview)history.go(-Math.max(1,history.state.previewDepth||1))});
$('#previewDialog').addEventListener('click',event=>{let dialog=$('#previewDialog'),rect=dialog.getBoundingClientRect();if(event.target===dialog&&(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom))dialog.close()});
function openItem(p,d){d?load(p):download(p)}function download(p){location.href='/api/download?path='+encodeURIComponent(p)}
function promptBox(title,value,cb){$('#dlgTitle').textContent=title;$('#dlgInput').value=value||'';$('#dlgOk').onclick=()=>{let v=$('#dlgInput').value.trim();if(v){dialog.close();cb(v)}};dialog.showModal();setTimeout(()=>{$('#dlgInput').focus();$('#dlgInput').select()},30)}
function newFolder(){promptBox(t('newFolderName'),'',async n=>{try{await api('/api/mkdir',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path,name:n})});toast(t('folderCreated'));load()}catch(e){toast(e.message,true)}})}
function renameItem(old){promptBox(t('rename'),old,async n=>{try{await api('/api/rename',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path,name:old,new_name:n})});toast(t('renamed'));load()}catch(e){toast(e.message,true)}})}
async function removeItem(name){if(!confirm(t('deleteAsk',name)))return;try{await api('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path,name})});toast(t('deleted'));load()}catch(e){toast(e.message,true)}}
function pickFiles(){$('#picker').click()}$('#picker').onchange=e=>upload(e.target.files);
function showUpload(files){uploadActive=true;$('#uploadTitle').textContent=t('uploading');$('#uploadList').className='upload-list';$('#uploadList').innerHTML=Array.from(files).map((file,i)=>'<div class="upload-item" id="upload-item-'+i+'"><div class="upload-item-head"><span class="upload-item-name">'+esc(file.name)+'</span><span class="upload-item-status" id="upload-status-'+i+'">'+t('queued')+'</span></div><div class="upload-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="upload-fill" id="upload-fill-'+i+'"></div></div><div class="upload-stats" id="upload-stats-'+i+'">0%</div></div>').join('');$('#uploadPanel').hidden=false}
function updateFileUpload(index,percent,loaded,total){let p=Math.max(0,Math.min(100,percent)),fill=$('#upload-fill-'+index),stats=$('#upload-stats-'+index);fill.style.width=p+'%';stats.textContent=(total?human(loaded)+' / '+human(total)+' · ':'')+Math.round(p)+'%';fill.parentElement.setAttribute('aria-valuenow',Math.round(p))}
function setFileStatus(index,key,complete=false,size=0){let status=$('#upload-status-'+index);status.textContent=t(key);status.className='upload-item-status '+(complete?'complete':key==='failed'?'failed':'');if(complete){$('#upload-fill-'+index).classList.add('complete');updateFileUpload(index,100,size,size)}}
function hideUpload(){uploadActive=false;$('#uploadPanel').hidden=true}
function sendUpload(file,index){return new Promise((resolve,reject)=>{let form=new FormData();form.append('path',path);form.append('files',file,file.name);let x=new XMLHttpRequest();x.open('POST','/api/upload');x.upload.onprogress=e=>{if(e.lengthComputable){updateFileUpload(index,e.loaded/e.total*100,e.loaded,e.total);if(e.loaded>=e.total)setFileStatus(index,'processing')}};x.onload=()=>{let d;try{d=JSON.parse(x.responseText||'{}')}catch{d={error:x.statusText}}if(x.status>=200&&x.status<300)resolve(d);else reject(Error(d.error||x.statusText||t('requestFailed')))};x.onerror=()=>reject(Error(t('requestFailed')));x.onabort=()=>reject(Error(t('requestFailed')));x.send(form)})}
async function upload(files){if(!writable||!files.length||uploadActive)return;showUpload(files);let done=0,failed=0;for(let i=0;i<files.length;i++){setFileStatus(i,'uploadingFile');try{await sendUpload(files[i],i);setFileStatus(i,'complete',true,files[i].size);done++}catch(e){setFileStatus(i,'failed');failed++}}try{$('#picker').value='';await load()}catch(e){toast(e.message,true)}setTimeout(()=>{hideUpload();toast(t('uploadSummary',done,files.length,failed),failed>0)},3000)}
let drag=0;addEventListener('dragenter',e=>{e.preventDefault();if(writable){drag++;$('#drop').classList.add('on')}});addEventListener('dragleave',e=>{e.preventDefault();if(--drag<=0){drag=0;$('#drop').classList.remove('on')}});addEventListener('dragover',e=>e.preventDefault());addEventListener('drop',e=>{e.preventDefault();drag=0;$('#drop').classList.remove('on');upload(e.dataTransfer.files)});let initialPath=new URLSearchParams(location.search).get('path')||'';history.replaceState({path:initialPath},'',location.href);addEventListener('popstate',event=>{let state=event.state||{path:new URLSearchParams(location.search).get('path')||''},dialog=$('#previewDialog');if(state.preview){preview(state.preview,false);return}if(dialog.open)dialog.close();if(state.path!==path)load(state.path,false)});load(initialPath,false);
</script></body></html>'''


def safe_name(name: str) -> str:
    if not name or name in {".", ".."} or "/" in name or "\\" in name or "\0" in name:
        raise ValueError("Invalid file name.")
    return name


class LimitedInput:
    """Read at most Content-Length bytes while supporting a pushback buffer."""

    def __init__(self, stream, length: int):
        self.stream = stream
        self.remaining = length
        self.buffer = b""

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self.buffer) + self.remaining
        output = self.buffer[:size]
        self.buffer = self.buffer[len(output):]
        needed = size - len(output)
        if needed > 0 and self.remaining > 0:
            chunk = self.stream.read(min(needed, self.remaining))
            self.remaining -= len(chunk)
            output += chunk
        return output

    def unread(self, data: bytes):
        self.buffer = data + self.buffer

    def readline(self, limit: int) -> bytes:
        output = bytearray()
        while len(output) < limit:
            char = self.read(1)
            if not char:
                return bytes(output)
            output += char
            if char == b"\n":
                return bytes(output)
        raise ValueError("A multipart header line is too large.")


def disposition_parameters(value: str):
    params = {}
    pattern = r";\s*([!#$%&'*+\-.^_`|~0-9A-Za-z]+)\s*=\s*(?:\"((?:\\.|[^\"])*)\"|([^;]*))"
    for match in re.finditer(pattern, value):
        key = match.group(1).lower()
        if match.group(2) is not None:
            params[key] = re.sub(r"\\(.)", r"\1", match.group(2))
        else:
            params[key] = match.group(3).strip()
    if "filename" not in params and "filename*" in params:
        encoded = params["filename*"]
        try:
            charset, _language, encoded_name = encoded.split("'", 2)
            params["filename"] = urllib.parse.unquote(encoded_name, encoding=charset or "utf-8", errors="strict")
        except (LookupError, UnicodeError, ValueError):
            raise ValueError("Invalid encoded upload file name.")
    return params


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

    def send_file(self, target, preview):
        size = target.stat().st_size
        range_header = None if self.headers.get("If-Range") else self.headers.get("Range")
        start, end = 0, size - 1
        if range_header:
            match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
            if match and (match.group(1) or match.group(2)):
                if match.group(1):
                    start = int(match.group(1))
                    end = min(int(match.group(2)), size - 1) if match.group(2) else size - 1
                else:
                    suffix = int(match.group(2))
                    start = max(0, size - suffix)
                valid = size > 0 and start < size and end >= start
                if not match.group(1):
                    valid = valid and suffix > 0
            else:
                valid = False
            if not valid:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return

        content_type = PREVIEW_TYPES.get(target.suffix.lower()) if preview else mimetypes.guess_type(target.name)[0]
        self.send_response(206 if range_header else 200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Disposition", ("inline" if preview else "attachment") + "; filename*=UTF-8''" + urllib.parse.quote(target.name))
        self.send_header("Accept-Ranges", "bytes")
        if range_header:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        if preview:
            self.send_header("Content-Security-Policy", "sandbox; default-src 'none'")
            self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(end - start + 1 if range_header else size))
        self.end_headers()
        with target.open("rb") as source:
            if range_header:
                source.seek(start)
                remaining = end - start + 1
                while remaining:
                    chunk = source.read(min(1024 * 1024, remaining))
                    if not chunk: break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
            else:
                shutil.copyfileobj(source, self.wfile)

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
            elif parsed.path in ("/api/download", "/api/preview"):
                target = self.resolve(query.get("path", [""])[0])
                if not target.is_file(): raise ValueError("The requested path is not a file.")
                preview = parsed.path == "/api/preview"
                if preview and target.suffix.lower() not in PREVIEW_TYPES:
                    raise ValueError("This file cannot be previewed.")
                self.send_file(target, preview)
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

    def multipart_boundary(self, content_type: str) -> bytes:
        if content_type.split(";", 1)[0].strip().lower() != "multipart/form-data":
            raise ValueError("A multipart/form-data request is required.")
        match = re.search(r'(?:^|;)\s*boundary=(?:"([^"]+)"|([^;]+))', content_type, re.IGNORECASE)
        if not match:
            raise ValueError("The multipart boundary is missing.")
        value = (match.group(1) or match.group(2)).strip()
        try:
            boundary = value.encode("ascii")
        except UnicodeEncodeError:
            raise ValueError("The multipart boundary must be ASCII.")
        if not boundary or len(boundary) > 200 or b"\r" in boundary or b"\n" in boundary:
            raise ValueError("The multipart boundary is invalid.")
        return boundary

    def multipart_headers(self, reader: LimitedInput):
        headers, total = {}, 0
        while True:
            line = reader.readline(8192)
            if not line: raise ValueError("The upload was interrupted while reading multipart headers.")
            total += len(line)
            if total > 65536: raise ValueError("Multipart headers are too large.")
            if line == b"\r\n": return headers
            if not line.endswith(b"\r\n") or b":" not in line:
                raise ValueError("A multipart header is malformed.")
            raw_name, raw_value = line[:-2].split(b":", 1)
            try:
                name = raw_name.decode("ascii").strip().lower()
                value = raw_value.strip().decode("utf-8")
            except UnicodeDecodeError:
                try:
                    name = raw_name.decode("ascii").strip().lower()
                    value = raw_value.strip().decode("latin-1")
                except UnicodeDecodeError:
                    raise ValueError("A multipart header has an invalid encoding.")
            headers[name] = value

    def stream_multipart_part(self, reader: LimitedInput, boundary: bytes, output):
        marker = b"\r\n--" + boundary
        buffer = b""
        while True:
            chunk = reader.read(1024 * 1024)
            if not chunk:
                raise ValueError("The upload was interrupted before the multipart boundary.")
            buffer += chunk
            search_from = 0
            while True:
                index = buffer.find(marker, search_from)
                if index < 0:
                    keep = len(marker) + 2
                    if len(buffer) > keep:
                        output.write(buffer[:-keep])
                        buffer = buffer[-keep:]
                    break
                suffix_at = index + len(marker)
                if len(buffer) < suffix_at + 2:
                    if index:
                        output.write(buffer[:index])
                        buffer = buffer[index:]
                    break
                suffix = buffer[suffix_at:suffix_at + 2]
                if suffix in (b"\r\n", b"--"):
                    output.write(buffer[:index])
                    reader.unread(buffer[suffix_at + 2:])
                    return suffix == b"--"
                search_from = index + 1

    def parse_multipart(self, length: int, boundary: bytes):
        reader = LimitedInput(self.rfile, length)
        opening = reader.readline(len(boundary) + 6)
        if opening != b"--" + boundary + b"\r\n":
            raise ValueError("The multipart request has an invalid opening boundary.")
        fields, files = {}, []
        try:
            final = False
            while not final:
                headers = self.multipart_headers(reader)
                disposition = headers.get("content-disposition", "")
                if disposition.split(";", 1)[0].strip().lower() != "form-data":
                    raise ValueError("A multipart part is missing form-data disposition.")
                params = disposition_parameters(disposition)
                field_name = params.get("name")
                filename = params.get("filename")
                if filename is not None:
                    if len(files) >= 1000: raise ValueError("Too many files in one upload request.")
                    filename = safe_name(filename.replace("\\", "/").rsplit("/", 1)[-1])
                    temporary = tempfile.NamedTemporaryFile(prefix="simple-http-file-browser-", delete=False)
                    temporary_path = Path(temporary.name)
                    files.append((filename, temporary_path))
                    try:
                        final = self.stream_multipart_part(reader, boundary, temporary)
                    finally:
                        temporary.close()
                else:
                    with tempfile.SpooledTemporaryFile(max_size=65536) as field:
                        final = self.stream_multipart_part(reader, boundary, field)
                        if field.tell() > 1024 * 1024: raise ValueError("A multipart form field is too large.")
                        field.seek(0)
                        if field_name:
                            fields[field_name] = field.read().decode("utf-8")
                if final:
                    trailer = reader.read(2)
                    if trailer not in (b"", b"\r\n"):
                        raise ValueError("The multipart closing boundary is malformed.")
                    while reader.read(1024 * 1024): pass
            return fields, files
        except Exception:
            for _name, temporary_path in files:
                temporary_path.unlink(missing_ok=True)
            raise

    def store_uploaded_file(self, source: Path, target: Path, overwrite: bool):
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".upload", dir=target.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as output, source.open("rb") as uploaded:
                shutil.copyfileobj(uploaded, output, length=1024 * 1024)
            if overwrite:
                os.replace(temporary, target)
            else:
                try:
                    os.link(temporary, target)
                except FileExistsError:
                    raise FileExistsError(f"{target.name}: an item with the same name already exists.")
                temporary.unlink()
        finally:
            temporary.unlink(missing_ok=True)

    def handle_upload(self):
        length = int(self.headers.get("Content-Length", "0"))
        max_bytes = self.config["max_upload_mb"] * 1024 * 1024
        if length <= 0 or length > max_bytes: raise ValueError(f"Uploads are limited to {self.config['max_upload_mb']} MB per request.")
        boundary = self.multipart_boundary(self.headers.get("Content-Type", ""))
        fields, files = self.parse_multipart(length, boundary)
        try:
            parent = self.resolve(fields.get("path", ""))
            if not parent.is_dir(): raise ValueError("The destination folder is invalid.")
            overwrite = self.config["overwrite"]
            targets, seen = [], set()
            for name, _source in files:
                relative = (parent.relative_to(self.config["root"]) / name).as_posix()
                target = self.resolve(relative, must_exist=False)
                if target in seen and not overwrite:
                    raise FileExistsError(f"{name}: an item with the same name already exists.")
                seen.add(target)
                if target.exists() and (target.is_dir() or not overwrite):
                    raise FileExistsError(f"{name}: an item with the same name already exists.")
                targets.append(target)
            for (_name, source), target in zip(files, targets):
                self.store_uploaded_file(source, target, overwrite)
            self.send_json({"ok": True, "count": len(files)})
        finally:
            for _name, source in files:
                source.unlink(missing_ok=True)


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
