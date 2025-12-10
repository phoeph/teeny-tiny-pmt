;(function(){
  const API = (typeof window!=='undefined' && window.API) ? window.API : 'http://localhost:8000/api';
  const token = (typeof localStorage!=='undefined') ? localStorage.getItem('token') : null;

  function ensureContainer(){ let c=document.getElementById('left-sidebar'); if(c) return c; c=document.createElement('div'); c.id='left-sidebar'; document.body.appendChild(c); return c; }
  function setBodyPadding(collapsed){ try{ document.body.classList.add('with-left-sidebar'); if(collapsed){ document.body.classList.add('collapsed'); } else { document.body.classList.remove('collapsed'); } }catch(_){ }
  }
  function currentKey(){ try{ const p=location.pathname.split('/').pop()||''; const base=p.split('?')[0]; return base||''; }catch(_){ return ''; } }
  async function fetchMe(){ try{ const r=await fetch(`${API}/auth/me`, { headers:{ Authorization:`Bearer ${token}` } }); if(!r.ok) throw new Error('auth'); const raw=await r.json(); return (raw && raw.user) ? raw.user : raw; } catch(e){ return null; } }
  function hasAccess(me, key){ try{ return true; }catch(_){ return true; } }
  function item(href, label, key){ const a=document.createElement('a'); a.href=href; a.className='menu-item'; a.setAttribute('data-key', key); const icon = (key==='projects.html')
      ? '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M10 4l2 2h8v12H4V4h6z"/></svg>'
      : (key==='data-management.html')
        ? '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M3 3h18v18H3V3zm2 2v4h14V5H5zm14 6H5v8h14v-8z"/></svg>'
        : '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M3 3h8v8H3V3zm10 0h8v8h-8V3zM3 13h8v8H3v-8zm10 0h8v8h-8v-8z"/></svg>';
    a.innerHTML= icon + `<span>${label}</span>`; return a; }

  function renderSidebar(container, me){ const wrap=document.createElement('div'); wrap.className='left-sidebar';
    const brand=document.createElement('div'); brand.className='brand'; brand.innerHTML=`<svg viewBox="0 0 24 24"><path fill="currentColor" d="M3 3h8v8H3V3zm10 0h8v8h-8V3zM3 13h8v8H3v-8zm10 0h8v8h-8v-8z"/></svg><span>导航</span>`; wrap.appendChild(brand);
    const menu=document.createElement('div'); menu.className='menu';
    const items=[ item('projects.html','项目列表','projects.html'), item('data-management.html','数据管理','data-management.html') ];
    const cur=currentKey(); items.forEach(function(a){ if(a.getAttribute('data-key')===cur){ a.classList.add('active'); } const ok=hasAccess(me, a.getAttribute('data-key')); if(!ok){ a.classList.add('disabled'); a.title='无权限'; } menu.appendChild(a); });
    wrap.appendChild(menu);
    const footer=document.createElement('div'); footer.className='footer'; footer.innerHTML=`<button class="toggle" id="lsToggle" title="展开/折叠"><svg viewBox="0 0 24 24"><path fill="currentColor" d="M9 6l-4 6 4 6V6zm10 0l-4 6 4 6V6z"/></svg></button>`; wrap.appendChild(footer);
    container.innerHTML=''; container.appendChild(wrap);
    try{ const collapsed = localStorage.getItem('__left_sidebar_collapsed')==='true'; if(collapsed) wrap.classList.add('collapsed'); setBodyPadding(collapsed); document.getElementById('lsToggle').onclick=function(){ const now=wrap.classList.toggle('collapsed'); localStorage.setItem('__left_sidebar_collapsed', now? 'true':'false'); setBodyPadding(now); }; }catch(_){ }
  }

  document.addEventListener('DOMContentLoaded', async function(){ try{ const c=ensureContainer(); const me=await fetchMe(); renderSidebar(c, me); }catch(e){ try{ const c=ensureContainer(); renderSidebar(c, null); }catch(_){ } } });
})();
