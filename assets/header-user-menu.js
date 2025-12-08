;(function(){
  const API = (typeof window!=='undefined' && window.API) ? window.API : 'http://localhost:8000/api';
  const token = (typeof localStorage!=='undefined') ? localStorage.getItem('token') : null;

  function showToast(text, type){ try{ const el=document.createElement('div'); el.className=`toast ${type||'success'}`; el.textContent=text; document.body.appendChild(el); setTimeout(()=>el.remove(), 1800); }catch(e){} }

  async function fetchMe(){ try{ const r=await fetch(`${API}/auth/me`, { headers:{ Authorization: `Bearer ${token}` } }); if(!r.ok) throw new Error('auth'); const raw=await r.json(); return (raw && raw.user) ? raw.user : raw; } catch(e){ return null; } }

  async function fetchUnreadCount(){ try{ const r=await fetch(`${API}/notifications?unread=true`, { headers:{ Authorization:`Bearer ${token}` } }); if(!r.ok) throw new Error('n'); const data=await r.json(); const items=Array.isArray(data)? data : (Array.isArray(data.items)? data.items : []); return items.filter(x=> x && (x.read===false)).length || items.length || 0; } catch(e){ try{ const cache=JSON.parse(localStorage.getItem('__notif_cache')||'[]'); return (Array.isArray(cache)? cache.filter(x=>!x.read).length : 0); }catch(_) { return 0; } } }

  async function fetchNotifications(params){ const p=params||{}; const unreadFlag = p.status==='unread' ? true : (p.unread===true); const qs=new URLSearchParams(); if(unreadFlag) qs.set('unread','true'); const page = Number.isFinite(p.page)? p.page : 1; const pageSize = Number.isFinite(p.page_size)? p.page_size : 10; qs.set('page', String(page)); qs.set('page_size', String(pageSize)); try{ const r=await fetch(`${API}/notifications${qs.toString()? ('?'+qs.toString()) : ''}`, { headers:{ Authorization:`Bearer ${token}` } }); if(!r.ok) throw new Error('n'); const data=await r.json(); return data && data.items ? data : { page, page_size: pageSize, total: (Array.isArray(data)? data.length : 0), items: (Array.isArray(data)? data : []) }; } catch(e){ try{ const cache=JSON.parse(localStorage.getItem('__notif_cache')||'[]'); const start=(page-1)*pageSize; return { page, page_size: pageSize, total: Array.isArray(cache)? cache.length : 0, items: (Array.isArray(cache)? cache.slice(start, start+pageSize) : []) }; }catch(_){ return { page, page_size: pageSize, total: 0, items: [] }; } } }

  async function markRead(id){ try{ const r=await fetch(`${API}/notifications/${id}`, { method:'PATCH', headers:{ 'Content-Type':'application/json', Authorization:`Bearer ${token}` }, body: JSON.stringify({ read:true }) }); if(!r.ok) throw new Error('n'); return true; } catch(e){ try{ const cache=JSON.parse(localStorage.getItem('__notif_cache')||'[]'); const next=(Array.isArray(cache)? cache.map(x=> x.id===id? Object.assign({}, x, { read:true }) : x ) : []); localStorage.setItem('__notif_cache', JSON.stringify(next)); return true; }catch(_){ return false; } } }

  async function markAllRead(){ try{ const res = await fetchNotifications({ status:'unread', page:1, page_size:1000 }); const items = res.items || []; for (const it of items) { if (it && it.id!=null) { try{ await markRead(it.id); }catch(_){} } } return true; } catch(e){ try{ const cache=JSON.parse(localStorage.getItem('__notif_cache')||'[]'); const next=(Array.isArray(cache)? cache.map(x=> Object.assign({}, x, { read:true }) ) : []); localStorage.setItem('__notif_cache', JSON.stringify(next)); return true; }catch(_){ return false; } } }

  function prefixFromEmail(email){ if(!email) return ''; const i=String(email).indexOf('@'); return i>0? email.slice(0,i) : String(email||'').trim()||''; }

  function ensureContainer(){ let c=document.getElementById('userMenuContainer'); if(c) return c; const header = document.querySelector('.header') || document.querySelector('.top') || document.querySelector('.header-right') || document.querySelector('.header-actions') || document.querySelector('.page-header'); if(!header){ c=document.createElement('div'); c.id='userMenuContainer'; document.body.appendChild(c); return c; } c=document.createElement('div'); c.id='userMenuContainer'; header.appendChild(c); return c; }

  function renderMenu(container, ctx){ const el=document.createElement('div'); el.className='user-menu'; el.innerHTML=`
    <div class="user-menu-trigger" id="userMenuTrigger">
      <span class="user-menu-prefix" id="userMenuPrefix">${ctx.displayName||'用户'}</span>
      <span class="user-menu-badge hidden" id="userNotifBadge">0</span>
      <svg class="user-menu-arrow" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"></path></svg>
    </div>
  `;
    container.innerHTML=''; container.appendChild(el);
    const trigger=el.querySelector('#userMenuTrigger');
    const badge=el.querySelector('#userNotifBadge');
    const dropdown=document.createElement('div'); dropdown.className='user-dropdown'; dropdown.style.display='none'; dropdown.style.right='0px'; dropdown.style.top='calc(100% + 8px)';
    dropdown.innerHTML=`
      <div class="user-dropdown-item" data-action="profile">个人中心</div>
      <div class="user-dropdown-item" data-action="notifications">我的通知</div>
      <div class="user-dropdown-item" data-action="logout">退出登录</div>
    `;
    el.style.position='relative'; el.appendChild(dropdown);
    trigger.addEventListener('click', ()=>{ dropdown.style.display = (dropdown.style.display==='none'?'block':'none'); });
    document.addEventListener('click', (e)=>{ if(!el.contains(e.target)) dropdown.style.display='none'; });
    dropdown.querySelector('[data-action="profile"]').onclick=async function(){ dropdown.style.display='none'; try{ const fresh = await fetchMe(); openProfile(fresh || ctx.me); } catch(_){ openProfile(ctx.me); } };
    dropdown.querySelector('[data-action="notifications"]').onclick=function(){ dropdown.style.display='none'; openNotifications(); };
    dropdown.querySelector('[data-action="logout"]').onclick=function(){ dropdown.style.display='none'; try{ localStorage.removeItem('token'); location.href='login.html'; }catch(_){ location.reload(); } };
    updateBadge(badge);
    startPolling(badge);
  }

  async function updateBadge(badge){ const c=await fetchUnreadCount(); if(c>0){ badge.textContent = c>99? '99+' : String(c); badge.classList.remove('hidden'); } else { badge.classList.add('hidden'); } }
  function startPolling(badge){ try{ setInterval(()=>{ updateBadge(badge); }, 30000); }catch(_){ }
  }

  function openProfile(me){ const backdrop=document.createElement('div'); backdrop.className='user-modal-backdrop'; backdrop.style.display='flex';
    const modal=document.createElement('div'); modal.className='user-modal';
    const email=(me&&me.email)||''; const username=(me&&me.username)||''; const full_name=(me&&me.full_name)||''; const phone=(me&&me.phone)||''; const created_at=(me&&me.created_at)||''; const expires_at=(me&&me.expires_at)||''; const last_login_at=(me&&me.last_login_at)||''; const password_changed_at=(me&&me.password_changed_at)||''; const avatar_key=(me&&me.avatar_key)||'';
    modal.innerHTML=`
      <h4>个人中心</h4>
      <div class="user-form-row"><label>头像</label><div class="avatar-grid" id="avatarGrid"></div></div>
      <div class="user-form-row"><label>用户名</label><div>${username||'-'}</div></div>
      <div class="user-form-row"><label>用户姓名</label><input id="fullnameInput" value="${full_name||''}" placeholder="请输入姓名" /></div>
      <div class="user-form-row"><label>用户手机</label><input id="phoneInput" value="${phone||''}" placeholder="请输入手机号" /></div>
      <div class="user-form-row"><label>用户邮箱</label><div>${email||'-'}</div></div>
      <div class="user-form-row"><label>账号创建时间</label><div>${created_at||'-'}</div></div>
      <div class="user-form-row"><label>账号过期时间</label><div>${expires_at||'-'}</div></div>
      <div class="user-form-row"><label>最后登录时间</label><div>${last_login_at||'-'}</div></div>
      <div class="user-form-row"><label>密码最后修改时间</label><div>${password_changed_at||'-'}</div></div>
      <div class="user-modal-actions"><button class="user-btn-ghost" id="editBtn">编辑</button><button class="user-btn-ghost" id="closeBtn">关闭</button><button class="user-btn-primary" id="saveBtn">保存</button></div>
    `;
    backdrop.appendChild(modal); document.body.appendChild(backdrop);
    const grid=modal.querySelector('#avatarGrid'); const presets=['cat_1','cat_2','dog_1','dog_2','cat_3','dog_3']; const emojiMap={cat_1:'🐱',cat_2:'🐈',cat_3:'🐈‍⬛',dog_1:'🐶',dog_2:'🐕',dog_3:'🦮'}; presets.forEach(k=>{ const item=document.createElement('div'); item.className='avatar-item'; item.innerHTML=emojiMap[k]||'🐾'; if(String(avatar_key||'')===String(k)) item.classList.add('selected'); item.classList.add('disabled'); item.onclick=function(){ if(modal.dataset.editing!=='true') return; grid.querySelectorAll('.avatar-item').forEach(x=>x.classList.remove('selected')); item.classList.add('selected'); modal.dataset.avatarKey=k; }; grid.appendChild(item); });
    const fullnameInput = modal.querySelector('#fullnameInput'); const phoneInput = modal.querySelector('#phoneInput'); fullnameInput.disabled = true; phoneInput.disabled = true;
    modal.querySelector('#closeBtn').onclick=function(){ backdrop.remove(); };
    modal.dataset.editing='false';
    modal.querySelector('#editBtn').onclick=function(){ const editing = modal.dataset.editing==='true'; const next=!editing; modal.dataset.editing = next? 'true':'false'; fullnameInput.disabled = !next; phoneInput.disabled = !next; grid.querySelectorAll('.avatar-item').forEach(function(x){ x.classList.toggle('disabled', !next); }); showToast(next? '已进入编辑模式' : '已退出编辑模式'); };
    modal.querySelector('#saveBtn').onclick=async function(){ const nextFullname=fullnameInput.value.trim(); const nextPhone=phoneInput.value.trim(); const nextAvatar=modal.dataset.avatarKey || avatar_key || ''; try{ const r=await fetch(`${API}/users/me`, { method:'PATCH', headers:{ 'Content-Type':'application/json', Authorization:`Bearer ${token}` }, body: JSON.stringify({ full_name: nextFullname||undefined, phone: nextPhone||undefined, avatar_key: nextAvatar||undefined }) }); if(r.ok){ const data = await r.json().catch(()=>null); try{ const u = data || {}; const name = (u.full_name)|| (u.username) || (u.email_prefix ? String(u.email_prefix) : ''); const prefixEl=document.getElementById('userMenuPrefix'); if(prefixEl && name){ prefixEl.textContent = name; } }catch(_){} showToast('保存成功','success'); backdrop.remove(); } else { const t=await r.text(); showToast(t||'保存失败','error'); } } catch(e){ try{ const cache=JSON.parse(localStorage.getItem('__me_cache')||'{}'); cache.full_name=nextFullname; cache.phone=nextPhone; cache.avatar_key=nextAvatar; localStorage.setItem('__me_cache', JSON.stringify(cache)); try{ const name = nextFullname || ''; const prefixEl=document.getElementById('userMenuPrefix'); if(prefixEl && name){ prefixEl.textContent = name; } }catch(_){} showToast('已保存（本地缓存）','success'); backdrop.remove(); }catch(_){ showToast('保存失败','error'); } } };
  }

  function buildNotifItem(n){ const typeLabel = '@提及'; const time=n.created_at||''; const read=!!n.read; const title=n.title||''; const content=n.content||''; const url=resolveUrl(n) || '#'; const wrap=document.createElement('div'); wrap.className='user-dropdown-item'; wrap.innerHTML=`<div style="flex:1;display:flex;flex-direction:column;gap:4px"><div style="display:flex;justify-content:space-between"><span>${typeLabel}</span><span style="color:#6b7280;font-size:12px;">${time}</span></div><div style="color:#111827;font-weight:600;">${title}</div><div style="color:#374151;">${content}</div></div><div style="display:flex;gap:6px"><button class="user-btn-ghost" data-action="read" style="padding:4px 8px;">${read? '已读' : '标记已读'}</button><button class="user-btn-primary" data-action="open" style="padding:4px 8px;">去看看</button></div>`;
    const readBtn=wrap.querySelector('button[data-action="read"]'); const openBtn=wrap.querySelector('button[data-action="open"]');
    readBtn.onclick=async function(ev){ ev.stopPropagation(); if(!read){ await markRead(n.id); readBtn.textContent='已读'; } };
    openBtn.onclick=async function(ev){ ev.stopPropagation(); try{ if(!read){ try{ await markRead(n.id); readBtn.textContent='已读'; }catch(_){ } } const target = await (async function(){ const a=(n.anchor||'').trim(); if(a && (/^https?:\/\//i.test(a) || a.indexOf('?')>=0)) return a; if(n && n.target_type==='comment' && Number.isFinite(n.target_id)){ try{ const r=await fetch(`${API}/comments/context/${n.target_id}`, { headers:{ Authorization:`Bearer ${token}` } }); if(r.ok){ const data=await r.json(); if(data && data.url){ return data.url; } } }catch(_){ } } return (/^https?:\/\//i.test(url) || url.indexOf('?')>=0) ? url : (location.pathname + url); })(); const abs = /^https?:\/\//i.test(target) ? target : (location.origin + (target.startsWith('/')? '' : '/') + target); window.open(abs, '_blank'); }catch(_){ } };
    wrap.onclick=async function(){ try{ const t = await (async function(){ const a=(n.anchor||'').trim(); if(a && (/^https?:\/\//i.test(a) || a.indexOf('?')>=0)) return a; if(n && n.target_type==='comment' && Number.isFinite(n.target_id)){ try{ const r=await fetch(`${API}/comments/context/${n.target_id}`, { headers:{ Authorization:`Bearer ${token}` } }); if(r.ok){ const data=await r.json(); if(data && data.url){ return data.url; } } }catch(_){ } } return url; })(); window.location.href=t; }catch(_){ } };
    return wrap;
  }

  function resolveUrl(n){ try{ const a = (n.anchor||'').trim(); if (!a) return '#'; if (/^https?:\/\//i.test(a) || a.indexOf('?')>=0) return a; if (a.startsWith('comment-') || /^#comment-/.test(a)) return '#' + (a.startsWith('#')? a.slice(1) : a); return '#' + a; } catch(e){} return '#'; }

  async function openNotifications(){ const backdrop=document.createElement('div'); backdrop.className='user-modal-backdrop'; backdrop.style.display='flex'; const modal=document.createElement('div'); modal.className='user-modal'; modal.style.width='640px'; modal.innerHTML=`<h4>我的通知</h4><div style="display:flex;gap:8px;align-items:center;margin:8px 0;"><select id="statusSel"><option value="unread">未读</option><option value="all">全部</option></select><button class="user-btn-ghost" id="readAllBtn">全部标记已读</button></div><div id="notifList" style="max-height:420px;overflow:auto;border:1px solid #e5e7eb;border-radius:8px;"></div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;"><div id="pageInfo" style="color:#6b7280;font-size:12px;"></div><div style="display:flex;gap:8px;"><button class="user-btn-ghost" id="prevBtn">上一页</button><button class="user-btn-ghost" id="nextBtn">下一页</button></div></div><div class="user-modal-actions"><button class="user-btn-ghost" id="closeBtn">关闭</button></div>`; backdrop.appendChild(modal); document.body.appendChild(backdrop);
    const list=modal.querySelector('#notifList'); const statusSel=modal.querySelector('#statusSel'); const readAllBtn=modal.querySelector('#readAllBtn'); const closeBtn=modal.querySelector('#closeBtn'); const pageInfo=modal.querySelector('#pageInfo'); const prevBtn=modal.querySelector('#prevBtn'); const nextBtn=modal.querySelector('#nextBtn'); let page=1; const pageSize=10;
    async function reload(){ const status=statusSel.value; const res=await fetchNotifications({ status, page, page_size: pageSize }); const items=res.items||[]; const total=res.total||items.length; list.innerHTML=''; items.forEach(n=> list.appendChild(buildNotifItem(n)) ); const maxPage = Math.max(1, Math.ceil(total / pageSize)); pageInfo.textContent = `第 ${page} / ${maxPage} 页 · 共 ${total} 条`; prevBtn.disabled = (page<=1); nextBtn.disabled = (page>=maxPage); }
    statusSel.onchange=function(){ page=1; reload(); }; readAllBtn.onclick=async function(){ await markAllRead(); await reload(); };
    prevBtn.onclick=function(){ if(page>1){ page--; reload(); } }; nextBtn.onclick=function(){ page++; reload(); };
    closeBtn.onclick=function(){ backdrop.remove(); };
    await reload();
  }

  (async function init(){ try{ const container=ensureContainer(); const me=await fetchMe(); const displayName=(me&&me.full_name)||((me&&me.username)||prefixFromEmail(me&&me.email)||''); renderMenu(container, { displayName, me }); } catch(e){ } })();
})();
