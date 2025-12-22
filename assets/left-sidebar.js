;(function(){
  const API = (typeof window!=='undefined' && window.API) ? window.API : 'http://localhost:8000/api';
  const token = (typeof localStorage!=='undefined') ? localStorage.getItem('token') : null;

  function ensureContainer(){ let c=document.getElementById('left-sidebar'); if(c) return c; c=document.createElement('div'); c.id='left-sidebar'; document.body.appendChild(c); return c; }
  function setBodyPadding(collapsed){ try{ document.body.classList.add('with-left-sidebar'); if(collapsed){ document.body.classList.add('collapsed'); } else { document.body.classList.remove('collapsed'); } }catch(_){ }
  }
  function currentKey(){ try{ const p=location.pathname.split('/').pop()||''; const base=p.split('?')[0]; return base||''; }catch(_){ return ''; } }
  async function fetchMe(){ try{ const r=await fetch(`${API}/auth/me`, { headers:{ Authorization:`Bearer ${token}` } }); if(!r.ok) throw new Error('auth'); const raw=await r.json(); return (raw && raw.user) ? raw.user : raw; } catch(e){ return null; } }
  function hasAccess(me, key){ try{ return true; }catch(_){ return true; } }
  
  function item(href, label, key){ 
    const a=document.createElement('a'); 
    a.href=href; 
    a.className='menu-item'; 
    a.setAttribute('data-key', key);
    a.setAttribute('data-tooltip', label);
    const icons = {
      'projects.html': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>',
      'reports.html': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10,9 9,9 8,9"></polyline></svg>',
      'data-statistics.html': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
      'data-management.html': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>',
      'default': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>'
    };
    const icon = icons[key] || icons['default'];
    a.innerHTML= icon + `<span>${label}</span>`; 
    return a; 
  }

  function renderSidebar(container, me){ 
    const wrap=document.createElement('div'); 
    wrap.className='left-sidebar';
    
    // Brand
    const brand=document.createElement('div'); 
    brand.className='brand'; 
    brand.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg><span>项目管理</span>`; 
    wrap.appendChild(brand);
    
    // Menu
    const menu=document.createElement('div'); 
    menu.className='menu';
    const items=[ 
      item('projects.html','项目列表','projects.html'), 
      item('reports.html','汇报管理','reports.html'),
      item('data-statistics.html','数据统计','data-statistics.html'),
      item('data-management.html','数据管理','data-management.html') 
    ];
    const cur=currentKey(); 
    items.forEach(function(a){ 
      if(a.getAttribute('data-key')===cur){ a.classList.add('active'); } 
      const ok=hasAccess(me, a.getAttribute('data-key')); 
      if(!ok){ a.classList.add('disabled'); a.title='无权限'; } 
      menu.appendChild(a); 
    });
    wrap.appendChild(menu);
    
    // Footer
    const footer=document.createElement('div'); 
    footer.className='footer'; 
    footer.innerHTML=`<button class="toggle" id="lsToggle" title="展开/折叠"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="11 17 6 12 11 7"></polyline><polyline points="18 17 13 12 18 7"></polyline></svg></button>`; 
    wrap.appendChild(footer);
    
    container.innerHTML=''; 
    container.appendChild(wrap);
    
    try{ 
      const collapsed = localStorage.getItem('__left_sidebar_collapsed')==='true'; 
      if(collapsed) wrap.classList.add('collapsed'); 
      setBodyPadding(collapsed); 
      document.getElementById('lsToggle').onclick=function(){ 
        const now=wrap.classList.toggle('collapsed'); 
        localStorage.setItem('__left_sidebar_collapsed', now? 'true':'false'); 
        setBodyPadding(now); 
      }; 
    }catch(_){ }
  }

  document.addEventListener('DOMContentLoaded', async function(){ 
    try{ 
      const c=ensureContainer(); 
      const me=await fetchMe(); 
      renderSidebar(c, me); 
    }catch(e){ 
      try{ 
        const c=ensureContainer(); 
        renderSidebar(c, null); 
      }catch(_){ } 
    } 
  });
})();
