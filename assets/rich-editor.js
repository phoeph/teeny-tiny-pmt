function createRichEditor(targetId, options){
  const opts = options || {};
  const container = document.getElementById(targetId);
  if (!container) return null;
  const toolbar = document.createElement('div');
  toolbar.style.display = 'flex'; toolbar.style.flexWrap = 'wrap'; toolbar.style.gap = '8px'; toolbar.style.marginBottom = '8px';
  const mkIconBtn = function(svg, title, onClick){ const b=document.createElement('button'); b.type='button'; b.title=title||''; b.style.padding='6px'; b.style.width='32px'; b.style.height='32px'; b.style.display='inline-flex'; b.style.alignItems='center'; b.style.justifyContent='center'; b.style.border='1px solid var(--border-color)'; b.style.borderRadius='6px'; b.style.background='var(--bg-surface)'; b.style.cursor='pointer'; b.innerHTML=svg; b.onclick=function(){ onClick && onClick(); editor.focus(); }; return b; };
  const icons = {
    B: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M7 5h6.5a3.5 3.5 0 0 1 0 7H7V5zm0 9h7a3 3 0 0 1 0 6H7v-6z"/></svg>',
    I: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M9 5h10v2H15l-6 12h5v2H4v-2h6l6-12H9z"/></svg>',
    U: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M6 5h2v6a4 4 0 1 0 8 0V5h2v6a6 6 0 1 1-12 0V5zm0 13h12v2H6z"/></svg>',
    H1: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M4 5h2v6h8V5h2v14h-2v-6H6v6H4z"/><path fill="var(--text-secondary)" d="M18 7h2v12h-2z"/></svg>',
    H2: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M4 5h2v6h8V5h2v14h-2v-6H6v6H4z"/><path fill="var(--text-secondary)" d="M16 9h6v2h-4l-2 2v2h6v2h-8v-4l2-2V9z"/></svg>',
    UL: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M4 6h2v2H4V6zm5 2h11V6H9v2zm-5 5h2v2H4v-2zm5 2h11v-2H9v2zm-5 5h2v2H4v-2zm5 2h11v-2H9v2z"/></svg>',
    OL: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M5 6h2v2H5V6zm4 2h12V6H9v2zm-4 5h2v2H5v-2zm4 2h12v-2H9v2zm-4 5h2v2H5v-2zm4 2h12v-2H9v2z"/></svg>',
    LINK: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M7.5 12a4.5 4.5 0 0 1 1.3-3.2l3-3a4.5 4.5 0 1 1 6.4 6.4l-1.2 1.2-1.4-1.4 1.2-1.2a2.5 2.5 0 1 0-3.5-3.5l-3 3A2.5 2.5 0 1 0 11 14.5l1.4 1.4A4.5 4.5 0 0 1 7.5 12z"/></svg>',
    QUOTE: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M6 8h12v2H6zm0 4h10v2H6z"/></svg>',
    CODE: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M9 7L3 12l6 5v-3l-3-2 3-2V7zm6 0v3l3 2-3 2v3l6-5-6-5z"/></svg>',
    LEFT: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M4 5h16v2H4zM4 9h12v2H4zM4 13h16v2H4zM4 17h12v2H4z"/></svg>',
    CENTER: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M4 5h16v2H4zM6 9h12v2H6zM4 13h16v2H4zM6 17h12v2H6z"/></svg>',
    RIGHT: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M4 5h16v2H4zM8 9h12v2H8zM4 13h16v2H4zM8 17h12v2H8z"/></svg>',
    UNDO: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M12 5v4H7l5 5v-3h3a4 4 0 1 1-3.9 5h2a2 2 0 1 0 1.9-3H12V5z"/></svg>',
    REDO: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M12 5v4h3a4 4 0 1 1-3.9 5h2a2 2 0 1 0 1.9-3H12v3l5-5-5-5z"/></svg>',
    IMG: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M4 6h16v12H4V6zm2 2v8h12V8H6zm2 6l3-4 3 4H8zm8-6a2 2 0 1 1-4 0a2 2 0 0 1 4 0z"/></svg>',
    ATTACH: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M7 7a5 5 0 0 1 7.07 0l4.24 4.24l-1.41 1.41L12.66 8.41a3 3 0 0 0-4.24 4.24l6.36 6.36a4 4 0 1 1-5.66-5.66l1.41 1.41a2 2 0 1 0 2.83 2.83L9.83 12.1A5 5 0 0 1 7 7z"/></svg>',
    COLOR: '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="var(--text-secondary)" d="M4 5h16v2H4zM4 9h16v2H4zM4 13h16v2H4z"/></svg>'
  };
  const mkCmd = (cmd)=> mkIconBtn(icons[cmd], cmd, ()=> document.execCommand(cmd.toLowerCase(), false, null));
  const mkHeading = function(level){ return mkIconBtn(icons['H'+level], 'H'+level, ()=> document.execCommand('formatBlock', false, 'H'+level)); };
  const mkLink = function(){ return mkIconBtn(icons.LINK, 'Link', ()=>{ const url=prompt('请输入链接URL'); if(url){ document.execCommand('createLink', false, url); } }); };
  const mkQuote = function(){ return mkIconBtn(icons.QUOTE, 'Quote', ()=> document.execCommand('formatBlock', false, 'BLOCKQUOTE')); };
  const mkCode = function(){ return mkIconBtn(icons.CODE, 'Code', ()=> document.execCommand('formatBlock', false, 'PRE')); };
  const mkAlign = function(which){ return mkIconBtn(icons[which.toUpperCase()], which, ()=> document.execCommand('justify'+which, false, null)); };
  const mkUndo = function(){ return mkIconBtn(icons.UNDO, 'Undo', ()=> document.execCommand('undo', false, null)); };
  const mkRedo = function(){ return mkIconBtn(icons.REDO, 'Redo', ()=> document.execCommand('redo', false, null)); };
  const mkImage = function(){ const file=document.createElement('input'); file.type='file'; file.accept='image/*'; file.style.display='none'; const btn = mkIconBtn(icons.IMG, 'Image', ()=> file.click()); file.onchange=async function(){ if(!file.files.length) return; let f=file.files[0]; try{ f = await compressImage(f); }catch(_){} const url = await __uploadFile(f, opts); if(url){ document.execCommand('insertImage', false, url); } }; const wrap=document.createElement('span'); wrap.appendChild(btn); wrap.appendChild(file); return wrap; };
  const mkAttach = function(){ const file=document.createElement('input'); file.type='file'; file.style.display='none'; const btn = mkIconBtn(icons.ATTACH, 'Attach', ()=> file.click()); file.onchange=async function(){ if(!file.files.length) return; const f=file.files[0]; const url = await __uploadFile(f, opts); if(url){ const a=document.createElement('a'); a.href=url; a.target='_blank'; a.textContent=f.name; const sel=window.getSelection(); if(sel&&sel.rangeCount){ const range=sel.getRangeAt(0); range.insertNode(a); } else { editor.appendChild(a); } } }; const wrap=document.createElement('span'); wrap.appendChild(btn); wrap.appendChild(file); return wrap; };
  const mkColor = function(){
    const btn = mkIconBtn(icons.COLOR, 'Color', ()=> showColorPanel(btn));
    const wrap=document.createElement('span'); wrap.appendChild(btn); return wrap;
  };
  function showColorPanel(anchor){
    const colors = ['#111827','#374151','#6b7280','#9ca3af','#f3f4f6','#2563eb','#10b981','#ef4444','#f59e0b','#8b5cf6','#ec4899','#14b8a6','#0ea5e9'];
    let panel = document.getElementById('colorPanel');
    if(!panel){ panel = document.createElement('div'); panel.id='colorPanel'; panel.style.position='absolute'; panel.style.zIndex='10000'; panel.style.background='var(--bg-surface)'; panel.style.border='1px solid var(--border-color)'; panel.style.borderRadius='8px'; panel.style.boxShadow='0 10px 30px rgba(0,0,0,0.15)'; panel.style.padding='8px'; panel.style.width='200px'; panel.style.maxWidth='200px'; panel.style.display='grid'; panel.style.gridTemplateColumns='repeat(7, 1fr)'; panel.style.gap='6px'; document.body.appendChild(panel); }
    panel.innerHTML='';
    const rect = anchor.getBoundingClientRect(); panel.style.left = (rect.left + window.scrollX) + 'px'; panel.style.top = (rect.bottom + window.scrollY + 6) + 'px';
    colors.forEach(function(c){ const cell=document.createElement('div'); cell.style.width='22px'; cell.style.height='22px'; cell.style.borderRadius='4px'; cell.style.border='1px solid var(--border-color)'; cell.style.background=c; cell.title=c; cell.onmouseenter=function(){ try{ document.execCommand('foreColor', false, c); } catch (e) {} }; cell.onclick=function(){ try{ document.execCommand('foreColor', false, c); } catch (e) {} panel.style.display='none'; }; panel.appendChild(cell); });
    panel.onmouseleave = function(){ panel.style.display='none'; };
    panel.style.display='grid';
  }
  const editor = document.createElement('div'); editor.contentEditable = 'true'; editor.style.minHeight='140px'; editor.style.border='1px solid var(--border-color)'; editor.style.borderRadius='8px'; editor.style.padding='8px'; editor.style.background='var(--bg-surface)'; editor.style.outline='none';
  const saveBar=document.createElement('div'); saveBar.style.display='flex'; saveBar.style.justifyContent='flex-end'; saveBar.style.marginTop='8px'; const saveBtn=document.createElement('button'); saveBtn.type='button'; saveBtn.textContent= opts.saveText || '保存'; saveBtn.style.padding='8px 16px'; saveBtn.style.border='none'; saveBtn.style.borderRadius='6px'; saveBtn.style.background='var(--primary)'; saveBtn.style.color='var(--bg-surface)'; saveBtn.onclick=function(){ if(typeof opts.onSave==='function'){ opts.onSave(getHTML()); } };
  saveBar.appendChild(saveBtn);
  [mkIconBtn(icons.B,'Bold', ()=> document.execCommand('bold', false, null)), mkIconBtn(icons.I,'Italic', ()=> document.execCommand('italic', false, null)), mkIconBtn(icons.U,'Underline', ()=> document.execCommand('underline', false, null)), mkHeading(1), mkHeading(2), mkIconBtn(icons.UL,'UL', ()=> document.execCommand('insertUnorderedList', false, null)), mkIconBtn(icons.OL,'OL', ()=> document.execCommand('insertOrderedList', false, null)), mkLink(), mkQuote(), mkCode(), mkColor(), mkAlign('Left'), mkAlign('Center'), mkAlign('Right'), mkUndo(), mkRedo(), mkImage(), mkAttach()].forEach(el=> toolbar.appendChild(el));
  container.innerHTML=''; container.appendChild(toolbar); container.appendChild(editor); container.appendChild(saveBar);
  (async function preloadUsers(){ try{ const API=(window.API)||'http://localhost:8000/api'; const token=localStorage.getItem('token')||''; const r=await fetch(`${API}/users`, { headers:{ Authorization:`Bearer ${token}` } }); if(r.ok){ const list=await r.json(); window.__assigneesIndex = Array.isArray(list)? list.map(function(u){ return { name: u.full_name || u.username || u.email_prefix, prefix: u.email_prefix || u.username || '', email: u.email || '' }; }) : null; } }catch(_){ } })();
  function setHTML(html){ editor.innerHTML = String(html||''); }
  function getHTML(){ return editor.innerHTML; }
  function collapse(){ editor.innerHTML=''; editor.style.minHeight='0px'; editor.style.height='0px'; editor.style.padding='0'; saveBar.style.display='none'; }
  function expand(){ editor.style.minHeight='140px'; editor.style.height=''; editor.style.padding='8px'; saveBar.style.display='flex'; }
  toolbar.addEventListener('click', function(){ if((editor.style.height||'')==='0px'){ expand(); } });
  // @ 提及用户：检测输入并显示建议面板
  editor.addEventListener('input', function(){ detectMention(); });
  editor.addEventListener('keyup', function(e){ if(e.key==='@' || /^[a-zA-Z0-9_\-]$/.test(e.key)) detectMention(); });
  editor.addEventListener('paste', async function(e){
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    let hasImage = false;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        e.preventDefault();
        hasImage = true;
        let file = items[i].getAsFile();
        if(file){
           try{ file = await compressImage(file); }catch(_){}
           const url = await __uploadFile(file, opts);
           if(url){
             document.execCommand('insertImage', false, url);
           }
        }
      }
    }
   });
   editor.addEventListener('dragover', function(e){ e.preventDefault(); });
   editor.addEventListener('drop', async function(e){
     e.preventDefault();
     const files = e.dataTransfer.files;
     if (files && files.length > 0) {
         for (let i = 0; i < files.length; i++) {
             const file = files[i];
             if (file.type.startsWith('image/')) {
                 let f = file;
                 try{ f = await compressImage(f); }catch(_){}
                 const url = await __uploadFile(f, opts);
                 if(url){
                     document.execCommand('insertImage', false, url);
                 }
             }
         }
     }
   });
   function detectMention(){ try{ const sel=window.getSelection(); if(!sel||!sel.rangeCount) return; const range=sel.getRangeAt(0); const node=range.startContainer; const txt=(node && node.textContent) ? node.textContent : ''; const atIdx=txt.lastIndexOf('@'); if(atIdx<0){ hideMentionPanel(); return; } const q = txt.slice(atIdx+1).trim(); showMentionPanel(range, q); }catch(_){}}
  function caretRect(range){ try{ const r=range.cloneRange(); r.collapse(true); const rect=r.getBoundingClientRect(); return rect; }catch(_){ return { left:0, bottom:0 }; }}
  function getUserIndex(){ const a = (window.__assigneesIndex && Array.isArray(window.__assigneesIndex))? window.__assigneesIndex.slice() : []; return a; }
  function showMentionPanel(range, q){ let el=document.getElementById('mentionPanel'); if(!el){ el=document.createElement('div'); el.id='mentionPanel'; el.className='dropdown'; document.body.appendChild(el); } const rect=caretRect(range); const list=getUserIndex(); const query=String(q||'').toLowerCase(); const filtered = query? list.filter(function(u){ return String(u.name||'').toLowerCase().includes(query) || String(u.prefix||'').toLowerCase().includes(query) || String(u.email||'').toLowerCase().includes(query); }) : list.slice(0,10); el.style.display='block'; el.style.left=(rect.left + window.scrollX) + 'px'; el.style.top=(rect.bottom + window.scrollY + 6) + 'px'; el.style.width='240px'; el.innerHTML = filtered.map(function(u){ const tip=u.prefix||u.email||''; const pref = u.prefix||''; return '<div class="dropdown-item" title="'+tip+'" data-name="'+(u.name||pref)+'" data-prefix="'+pref+'">@'+(u.name||pref)+'</div>'; }).join(''); el.querySelectorAll('.dropdown-item').forEach(function(it){ it.onclick=function(){ insertMention(this.getAttribute('data-name')||'', this.getAttribute('data-prefix')||''); hideMentionPanel(); }; }); el.onmousedown=function(e){ e.preventDefault(); }; document.addEventListener('mousedown', function onDoc(e){ const inside=e.target===el || el.contains(e.target); if(!inside){ hideMentionPanel(); document.removeEventListener('mousedown', onDoc); } }); }
  function hideMentionPanel(){ const el=document.getElementById('mentionPanel'); if(el) el.style.display='none'; }
  function insertMention(name, prefix){ try{ const sel=window.getSelection(); if(!sel||!sel.rangeCount) return; const range=sel.getRangeAt(0); const node=range.startContainer; const txt=(node && node.textContent)? node.textContent : ''; const atIdx=txt.lastIndexOf('@'); if(atIdx>=0){ const r=document.createRange(); r.setStart(node, Math.max(0, atIdx)); r.setEnd(node, range.startOffset); r.deleteContents(); } const span=document.createElement('span'); span.className='mention'; span.textContent='@'+name; range.insertNode(span); if(prefix){ const hidden=document.createElement('span'); hidden.style.display='none'; hidden.textContent='@'+prefix; range.insertNode(hidden); } range.setStartAfter(span); range.setEndAfter(span); sel.removeAllRanges(); sel.addRange(range); }catch(_){} }
  // 包装保存：保存后折叠并清空
  if(typeof opts.onSave==='function'){
    const orig = opts.onSave;
    saveBtn.onclick = async function(){ try{ const res = await orig(getHTML()); if(res!==false){ collapse(); } } catch (e) { collapse(); } };
  }
  return { setHTML, getHTML, focus: ()=> editor.focus(), collapse, expand };
}

async function __uploadFile(file, opts){ try{ const API=(window.API)||'http://localhost:8000/api'; const token=localStorage.getItem('token')||''; const et = opts.entityType || 'project'; const eid = opts.entityId || 0; const res0 = await fetch(`${API}/comments/`, { method:'POST', headers:{ 'Content-Type':'application/json', Authorization:`Bearer ${token}` }, body: JSON.stringify({ entity_type: et, entity_id: eid, content: '富文本附件' }) }); if(!res0.ok) return null; const data=await res0.json(); const cid=data.id; const fd=new FormData(); fd.append('file', file); const rr=await fetch(`${API}/attachments/comments/${cid}`, { method:'POST', headers:{ Authorization:`Bearer ${token}` }, body: fd }); if(!rr.ok) return null; const info=await rr.json(); const attId = info && (info.id || info[0]?.id);
  return `${API}/attachments/${attId}`; } catch(_){ return null; } }

async function compressImage(file, maxWidth=1920, quality=0.8) {
  if (!file || !file.type.startsWith('image/')) return file;
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target.result;
      img.onload = () => {
        let width = img.width;
        let height = img.height;
        if (width > maxWidth) {
          height = Math.round(height * (maxWidth / width));
          width = maxWidth;
        }
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        canvas.toBlob((blob) => {
          if (!blob) { resolve(file); return; }
          const newFile = new File([blob], file.name.replace(/\.[^/.]+$/, "") + ".jpg", {
            type: 'image/jpeg',
            lastModified: Date.now(),
          });
          resolve(newFile);
        }, 'image/jpeg', quality);
      };
      img.onerror = () => resolve(file);
    };
    reader.onerror = () => resolve(file);
  });
}
