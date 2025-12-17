function setupLabelEditor(container, entity, extras){
  try {
    const API = (window.API) || 'http://localhost:8000/api';
    const token = localStorage.getItem('token') || '';
    const findAnchor = function(){
      const rows = container ? container.querySelectorAll('.jira-item') : [];
      for (var i=0;i<rows.length;i++){
        var lab = rows[i].querySelector('.jira-label');
        if (lab && String(lab.textContent||'').trim()==='Labels'){
          var val = rows[i].querySelector('.jira-value');
          if (val) return val;
        }
      }
      return null;
    };
    const anchor = findAnchor();
    if (!anchor) return;
    const current = (extras && extras.rawProject && extras.rawProject.label_path) || (entity && entity.label_path) || '';
    anchor.innerHTML = '<a id="labelsEditLink" href="javascript:void(0)" style="color:var(--primary);">' + (current || 'Select Label') + '</a>';
    const link = anchor.querySelector('#labelsEditLink');
    if (!link) return;

    async function fetchTree(){
      try{
        const res = await fetch(API + '/labels/tree', { headers:{ Authorization: 'Bearer ' + token } });
        if(!res.ok) return { items: [] };
        return await res.json();
      }catch(_){ return { items: [] }; }
    }

    async function resolveCanEdit(){
      try{
        const meRes = await fetch(API + '/auth/me', { headers:{ Authorization:'Bearer ' + token } });
        if(!meRes.ok) return false;
        const meRaw = await meRes.json();
        const me = meRaw && meRaw.user ? meRaw.user : meRaw;
        const isAdmin = !!(me && me.username==='admin');
        let assigneeId = null;
        let reporterId = null;
        if (entity.type==='project'){
          const rp = extras && extras.rawProject ? extras.rawProject : null;
          if (rp){ assigneeId = rp.owner_id || null; reporterId = rp.creator_id || null; }
          else {
            const idVal = entity.id || 0;
            const pr = await fetch(API + '/projects/' + idVal, { headers:{ Authorization:'Bearer ' + token } });
            if (pr.ok){ const p = await pr.json(); assigneeId = p.owner_id || null; reporterId = p.creator_id || null; }
          }
        } else {
          const ri = extras && extras.rawItem ? extras.rawItem : null;
          if (ri){ assigneeId = ri.assignee_id || null; reporterId = ri.creator_id || null; }
          else {
            const wid = Number(entity.id)||0;
            if (wid){
              const wr = await fetch(API + '/work-items/by-code/' + (entity.code||wid), { headers:{ Authorization:'Bearer ' + token } });
              if (wr.ok){ const w = await wr.json(); assigneeId = w.assignee_id || null; reporterId = w.creator_id || null; }
            }
          }
        }
        return isAdmin || (me && (me.id===assigneeId || me.id===reporterId));
      }catch(_){ return false; }
    }

    function openMenu(rootList){
      let menu = document.getElementById('labelCascaderDropdown');
      if(!menu){ menu=document.createElement('div'); menu.id='labelCascaderDropdown'; menu.className='dropdown'; document.body.appendChild(menu); }
      const rect = link.getBoundingClientRect();
      menu.style.display='block';
      menu.style.left=(rect.left + window.scrollX) + 'px';
      menu.style.top=(rect.bottom + window.scrollY) + 'px';
      menu.style.zIndex = '1000';
      let levels = [];
      let trail = [];
      levels[0] = Array.isArray(rootList) ? rootList : [];
      const render = function(){
        const colWidth = 220;
        const maxCols = Math.max(2, levels.length || 1);
        // Allow horizontal scrolling by setting max-width and overflow
        menu.style.maxWidth = (3 * colWidth + 32) + 'px'; // 3 cols + padding
        menu.style.width = 'auto';
        menu.style.overflowX = 'auto';
        
        let html = '<div class="cascader-cols" style="display:flex; gap:8px; align-items:flex-start; width:max-content;">';
        for (var i=0;i<levels.length;i++){
          const header = i===0 ? '根节点' : (trail[i-1] && trail[i-1].name ? trail[i-1].name : '');
          html += '<div class="cascader-col" data-level="'+i+'" style="flex:0 0 '+colWidth+'px; max-height:280px; overflow:auto; border-right:1px solid var(--border-color);">';
          html += '<div style="padding:6px 10px; font-size:12px; color:var(--text-secondary); border-bottom:1px solid var(--border-color);">'+ (header || '&nbsp;') +'</div>';
          const list = levels[i] || [];
          html += list.map(function(n){
          const leaf = !n.children || n.children.length===0;
            // For non-leaf nodes, add a specific "Select" button
            const arrow = leaf ? '' : '<span class="arrow-area" style="padding-left:8px; color:var(--text-secondary); cursor:pointer;">›</span>';
            const selectBtn = leaf ? '' : '<span class="select-btn" title="选择此项" style="margin-left:auto; margin-right:4px; padding:0 4px; color:var(--primary); font-size:16px; cursor:pointer;">◎</span>';
            const active = (trail[i] && trail[i].name===n.name) ? 'background:var(--category-touch);' : '';
            
            // Layout: [Name] [Spacer] [SelectBtn] [Arrow]
            // We use flexbox in .dropdown-item
            return '<div class="dropdown-item" data-level="'+i+'" data-leaf="'+(leaf?'1':'0')+'" data-name="'+(n.name||'')+'" data-path="'+(n.path||'')+'" style="'+active+'">' +
                   '<span class="label-name" style="flex:1;">' + (n.name||'') + '</span>' +
                   selectBtn +
                   arrow +
                   '</div>';
          }).join('');
          html += '</div>';
        }
        html += '</div>';
        menu.innerHTML = html;
        Array.prototype.forEach.call(menu.querySelectorAll('.dropdown-item'), function(it){
          it.onclick = async function(e){
            // Check if clicked target is the Select Button or if it's a leaf node
            const isSelectBtn = e.target.classList.contains('select-btn');
            const isArrow = e.target.classList.contains('arrow-area');
            
            const i = Number(this.getAttribute('data-level'))||0;
            const leaf = this.getAttribute('data-leaf')==='1';
            const name = this.getAttribute('data-name')||'';
            const path = this.getAttribute('data-path')||'';
            const colList = levels[i] || [];
            const item = colList.find(function(n){ return n.name===name; }) || null;
            if (!item) return;

            // If arrow is clicked, or it's a non-leaf item and NOT the select button -> Expand only
            if (!leaf && (isArrow || !isSelectBtn)) {
              trail = trail.slice(0, i);
              trail[i] = item;
              levels = levels.slice(0, i+1);
              levels[i+1] = Array.isArray(item.children) ? item.children : [];
              render();
              return;
            }

            // Otherwise (Leaf clicked OR Select Button clicked) -> Save
            menu.style.display='none';
            
            // Build path
            // If leaf, path might be set. If constructed, we use trail.
            // If picking non-leaf, we use trail up to i-1 + current name.
            // Note: 'trail' might not include current item yet if we just clicked 'Select' on it without expanding first?
            // Actually, if we click Select, we are at level i.
            // Trail contains items 0..i-1.
            
            // Correct path construction:
            const selectedPathSuffix = trail.slice(0, i).map(function(t){ return t.name; }).concat([name]).join('/');
            
            // Prepend prefix if exists
            let finalPath = selectedPathSuffix;
            if (window.__labelPathPrefix) {
                // Handle slash carefully
                const prefix = window.__labelPathPrefix.endsWith('/') ? window.__labelPathPrefix : (window.__labelPathPrefix + '/');
                finalPath = prefix + selectedPathSuffix;
            } else if (path) {
                // If the node itself has a full path property (usually root nodes might, or if API provides it)
                // But we must respect the prefix logic for tasks.
                finalPath = path; 
            }
            
            link.textContent = finalPath;
            try{
              const projId = (entity && entity.type==='project') ? (entity.id || 0) : ((extras && extras.project_id) || 0);
              const wid = Number(entity && entity.type!=='project' ? (entity.id||0) : 0);
              const payload = { label_path: finalPath };
              if (entity.type==='project'){
                const res = await fetch(API + '/projects/' + projId, { method:'PUT', headers:{ 'Content-Type':'application/json', Authorization:'Bearer '+token }, body: JSON.stringify(payload) });
                if(!res.ok){ const txt = await res.text(); alert('保存失败(' + res.status + '): ' + txt); }
              } else {
                const res2 = await fetch(API + '/work-items/' + wid, { method:'PATCH', headers:{ 'Content-Type':'application/json', Authorization:'Bearer '+token }, body: JSON.stringify(payload) });
                if(!res2.ok){ const t2 = await res2.text(); alert('保存失败(' + res2.status + '): ' + t2); }
              }
            }catch(e){ console.error('[labels] save error', e); }
          };
        });
        menu.onmousedown=function(e){ e.preventDefault(); };
      };
      render();
    }

    // Prefetch permission state to set disabled styling
    resolveCanEdit().then(function(can){ if (!can){ link.style.color = 'var(--text-secondary)'; link.style.cursor = 'not-allowed'; } }).catch(function(){});

    link.onclick = async function(){
      const can = await resolveCanEdit();
      if (!can){ link.style.color = 'var(--text-secondary)'; link.style.cursor = 'not-allowed'; return; }
      const tree = await fetchTree();
      let list = Array.isArray(tree.items) ? tree.items : [];
      
      // Task restriction logic:
      // If entity is a Task, restrict to sub-nodes of the parent Job's label
      if (entity.type === 'task' && entity.parent_id) {
          try {
             // Fetch parent item (Job)
             // We use entity.parent_id if available. 
             // Note: normalizeEntity in meta-panel.js populates parent_id.
             const pid = entity.parent_id;
             if (pid) {
                 const pRes = await fetch(API + '/work-items/' + pid, { headers:{ Authorization: 'Bearer ' + token } });
                 if (pRes.ok) {
                     const parentItem = await pRes.json();
                     const pPath = parentItem.label_path;
                     if (pPath) {
                         // Find the node in the tree matching pPath
                         const parts = pPath.split('/');
                         let currentLevel = list;
                         let foundNode = null;
                         for (const part of parts) {
                             if (!currentLevel) break;
                             const node = currentLevel.find(n => n.name === part);
                             if (node) {
                                 foundNode = node;
                                 currentLevel = node.children;
                             } else {
                                 foundNode = null;
                                 break;
                             }
                         }
                         
                         // If found, restrict list to its children
                         if (foundNode && foundNode.children && foundNode.children.length > 0) {
                             list = foundNode.children;
                             // We also need to prefix the path when saving? 
                             // Wait, if I select 'China' (child of 'Asia'), the path should be 'Region/Asia/China'.
                             // But if I restrict the root to 'China', the cascader might think 'China' is root.
                             // The existing logic builds path from 'trail'.
                             // If I start from a subtree, I need to prepend the parent path to the trail?
                             // Yes.
                             // Hack: Pre-fill 'trail' with the parent path nodes?
                             // But 'trail' is visual.
                             // If I set 'trail' to parent nodes, they will appear in the columns?
                             // The render function iterates 'levels'.
                             // If I want to hide the parent levels and only show children, 
                             // I should set the *context* path prefix.
                             window.__labelPathPrefix = pPath;
                         } else {
                             // Parent has label but no children, or label not found in tree.
                             // If parent label is valid but has no children, task can't have sub-labels?
                             // Or maybe we should show empty list?
                             if (foundNode) list = []; 
                         }
                     }
                 }
             }
          } catch(e) { console.error(e); }
      } else {
          window.__labelPathPrefix = '';
      }

      openMenu(list);
    };
  } catch(_){}
}
