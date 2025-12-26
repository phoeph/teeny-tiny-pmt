(function(){
  // 使用全局的时间格式化函数，如果存在的话
  function __fmtCST(s){
    // 优先使用全局工具
    if(window.__fmtCST && window.__fmtCST !== __fmtCST){
      return window.__fmtCST(s);
    }
    if(window.DateTimeUtils && window.DateTimeUtils.formatCST){
      return window.DateTimeUtils.formatCST(s);
    }
    // 本地实现
    try{
      if(!s) return '';
      var d=new Date(s);
      if(isNaN(d.getTime())) return String(s||'');
      // 转换为东八区时间
      var cst = new Date(d.getTime() + 8*60*60*1000);
      var y=cst.getUTCFullYear();
      var m=String(cst.getUTCMonth()+1).padStart(2,'0');
      var dd=String(cst.getUTCDate()).padStart(2,'0');
      var hh=String(cst.getUTCHours()).padStart(2,'0');
      var mm=String(cst.getUTCMinutes()).padStart(2,'0');
      var ss=String(cst.getUTCSeconds()).padStart(2,'0');
      return y+'-'+m+'-'+dd+' '+hh+':'+mm+':'+ss;
    }catch(_){
      return String(s||'');
    }
  }

  function __getOperationTypeLabel(type){
    var labels={
      'CREATE_PROJECT': '创建项目',
      'UPDATE_PROJECT': '更新项目',
      'DELETE_PROJECT': '删除项目',
      'ADD_MEMBER': '添加成员',
      'REMOVE_MEMBER': '移除成员',
      'CREATE_TASK': '创建任务',
      'UPDATE_TASK': '更新任务',
      'DELETE_TASK': '删除任务',
      'MOVE_TASK': '移动任务',
      'ASSIGN_TASK': '分配任务',
      'CHANGE_TASK_STATUS': '变更任务状态',
      'CREATE_JOB': '创建作业',
      'UPDATE_JOB': '更新作业',
      'DELETE_JOB': '删除作业',
      'CHANGE_JOB_STATUS': '变更作业状态',
      'ADD_COMMENT': '添加评论',
      'UPDATE_COMMENT': '更新评论',
      'DELETE_COMMENT': '删除评论',
      'START_WATCHING': '开始关注',
      'STOP_WATCHING': '取消关注',
      // 小写版本兼容
      'create_project': '创建项目',
      'update_project': '更新项目',
      'delete_project': '删除项目',
      'add_member': '添加成员',
      'remove_member': '移除成员',
      'create_task': '创建任务',
      'update_task': '更新任务',
      'delete_task': '删除任务',
      'move_task': '移动任务',
      'assign_task': '分配任务',
      'change_task_status': '变更任务状态',
      'create_job': '创建作业',
      'update_job': '更新作业',
      'delete_job': '删除作业',
      'change_job_status': '变更作业状态',
      'add_comment': '添加评论',
      'update_comment': '更新评论',
      'delete_comment': '删除评论',
      'start_watching': '开始关注',
      'stop_watching': '取消关注'
    };
    return labels[type] || type;
  }

  function __getEntityTypeLabel(type){
    var labels={
      'project': '项目',
      'work_item': '工作项',
      'job': '作业',
      'comment': '评论'
    };
    return labels[type] || type;
  }

  function __getResultStatusLabel(status){
    var labels={
      'success': '成功',
      'failure': '失败'
    };
    return labels[status] || status;
  }

  function __getResultStatusColor(status){
    var colors={
      'success': 'var(--success)',
      'failure': 'var(--danger)'
    };
    return colors[status] || 'var(--text-secondary)';
  }

  // 字段名称翻译
  function __getFieldLabel(fieldName){
    var labels={
      'title': '标题',
      'name': '名称',
      'description': '描述',
      'status': '状态',
      'priority': '优先级',
      'assignee': '负责人',
      'assignee_id': '负责人',
      'owner': '负责人',
      'owner_id': '负责人',
      'reporter': '报告人',
      'reporter_id': '报告人',
      'creator': '报告人',
      'creator_id': '报告人',
      'due_date': '截止日期',
      'start_date': '开始日期',
      'end_date': '结束日期',
      'estimated_hours': '预估工时',
      'actual_hours': '实际工时',
      'progress': '进度',
      'parent_id': '父任务',
      'project_id': '所属项目',
      'type': '类型',
      'tags': '标签',
      'content': '内容',
      'is_archived': '归档状态',
      'order': '排序',
      'color': '颜色',
      'icon': '图标'
    };
    return labels[fieldName] || fieldName;
  }

  // 字段值翻译（针对枚举类型）
  function __getValueLabel(fieldName, value){
    if(value === null || value === undefined || value === '') return '(空)';
    
    // 状态值翻译
    var statusLabels={
      'todo': '待办',
      'in_progress': '进行中',
      'done': '已完成',
      'blocked': '已阻塞',
      'cancelled': '已取消',
      'pending': '待处理',
      'completed': '已完成',
      'closed': '已关闭',
      'open': '打开',
      'resolved': '已解决'
    };
    
    // 优先级值翻译
    var priorityLabels={
      'low': '低',
      'medium': '中',
      'high': '高',
      'urgent': '紧急',
      'critical': '严重'
    };
    
    // 类型值翻译
    var typeLabels={
      'task': '任务',
      'bug': '缺陷',
      'feature': '功能',
      'story': '故事',
      'epic': '史诗',
      'subtask': '子任务'
    };
    
    // 布尔值翻译
    if(fieldName === 'is_archived'){
      return value === 'true' || value === true ? '是' : '否';
    }
    
    // 根据字段名选择翻译表
    if(fieldName === 'status'){
      return statusLabels[value] || value;
    }
    if(fieldName === 'priority'){
      return priorityLabels[value] || value;
    }
    if(fieldName === 'type'){
      return typeLabels[value] || value;
    }
    
    return value;
  }

  // 生成变更描述文本
  function __formatChangeDescription(fieldName, oldValue, newValue){
    var fieldLabel = __getFieldLabel(fieldName);
    var oldLabel = __getValueLabel(fieldName, oldValue);
    var newLabel = __getValueLabel(fieldName, newValue);
    
    // 如果旧值为空，表示新增
    if(!oldValue || oldValue === '(空)'){
      return '设置 ' + fieldLabel + ' 为 ' + newLabel;
    }
    // 如果新值为空，表示清除
    if(!newValue || newValue === '(空)'){
      return '清除了 ' + fieldLabel + '（原值：' + oldLabel + '）';
    }
    // 正常修改
    return '将 ' + fieldLabel + ' 从 ' + oldLabel + ' 修改为 ' + newLabel;
  }

  // HTML 转义函数
  function __escapeHtml(text){
    if(!text) return '';
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function init(cfg){
    var entityType=cfg&&cfg.entityType||'work_item';
    var entityId=cfg&&cfg.entityId||0;
    var sel=cfg&&cfg.selectors||{};
    var listId=sel.listId||'historyList';
    var loadingId=sel.loadingId||'historyLoading';
    var emptyId=sel.emptyId||'historyEmpty';
    var errorId=sel.errorId||'historyError';
    var paginationId=sel.paginationId||'historyPagination';

    var currentPage=1;
    var pageSize=20;
    var totalPages=1;
    var totalItems=0;

    function showLoading(){
      var el=document.getElementById(loadingId);
      if(el){
        el.className='activity-loading';
        el.style.display='flex';
      }
      var listEl=document.getElementById(listId);
      if(listEl) listEl.style.display='none';
      var emptyEl=document.getElementById(emptyId);
      if(emptyEl) emptyEl.style.display='none';
      var errorEl=document.getElementById(errorId);
      if(errorEl) errorEl.style.display='none';
      var paginationEl=document.getElementById(paginationId);
      if(paginationEl) paginationEl.style.display='none';
    }

    function hideLoading(){
      var el=document.getElementById(loadingId);
      if(el) el.style.display='none';
    }

    function showEmpty(){
      var el=document.getElementById(emptyId);
      if(el){
        el.className='activity-empty';
        el.innerHTML='<div class="activity-empty-icon"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></div><div class="activity-empty-title">暂无操作记录</div><div class="activity-empty-desc">当前还没有任何操作历史</div>';
        el.style.display='flex';
      }
      var listEl=document.getElementById(listId);
      if(listEl) listEl.style.display='none';
      var errorEl=document.getElementById(errorId);
      if(errorEl) errorEl.style.display='none';
      var paginationEl=document.getElementById(paginationId);
      if(paginationEl) paginationEl.style.display='none';
    }

    function showError(msg){
      var el=document.getElementById(errorId);
      if(el){
        el.className='activity-error';
        el.textContent=msg||'加载失败';
        el.style.display='flex';
      }
      var listEl=document.getElementById(listId);
      if(listEl) listEl.style.display='none';
      var emptyEl=document.getElementById(emptyId);
      if(emptyEl) emptyEl.style.display='none';
      var paginationEl=document.getElementById(paginationId);
      if(paginationEl) paginationEl.style.display='none';
    }

    function hideAllStates(){
      var el=document.getElementById(loadingId);
      if(el) el.style.display='none';
      var emptyEl=document.getElementById(emptyId);
      if(emptyEl) emptyEl.style.display='none';
      var errorEl=document.getElementById(errorId);
      if(errorEl) errorEl.style.display='none';
    }

    function renderPagination(){
      var paginationEl=document.getElementById(paginationId);
      if(!paginationEl) return;

      paginationEl.innerHTML='';
      paginationEl.className='history-pagination';

      if(totalPages<=1){
        paginationEl.style.display='none';
        return;
      }

      paginationEl.style.display='flex';

      var prevBtn=document.createElement('button');
      prevBtn.textContent='上一页';
      prevBtn.className='history-pagination-btn';
      prevBtn.disabled=currentPage<=1;
      if(currentPage>1){
        prevBtn.onclick=function(){
          currentPage--;
          load();
        };
      }
      paginationEl.appendChild(prevBtn);

      var infoSpan=document.createElement('span');
      infoSpan.textContent=currentPage+' / '+totalPages;
      infoSpan.className='history-pagination-info';
      paginationEl.appendChild(infoSpan);

      var nextBtn=document.createElement('button');
      nextBtn.textContent='下一页';
      nextBtn.className='history-pagination-btn';
      nextBtn.disabled=currentPage>=totalPages;
      if(currentPage<totalPages){
        nextBtn.onclick=function(){
          currentPage++;
          load();
        };
      }
      paginationEl.appendChild(nextBtn);
    }

    function renderHistoryItem(item){
      // 使用新的卡片式布局
      var wrap=document.createElement('div');
      wrap.className='history-card';

      // 头像
      var avatar=document.createElement('div');
      avatar.className='history-card-avatar';
      avatar.textContent=(item.username||'').substring(0,1)||'用';
      wrap.appendChild(avatar);

      // 内容区域
      var body=document.createElement('div');
      body.className='history-card-body';

      // 第一行：时间 + 操作人 + 操作类型 + 状态
      var header=document.createElement('div');
      header.className='history-card-header';

      // 1. 操作时间
      var time=document.createElement('span');
      time.className='history-card-time';
      time.textContent=__fmtCST(item.created_at);
      header.appendChild(time);

      // 2. 操作人
      var author=document.createElement('span');
      author.className='history-card-author';
      author.textContent=item.username||'未知用户';
      header.appendChild(author);

      // 3. 操作类型
      var action=document.createElement('span');
      action.className='history-card-action';
      action.textContent=__getOperationTypeLabel(item.operation_type);
      header.appendChild(action);

      // 操作结果状态
      var statusBadge=document.createElement('span');
      statusBadge.className='history-card-status '+(item.result_status==='success'?'success':'failure');
      statusBadge.textContent=__getResultStatusLabel(item.result_status);
      header.appendChild(statusBadge);

      body.appendChild(header);

      // 第二行：变更详情
      if(item.field_name){
        // 有字段变更信息：显示 字段: 旧值 → 新值
        var changeRow=document.createElement('div');
        changeRow.className='history-card-change-row';

        // 字段名
        var fieldLabel=document.createElement('span');
        fieldLabel.className='history-card-field';
        fieldLabel.textContent=__getFieldLabel(item.field_name)+':';
        changeRow.appendChild(fieldLabel);

        // 旧值
        var oldVal=document.createElement('span');
        oldVal.className='history-card-old-value';
        oldVal.textContent=__getValueLabel(item.field_name, item.old_value);
        changeRow.appendChild(oldVal);

        // 箭头
        var arrow=document.createElement('span');
        arrow.className='history-card-arrow';
        arrow.textContent='→';
        changeRow.appendChild(arrow);

        // 新值
        var newVal=document.createElement('span');
        newVal.className='history-card-new-value';
        newVal.textContent=__getValueLabel(item.field_name, item.new_value);
        changeRow.appendChild(newVal);

        body.appendChild(changeRow);
      }else if(item.operation_content){
        // 没有字段变更信息：显示操作内容（旧数据兼容）
        var content=document.createElement('div');
        content.className='history-card-content';
        var contentText = item.operation_content;
        var opType = (item.operation_type || '').toLowerCase();
        
        // 特殊处理评论类型的操作
        if(opType === 'add_comment' || opType === 'update_comment' || opType === 'delete_comment'){
          // 解析评论内容
          var commentText = contentText;
          var isReply = false;
          
          // 移除 "添加评论: " / "更新评论: " / "删除评论: " 前缀
          commentText = commentText.replace(/^(添加评论|更新评论|删除评论)[:：]\s*/, '');
          
          // 移除 [reply:xxx] 前缀
          var replyMatch = commentText.match(/^\[reply:\d+\]\s*/);
          if(replyMatch){
            isReply = true;
            commentText = commentText.replace(replyMatch[0], '');
          }
          
          // 删除评论：显示 旧值 → (已删除) 格式
          if(opType === 'delete_comment'){
            var changeRow = document.createElement('div');
            changeRow.className = 'history-card-change-row';
            
            // 字段名
            var fieldLabel = document.createElement('span');
            fieldLabel.className = 'history-card-field';
            fieldLabel.textContent = isReply ? '回复:' : '评论:';
            changeRow.appendChild(fieldLabel);
            
            // 旧值（被删除的内容）
            var oldVal = document.createElement('span');
            oldVal.className = 'history-card-old-value';
            oldVal.textContent = commentText || '(空)';
            changeRow.appendChild(oldVal);
            
            // 箭头
            var arrow = document.createElement('span');
            arrow.className = 'history-card-arrow';
            arrow.textContent = '→';
            changeRow.appendChild(arrow);
            
            // 新值（已删除）
            var newVal = document.createElement('span');
            newVal.className = 'history-card-new-value history-card-deleted';
            newVal.textContent = '(已删除)';
            changeRow.appendChild(newVal);
            
            body.appendChild(changeRow);
          }else{
            // 添加/更新评论：简化显示
            var commentRow = document.createElement('div');
            commentRow.className = 'history-card-comment';
            
            if(isReply){
              commentRow.innerHTML = '<span class="history-card-comment-label">回复:</span> "' + __escapeHtml(commentText) + '"';
            }else{
              commentRow.innerHTML = '"' + __escapeHtml(commentText) + '"';
            }
            body.appendChild(commentRow);
          }
        }else{
          // 尝试从 operation_content 中解析变更信息
          // 匹配 "将 xxx 从 'yyy' 修改为 'zzz'" 格式
          var changeMatch = contentText.match(/将\s*(.+?)\s*从\s*'(.*)'\s*修改为\s*'(.*)'/);
          if(changeMatch){
            // 解析成功，显示为变更格式
            var changeRow=document.createElement('div');
            changeRow.className='history-card-change-row';

            var fieldLabel=document.createElement('span');
            fieldLabel.className='history-card-field';
            fieldLabel.textContent=__getFieldLabel(changeMatch[1])+':';
            changeRow.appendChild(fieldLabel);

            var oldVal=document.createElement('span');
            oldVal.className='history-card-old-value';
            oldVal.textContent=changeMatch[2]||'(空)';
            changeRow.appendChild(oldVal);

            var arrow=document.createElement('span');
            arrow.className='history-card-arrow';
            arrow.textContent='→';
            changeRow.appendChild(arrow);

            var newVal=document.createElement('span');
            newVal.className='history-card-new-value';
            newVal.textContent=changeMatch[3]||'(空)';
            changeRow.appendChild(newVal);

            body.appendChild(changeRow);
          }else{
            // 旧数据：提取操作对象名称，更友好地显示
            var targetMatch = contentText.match(/[:：]\s*(.+?)(?:\s*\(|$)/);
            if(targetMatch){
              var targetName = targetMatch[1].trim();
              var detailRow = document.createElement('div');
              detailRow.className='history-card-detail-simple';
              detailRow.innerHTML = '<span class="history-card-target-label">操作对象:</span> <span class="history-card-target-name">' + targetName + '</span>';
              body.appendChild(detailRow);
            }else{
              content.textContent=contentText;
              body.appendChild(content);
            }
          }
        }
      }

      // 失败原因
      if(item.failure_reason){
        var failure=document.createElement('div');
        failure.className='history-card-failure';
        failure.textContent='失败原因: '+item.failure_reason;
        body.appendChild(failure);
      }

      wrap.appendChild(body);
      return wrap;
    }

    async function load(){
      if(window.__historyLoading){
        window.__historyLoadPending=true;
        return;
      }
      window.__historyLoading=true;
      showLoading();

      try{
        var currentEntityId=entityId;
        if(entityType==='work_item'){
          currentEntityId=(window.__currentJobId||window.__currentTaskId||entityId)||0;
        }

        if(!(Number.isFinite(currentEntityId)&&currentEntityId>0)){
          showError('无效的实体ID');
          return;
        }

        var url=API+'/operation-logs/'+entityType+'/'+currentEntityId+'?page='+currentPage+'&page_size='+pageSize;
        var res=await fetch(url,{headers:{Authorization:'Bearer '+token}});

        if(!res.ok){
          var errorMsg='加载失败';
          try{
            var data=await res.json();
            errorMsg=data.detail||data.message||errorMsg;
          }catch(_){}
          showError(errorMsg);
          return;
        }

        var result=await res.json();
        var items=result.items||[];
        totalItems=result.total||0;
        totalPages=Math.max(1,Math.ceil(totalItems/pageSize));

        hideAllStates();

        var listEl=document.getElementById(listId);
        if(!listEl){
          showError('列表容器未找到');
          return;
        }

        listEl.innerHTML='';
        listEl.className='history-list';
        listEl.style.display='block';

        if(items.length===0){
          showEmpty();
          return;
        }

        for(var i=0;i<items.length;i++){
          var item=renderHistoryItem(items[i]);
          listEl.appendChild(item);
        }

        renderPagination();

      }catch(e){
        showError('网络错误: '+(e.message||''));
      }finally{
        window.__historyLoading=false;
        hideLoading();
        if(window.__historyLoadPending){
          window.__historyLoadPending=false;
          try{
            await load();
          }catch(_){}
        }
      }
    }

    return {
      load: load,
      refresh: function(){
        currentPage=1;
        return load();
      }
    };
  }

  window.HistoryModule={
    init: init,
    // 全局刷新方法，供外部调用
    refresh: function(){
      if(window.__historyModule && window.__historyModule.refresh){
        window.__historyModule.refresh();
      }
    }
  };
})();
