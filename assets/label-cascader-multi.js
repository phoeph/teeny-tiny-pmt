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
      if(!menu){ 
        menu=document.createElement('div'); 
        menu.id='labelCascaderDropdown'; 
        menu.className='dropdown'; 
        document.body.appendChild(menu); 
      }
      const rect = link.getBoundingClientRect();
      menu.style.display='block';
      menu.style.left=(rect.left + window.scrollX) + 'px';
      menu.style.top=(rect.bottom + window.scrollY) + 'px';
      menu.style.zIndex = '1000';
      
      // 过滤掉Excel列名（如level1_name, level2_name等）
      function filterExcelHeaders(nodes) {
        if (!Array.isArray(nodes)) return [];
        
        return nodes.filter(function(node) {
          const name = node.name || '';
          // 过滤掉Excel列名模式：levelN_name, levelN_code等
          const isExcelHeader = /^level\d+_/i.test(name);
          return !isExcelHeader;
        }).map(function(node) {
          // 递归过滤子节点
          if (node.children && node.children.length > 0) {
            return {
              ...node,
              children: filterExcelHeaders(node.children)
            };
          }
          return node;
        });
      }
      
      let levels = [];
      let trail = [];
      let scrollPositions = []; // Track scroll positions for each level
      let searchTerm = '';
      let filteredRootList = filterExcelHeaders(Array.isArray(rootList) ? rootList : []);
      levels[0] = filteredRootList;
      
      // Fuzzy search function
      function fuzzyMatch(text, search) {
        if (!search) return true;
        const searchLower = search.toLowerCase();
        const textLower = text.toLowerCase();
        return textLower.includes(searchLower);
      }
      
      // Recursive search through tree
      function searchInTree(nodes, term) {
        if (!term) return nodes;
        const results = [];
        
        function traverse(nodeList, parentPath = '') {
          nodeList.forEach(node => {
            const fullPath = parentPath ? `${parentPath}/${node.name}` : node.name;
            if (fuzzyMatch(node.name, term) || fuzzyMatch(fullPath, term)) {
              results.push({
                ...node,
                searchPath: fullPath,
                isSearchResult: true
              });
            }
            if (node.children && node.children.length > 0) {
              traverse(node.children, fullPath);
            }
          });
        }
        
        traverse(nodes);
        return results;
      }
      
      const render = function(){
        const colWidth = 220;
        // Allow horizontal scrolling by setting max-width and overflow
        menu.style.maxWidth = (3 * colWidth + 32) + 'px'; // 3 cols + padding
        menu.style.width = 'auto';
        menu.style.overflowX = 'auto';
        
        let html = '<div style="padding: 8px; border-bottom: 1px solid var(--border-color);">';
        html += '<div style="display: flex; gap: 8px; align-items: center;">';
        html += '<input type="text" id="labelSearch" placeholder="搜索标签..." autocomplete="off" spellcheck="false" style="flex: 1; padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 13px; direction: ltr; text-align: left; font-family: inherit;" value="' + (searchTerm || '') + '">';
        html += '<button id="clearLabelsBtn" title="清空标签" style="padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 4px; background: var(--bg-surface); color: var(--text-secondary); cursor: pointer; font-size: 12px; white-space: nowrap;">清空</button>';
        html += '</div>';
        html += '</div>';
        
        if (searchTerm) {
          // Show search results in a single column
          const searchResults = searchInTree(filteredRootList, searchTerm);
          html += '<div class="search-results" style="max-height: 300px; overflow-y: auto; padding: 4px;">';
          if (searchResults.length === 0) {
            html += '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">未找到匹配的标签</div>';
          } else {
            html += searchResults.map(function(n) {
              return '<div class="dropdown-item search-result-item" data-name="' + (n.name || '') + '" data-path="' + (n.searchPath || '') + '" style="padding: 8px 12px; margin: 2px 0; border-radius: 4px;">' +
                     '<div style="font-weight: 500;">' + (n.name || '') + '</div>' +
                     '<div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">' + (n.searchPath || '') + '</div>' +
                     '</div>';
            }).join('');
          }
          html += '</div>';
        } else {
          // Show normal cascader columns
          html += '<div class="cascader-cols" style="display:flex; gap:8px; align-items:flex-start; width:max-content;">';
          for (var i=0;i<levels.length;i++){
            // Remove "根节点" text and Excel headers - just show clean column headers
            const header = i===0 ? '' : (trail[i-1] && trail[i-1].name ? trail[i-1].name : '');
            html += '<div class="cascader-col" data-level="'+i+'" style="flex:0 0 '+colWidth+'px; max-height:280px; overflow:auto; border-right:1px solid var(--border-color);">';
            if (header) {
              html += '<div style="padding:6px 10px; font-size:12px; color:var(--text-secondary); border-bottom:1px solid var(--border-color); font-weight: 500;">'+ header +'</div>';
            }
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
        }
        
        menu.innerHTML = html;
        
        // Restore scroll positions
        if (!searchTerm) {
          setTimeout(() => {
            for (let i = 0; i < levels.length; i++) {
              const col = menu.querySelector(`.cascader-col[data-level="${i}"]`);
              if (col && scrollPositions[i] !== undefined) {
                col.scrollTop = scrollPositions[i];
              }
            }
          }, 0);
        }
        
        // Setup search input handler
        const searchInput = menu.querySelector('#labelSearch');
        const clearBtn = menu.querySelector('#clearLabelsBtn');
        
        if (searchInput) {
          let isComposing = false; // 标记是否正在使用输入法
          
          // 确保输入框获得焦点并且光标在正确位置
          setTimeout(() => {
            searchInput.focus();
            // 如果有值，将光标移到末尾
            if (searchInput.value) {
              const len = searchInput.value.length;
              searchInput.setSelectionRange(len, len);
            }
          }, 10);
          
          // 处理输入法开始事件
          searchInput.oncompositionstart = function(e) {
            isComposing = true;
          };
          
          // 处理输入法更新事件
          searchInput.oncompositionupdate = function(e) {
            isComposing = true;
          };
          
          // 处理输入法结束事件
          searchInput.oncompositionend = function(e) {
            isComposing = false;
            
            // 输入法结束后，更新搜索结果
            const newValue = this.value;
            searchTerm = newValue;
            
            // 只更新搜索结果部分，不重新渲染整个输入框
            updateSearchResults();
          };
          
          searchInput.oninput = function(e) {
            
            // 如果正在使用输入法，不要立即更新搜索结果
            if (isComposing) {
              return;
            }
            
            // 更新搜索词
            searchTerm = this.value;
            
            // 只更新搜索结果部分，不重新渲染整个输入框
            updateSearchResults();
          };
          
          searchInput.onkeydown = function(e) {
            if (e.key === 'Escape') {
              menu.style.display = 'none';
            }
          };
          
          // 防止输入框失去焦点
          searchInput.onblur = function(e) {
            // 如果点击的不是菜单内的元素，则关闭菜单
            if (!menu.contains(e.relatedTarget)) {
              setTimeout(() => {
                if (document.activeElement !== searchInput) {
                  searchInput.focus();
                }
              }, 10);
            }
          };
        }
        
        // 处理清空按钮点击
        if (clearBtn) {
          clearBtn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // 关闭弹窗
            menu.style.display = 'none';
            
            // 清空显示的标签
            link.textContent = 'Select Label';
            
            // 保存空值到后端
            saveSelection('');
          };
          
          // 清空按钮的悬停效果
          clearBtn.onmouseenter = function() {
            this.style.background = 'var(--danger-light)';
            this.style.color = 'var(--danger)';
            this.style.borderColor = 'var(--danger)';
          };
          
          clearBtn.onmouseleave = function() {
            this.style.background = 'var(--bg-surface)';
            this.style.color = 'var(--text-secondary)';
            this.style.borderColor = 'var(--border-color)';
          };
        }
        
        // 单独的函数来更新搜索结果，避免重新创建输入框
        function updateSearchResults() {
          if (searchTerm) {
            // 搜索模式：显示搜索结果
            updateSearchResultsView();
          } else {
            // 级联模式：更新级联选择器
            updateCascaderView();
          }
        }
        
        // 更新搜索结果视图
        function updateSearchResultsView() {
          let container = menu.querySelector('.search-results');
          const cascaderContainer = menu.querySelector('.cascader-cols');
          
          // 如果当前是级联视图，需要切换到搜索视图
          if (cascaderContainer && !container) {
            const searchResults = searchInTree(filteredRootList, searchTerm);
            let resultsHtml = '<div class="search-results" style="max-height: 300px; overflow-y: auto; padding: 4px;">';
            
            if (searchResults.length === 0) {
              resultsHtml += '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">未找到匹配的标签</div>';
            } else {
              resultsHtml += searchResults.map(function(n) {
                return '<div class="dropdown-item search-result-item" data-name="' + (n.name || '') + '" data-path="' + (n.searchPath || '') + '" style="padding: 8px 12px; margin: 2px 0; border-radius: 4px;">' +
                       '<div style="font-weight: 500;">' + (n.name || '') + '</div>' +
                       '<div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">' + (n.searchPath || '') + '</div>' +
                       '</div>';
              }).join('');
            }
            resultsHtml += '</div>';
            
            cascaderContainer.outerHTML = resultsHtml;
            bindResultEvents();
          } else if (container) {
            // 如果已经是搜索视图，只更新内容
            const searchResults = searchInTree(filteredRootList, searchTerm);
            let contentHtml = '';
            
            if (searchResults.length === 0) {
              contentHtml = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">未找到匹配的标签</div>';
            } else {
              contentHtml = searchResults.map(function(n) {
                return '<div class="dropdown-item search-result-item" data-name="' + (n.name || '') + '" data-path="' + (n.searchPath || '') + '" style="padding: 8px 12px; margin: 2px 0; border-radius: 4px;">' +
                       '<div style="font-weight: 500;">' + (n.name || '') + '</div>' +
                       '<div style="font-size: 11px; color: var(--text-secondary); margin-top: 2px;">' + (n.searchPath || '') + '</div>' +
                       '</div>';
              }).join('');
            }
            
            container.innerHTML = contentHtml;
            bindResultEvents();
          }
        }
        
        // 更新级联选择器视图
        function updateCascaderView() {
          const searchContainer = menu.querySelector('.search-results');
          let cascaderContainer = menu.querySelector('.cascader-cols');
          
          // 如果当前是搜索视图，需要切换到级联视图
          if (searchContainer && !cascaderContainer) {
            let cascaderHtml = '<div class="cascader-cols" style="display:flex; gap:8px; align-items:flex-start; width:max-content;">';
            cascaderHtml += generateCascaderColumns();
            cascaderHtml += '</div>';
            
            searchContainer.outerHTML = cascaderHtml;
            bindResultEvents();
            restoreScrollPositions();
          } else if (cascaderContainer) {
            // 如果已经是级联视图，智能更新
            updateCascaderColumns();
          }
        }
        
        // 生成级联选择器列的HTML
        function generateCascaderColumns() {
          let html = '';
          for (var i = 0; i < levels.length; i++) {
            const header = i === 0 ? '' : (trail[i-1] && trail[i-1].name ? trail[i-1].name : '');
            html += '<div class="cascader-col" data-level="' + i + '" style="flex:0 0 ' + colWidth + 'px; max-height:280px; overflow:auto; border-right:1px solid var(--border-color);">';
            if (header) {
              html += '<div style="padding:6px 10px; font-size:12px; color:var(--text-secondary); border-bottom:1px solid var(--border-color); font-weight: 500;">' + header + '</div>';
            }
            const list = levels[i] || [];
            html += list.map(function(n) {
              const leaf = !n.children || n.children.length === 0;
              const arrow = leaf ? '' : '<span class="arrow-area" style="padding-left:8px; color:var(--text-secondary); cursor:pointer;">›</span>';
              const selectBtn = leaf ? '' : '<span class="select-btn" title="选择此项" style="margin-left:auto; margin-right:4px; padding:0 4px; color:var(--primary); font-size:16px; cursor:pointer;">◎</span>';
              const active = (trail[i] && trail[i].name === n.name) ? 'background:var(--category-touch);' : '';
              
              return '<div class="dropdown-item" data-level="' + i + '" data-leaf="' + (leaf ? '1' : '0') + '" data-name="' + (n.name || '') + '" data-path="' + (n.path || '') + '" style="' + active + '">' +
                     '<span class="label-name" style="flex:1;">' + (n.name || '') + '</span>' +
                     selectBtn +
                     arrow +
                     '</div>';
            }).join('');
            html += '</div>';
          }
          return html;
        }
        
        // 智能更新级联选择器列
        function updateCascaderColumns() {
          const cascaderContainer = menu.querySelector('.cascader-cols');
          if (!cascaderContainer) return;
          
          const existingCols = cascaderContainer.querySelectorAll('.cascader-col');
          const currentLevelCount = levels.length;
          
          // 移除多余的列
          for (let i = currentLevelCount; i < existingCols.length; i++) {
            existingCols[i].remove();
          }
          
          // 更新或添加需要的列
          for (let i = 0; i < currentLevelCount; i++) {
            let col = cascaderContainer.querySelector(`.cascader-col[data-level="${i}"]`);
            
            if (col) {
              // 更新现有列
              updateSingleColumn(col, i);
            } else {
              // 添加新列
              const newColHtml = '<div class="cascader-col" data-level="' + i + '" style="flex:0 0 ' + colWidth + 'px; max-height:280px; overflow:auto; border-right:1px solid var(--border-color);">' +
                                generateSingleColumnContent(i) +
                                '</div>';
              cascaderContainer.insertAdjacentHTML('beforeend', newColHtml);
              
              // 绑定新列的事件
              const newCol = cascaderContainer.querySelector(`.cascader-col[data-level="${i}"]`);
              bindColumnEvents(newCol);
            }
          }
          
          // 恢复滚动位置
          restoreScrollPositions();
        }
        
        // 更新单个列的内容
        function updateSingleColumn(col, levelIndex) {
          const savedScrollTop = col.scrollTop;
          col.innerHTML = generateSingleColumnContent(levelIndex);
          col.scrollTop = savedScrollTop;
          bindColumnEvents(col);
        }
        
        // 生成单个列的内容
        function generateSingleColumnContent(levelIndex) {
          const header = levelIndex === 0 ? '' : (trail[levelIndex-1] && trail[levelIndex-1].name ? trail[levelIndex-1].name : '');
          let html = '';
          
          if (header) {
            html += '<div style="padding:6px 10px; font-size:12px; color:var(--text-secondary); border-bottom:1px solid var(--border-color); font-weight: 500;">' + header + '</div>';
          }
          
          const list = levels[levelIndex] || [];
          html += list.map(function(n) {
            const leaf = !n.children || n.children.length === 0;
            const arrow = leaf ? '' : '<span class="arrow-area" style="padding-left:8px; color:var(--text-secondary); cursor:pointer;">›</span>';
            const selectBtn = leaf ? '' : '<span class="select-btn" title="选择此项" style="margin-left:auto; margin-right:4px; padding:0 4px; color:var(--primary); font-size:16px; cursor:pointer;">◎</span>';
            const active = (trail[levelIndex] && trail[levelIndex].name === n.name) ? 'background:var(--category-touch);' : '';
            
            return '<div class="dropdown-item" data-level="' + levelIndex + '" data-leaf="' + (leaf ? '1' : '0') + '" data-name="' + (n.name || '') + '" data-path="' + (n.path || '') + '" style="' + active + '">' +
                   '<span class="label-name" style="flex:1;">' + (n.name || '') + '</span>' +
                   selectBtn +
                   arrow +
                   '</div>';
          }).join('');
          
          return html;
        }
        
        // 恢复滚动位置
        function restoreScrollPositions() {
          setTimeout(() => {
            for (let i = 0; i < levels.length; i++) {
              const col = menu.querySelector(`.cascader-col[data-level="${i}"]`);
              if (col && scrollPositions[i] !== undefined) {
                col.scrollTop = scrollPositions[i];
              }
            }
          }, 0);
        }
        
        // 为单个列绑定事件
        function bindColumnEvents(col) {
          const items = col.querySelectorAll('.dropdown-item');
          Array.prototype.forEach.call(items, function(item) {
            item.onclick = handleCascaderItemClick;
          });
        }
        
        // 处理级联选择器项目点击
        function handleCascaderItemClick(e) {
          // Save scroll positions before any changes
          for (let j = 0; j < levels.length; j++) {
            const col = menu.querySelector(`.cascader-col[data-level="${j}"]`);
            if (col) {
              scrollPositions[j] = col.scrollTop;
            }
          }
          
          // Check if clicked target is the Select Button or if it's a leaf node
          const isSelectBtn = e.target.classList.contains('select-btn');
          const isArrow = e.target.classList.contains('arrow-area');
          
          const i = Number(this.getAttribute('data-level')) || 0;
          const leaf = this.getAttribute('data-leaf') === '1';
          const name = this.getAttribute('data-name') || '';
          const path = this.getAttribute('data-path') || '';
          const colList = levels[i] || [];
          const item = colList.find(function(n) { return n.name === name; }) || null;
          if (!item) return;

          // If arrow is clicked, or it's a non-leaf item and NOT the select button -> Expand only
          if (!leaf && (isArrow || !isSelectBtn)) {
            trail = trail.slice(0, i);
            trail[i] = item;
            levels = levels.slice(0, i + 1);
            levels[i + 1] = Array.isArray(item.children) ? filterExcelHeaders(item.children) : [];
            updateSearchResults();
            return;
          }

          // Otherwise (Leaf clicked OR Select Button clicked) -> Save
          menu.style.display = 'none';
          
          // Build path
          const selectedPathSuffix = trail.slice(0, i).map(function(t) { return t.name; }).concat([name]).join('/');
          
          // Prepend prefix if exists
          let finalPath = selectedPathSuffix;
          if (window.__labelPathPrefix) {
            const prefix = window.__labelPathPrefix.endsWith('/') ? window.__labelPathPrefix : (window.__labelPathPrefix + '/');
            finalPath = prefix + selectedPathSuffix;
          } else if (path) {
            finalPath = path;
          }
          
          link.textContent = finalPath;
          saveSelection(finalPath);
        }
        
        // 绑定搜索结果和级联选择器的事件
        function bindResultEvents() {
          // Handle search result clicks
          Array.prototype.forEach.call(menu.querySelectorAll('.search-result-item'), function(it){
            it.onclick = function(e) {
              const name = this.getAttribute('data-name') || '';
              const fullPath = this.getAttribute('data-path') || '';
              
              menu.style.display = 'none';
              link.textContent = fullPath;
              
              // Save the selected path
              saveSelection(fullPath);
            };
          });
          
          // Handle normal cascader clicks
          Array.prototype.forEach.call(menu.querySelectorAll('.cascader-col .dropdown-item'), function(it){
            it.onclick = handleCascaderItemClick;
          });
        }
        
        menu.onmousedown=function(e){ e.preventDefault(); };
        
        // 初始绑定事件
        bindResultEvents();
      };
      
      // Helper function to save selection
      async function saveSelection(finalPath) {
        try{
          const projId = (entity && entity.type==='project') ? (entity.id || 0) : ((extras && extras.project_id) || 0);
          const wid = Number(entity && entity.type!=='project' ? (entity.id||0) : 0);
          const payload = { label_path: finalPath };
          
          if (entity.type==='project'){
            const res = await fetch(API + '/projects/' + projId, { method:'PUT', headers:{ 'Content-Type':'application/json', Authorization:'Bearer '+token }, body: JSON.stringify(payload) });
            if(!res.ok){ const txt = await res.text(); alert('保存失败(' + res.status + '): ' + txt); }
          } else {
            // Save the work item label
            const res2 = await fetch(API + '/work-items/' + wid, { method:'PATCH', headers:{ 'Content-Type':'application/json', Authorization:'Bearer '+token }, body: JSON.stringify(payload) });
            if(!res2.ok){ 
              const t2 = await res2.text(); 
              alert('保存失败(' + res2.status + '): ' + t2); 
              return;
            }
            
            // Check if this is a JOB (has subtasks) and implement label inheritance
            const rawItem = (extras && extras.rawItem) || null;
            const isJob = rawItem && (rawItem.kind === 'JOB' || (Array.isArray(rawItem.subtasks) && rawItem.subtasks.length > 0));
            
            if (isJob && finalPath) {
              try {
                // Use subtasks from rawItem directly (already loaded with page)
                const subtasks = rawItem.subtasks || [];
                
                // Find all subtasks with empty labels
                const emptyLabelTasks = subtasks.filter(function(task) {
                  const label = task.label_path || '';
                  return !label.trim();
                });
                
                if (emptyLabelTasks.length > 0) {
                    // Batch update all empty-label tasks
                    const updatePromises = emptyLabelTasks.map(function(task) {
                      return fetch(API + '/work-items/' + task.id, {
                        method: 'PATCH',
                        headers: { 
                          'Content-Type': 'application/json', 
                          Authorization: 'Bearer ' + token 
                        },
                        body: JSON.stringify({ label_path: finalPath })
                      });
                    });
                    
                    await Promise.all(updatePromises);
                    
                    // Show success message with count
                    if (window.showToast) {
                      window.showToast('标签已保存，同时更新了' + emptyLabelTasks.length + '个子任务', 'success');
                    }
                    
                    // Trigger page refresh if available
                    if (typeof window.fetchJob === 'function') {
                      setTimeout(function() { window.fetchJob(); }, 500);
                    } else if (typeof window.location !== 'undefined' && typeof window.location.reload === 'function') {
                      setTimeout(function() { window.location.reload(); }, 800);
                    }
                }
              } catch (inheritError) {
                // 标签继承失败，静默处理
                // Don't show error to user - JOB label was saved successfully
              }
            }
          }
        }catch(e){ 
          console.error('[labels] save error', e);
        }
      }
      
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
          } catch(e) { 
            // 静默处理错误
          }
      } else {
          window.__labelPathPrefix = '';
      }

      openMenu(list);
    };
  } catch(_){}
}
