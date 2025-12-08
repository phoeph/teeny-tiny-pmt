;(function(){
  const storeKey = '__page_history__';
  function now(){ const d=new Date(); const y=d.getFullYear(); const m=String(d.getMonth()+1).padStart(2,'0'); const da=String(d.getDate()).padStart(2,'0'); const hh=String(d.getHours()).padStart(2,'0'); const mm=String(d.getMinutes()).padStart(2,'0'); const ss=String(d.getSeconds()).padStart(2,'0'); return `${y}-${m}-${da} ${hh}:${mm}:${ss}`; }
  function load(){ try{ const raw=localStorage.getItem(storeKey)||'{}'; const obj=JSON.parse(raw); return obj&&typeof obj==='object'? obj : {}; }catch(_){ return {}; } }
  function save(obj){ try{ localStorage.setItem(storeKey, JSON.stringify(obj)); }catch(_){} }
  function init(key){ const db=load(); if(!db[key]){ db[key]=[]; save(db); } }
  function log(key, action, detail){ const db=load(); const list=db[key]||[]; list.unshift({ t: now(), a: String(action||''), d: String(detail||'') }); db[key]=list.slice(0,200); save(db); }
  function get(key){ const db=load(); return Array.isArray(db[key])? db[key] : []; }
  function renderTo(key, elId){ const el=document.getElementById(elId); if(!el) return; const items=get(key); el.textContent=''; if(!items.length){ el.textContent='暂无历史'; return; } const html=items.map(i=> `<span>${i.t}</span> · <span>${i.a}</span> · <span>${i.d}</span>`).join(' | '); el.innerHTML=html; }
  window.PageHistory = {
    init,
    log: function(action, detail){ const k=window.__pageHistoryKey||'default'; log(k, action, detail); },
    renderTo: function(elId){ const k=window.__pageHistoryKey||'default'; renderTo(k, elId); },
    get: function(){ const k=window.__pageHistoryKey||'default'; return get(k); }
  };
})();
