function openCommentModal(opts){
  const o = opts || {};
  const title = o.title || '添加评论';
  const saveText = o.saveText || '发布';
  const entityType = o.entityType || 'project';
  const entityId = o.entityId || 0;
  const initialHTML = o.initialHTML || '';
  const onSave = typeof o.onSave === 'function' ? o.onSave : async function(){ return true; };
  const id = 'cm_' + Date.now();
  const backdrop = document.createElement('div'); backdrop.className = 'cm-backdrop';
  const modal = document.createElement('div'); modal.className = 'cm-modal';
  const header = document.createElement('div'); header.className = 'cm-header';
  const hTitle = document.createElement('div'); hTitle.className = 'cm-title'; hTitle.textContent = title;
  const btnClose = document.createElement('button'); btnClose.className = 'cm-close'; btnClose.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="#374151" d="M6 6l12 12M18 6L6 18" stroke="#374151" stroke-width="2"/></svg>';
  btnClose.onclick = function(){ try{ document.body.removeChild(backdrop); } catch (e) {} };
  header.appendChild(hTitle); header.appendChild(btnClose);
  const body = document.createElement('div'); body.className = 'cm-body';
  const editorHost = document.createElement('div'); editorHost.id = id + '_editor'; body.appendChild(editorHost);
  const error = document.createElement('div'); error.className = 'cm-error'; error.id = id + '_error'; body.appendChild(error);
  const actions = document.createElement('div'); actions.className = 'cm-actions';
  const cancelBtn = document.createElement('button'); cancelBtn.className = 'cm-btn'; cancelBtn.textContent = '取消'; cancelBtn.onclick = function(){ try{ document.body.removeChild(backdrop); } catch (e) {} };
  const saveBtn = document.createElement('button'); saveBtn.className = 'cm-btn primary'; saveBtn.textContent = saveText;
  actions.appendChild(cancelBtn); actions.appendChild(saveBtn);
  modal.appendChild(header); modal.appendChild(body); modal.appendChild(actions);
  backdrop.appendChild(modal); document.body.appendChild(backdrop);
  try{
    const ed = createRichEditor(editorHost.id, {
      entityType: entityType,
      entityId: entityId,
      saveText: saveText,
      onSave: async function(html){ const c = (html || '').trim(); error.textContent=''; if(!c){ error.textContent='请输入内容'; return false; } const ok = await onSave(html); if(ok !== false){ try{ document.body.removeChild(backdrop); } catch (e) {} } return ok; }
    });
    ed.setHTML(initialHTML || '');
    try{ ed && ed.focus && ed.focus(); }catch(_){ }
    saveBtn.onclick = function(){ const btn = saveBtn; btn.disabled = true; try{ const html = ed.getHTML(); ed.focus(); const fn = ed; if(fn && typeof fn.focus==='function'){ /* noop */ } } finally { btn.disabled = false; } };
  }catch(e){ error.textContent = '编辑器加载错误'; }
}
