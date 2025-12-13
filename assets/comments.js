(function(){
  function __fmtCST(s){ try{ if(!s) return ''; var d=new Date(s); if(isNaN(d.getTime())) return String(s||''); var utc = new Date(d.getTime()); var cst = new Date(utc.getTime() + 8*60*60*1000); var y=cst.getUTCFullYear(); var m=String(cst.getUTCMonth()+1).padStart(2,'0'); var dd=String(cst.getUTCDate()).padStart(2,'0'); var hh=String(cst.getUTCHours()).padStart(2,'0'); var mm=String(cst.getUTCMinutes()).padStart(2,'0'); var ss=String(cst.getUTCSeconds()).padStart(2,'0'); return y+'-'+m+'-'+dd+' '+hh+':'+mm+':'+ss; } catch(_){ return String(s||''); } }
  function init(cfg){
    var entityType=cfg&&cfg.entityType||'';
    var entityId=cfg&&cfg.entityId||0;
    var sel=cfg&&cfg.selectors||{};
    var hooks=cfg&&cfg.hooks||{};
    var listId=sel.listId||'';
    var editorId=sel.editorId||'';
    var addBtnId=sel.addBtnId||'';
    var cancelBtnId=sel.cancelBtnId||'';
    var errorId=sel.errorId||'';
    var rx=/^\[reply:(\d+)\]\s*/;
    var MAX_INDENT=1;
    function __clearHash(){ try{ if(location && (location.hash||'').length>0){ if(history && history.replaceState){ history.replaceState(null,'', location.pathname + location.search); } else { location.hash=''; } } }catch(_){ } }
    async function loadAttachments(commentId){
      try{
        var r=await fetch(API+"/attachments/comments/"+commentId,{headers:{Authorization:"Bearer "+token}});
        if(!r.ok) return;
        var items=await r.json();
        var div=document.getElementById("att-"+commentId);
        if(div){ div.innerHTML=(items||[]).map(function(a){ return '<a href="'+API+'/attachments/'+a.id+'" target="_blank">'+a.file_name+'</a>'; }).join(' · '); }
      }catch(_){ }
    }
    async function load(){
      if(window.__commentsLoading){ window.__commentsLoadPending=true; return; }
      window.__commentsLoading=true;
      var list=document.getElementById(listId);
      if(!list) return;
      list.innerHTML='';
      try{
        var url=API+"/comments/"+(entityType==="project"?"project/":"work_item/")+entityId;
        var res=await fetch(url,{headers:{Authorization:"Bearer "+token}});
        if(!res.ok) throw new Error('comments fetch failed');
        var raw=await res.json();
        var items=Array.isArray(raw)?raw:[];
        var map=new Map();
        var children=new Map();
        items.forEach(function(c){
          var m=rx.exec(c.content||'');
          var replyTo=m?parseInt(m[1],10):null;
          var clean=m?(c.content||'').replace(rx,''):(c.content||'');
          var node=Object.assign({},c,{replyTo:replyTo,content:clean});
          map.set(c.id,node);
          if(replyTo!=null){ if(!children.has(replyTo)) children.set(replyTo,[]); children.get(replyTo).push(node); }
        });
        window.__expandedReplies=window.__expandedReplies||{};
        try{ Object.keys(window.__expandedReplies).forEach(function(k){ var id=parseInt(k,10); var cur=map.get(id); while(cur&&cur.replyTo!=null){ cur=map.get(cur.replyTo); } if(cur&&cur.id!==id){ window.__expandedReplies[cur.id]=true; } }); }catch(_){ }
        try{
          var h=(location.hash||'').trim(); var qId=new URLSearchParams(location.search).get('commentId');
          var targetIdStr=h&&h.startsWith('#comment-')?h.slice(9):(qId||'');
          var targetId=parseInt(targetIdStr||'',10);
          if(Number.isFinite(targetId)&&map.has(targetId)){
            var root=map.get(targetId);
            while(root&&root.replyTo!=null){ root=map.get(root.replyTo); }
            if(root){
              window.__expandedReplies[root.id]=true;
              var kids=(children.get(root.id)||[]).sort(function(a,b){ return new Date(a.created_at)-new Date(b.created_at); });
              var idx=kids.findIndex(function(x){ return Number(x.id)===targetId; });
              if(idx>=0){ var size=10; var page=Math.floor(idx/size)+1; window.__replyPager=window.__replyPager||{}; window.__replyPager[root.id]={page:page,size:size}; }
            }
          }
        }catch(_){ }
        var tops=items.filter(function(c){ var m=rx.exec(c.content||''); return !m; }).sort(function(a,b){ return new Date(a.created_at)-new Date(b.created_at); });
        function depthFor(id){ var d=0; var cur=map.get(id); var seen=new Set(); while(cur&&cur.replyTo!=null&&!seen.has(cur.id)){ seen.add(cur.id); d++; cur=map.get(cur.replyTo); if(d>32)break; } return d; }
        async function renderOne(c,depth,target){
          var wrap=document.createElement('div');
          wrap.id='comment-'+c.id;
          wrap.style.border='none';
          wrap.style.borderBottom='1px solid var(--border-color)';
          wrap.style.borderRadius='0';
          wrap.style.padding='8px 0';
          wrap.style.margin='0';
          var d=Math.min((depth||0),MAX_INDENT);
          if(d>0){ wrap.style.marginLeft=(16*d)+'px'; wrap.style.borderLeft='2px solid var(--border-color)'; wrap.style.paddingLeft='8px'; wrap.style.borderBottom='none'; }
          var authorInfo=c&&c.author||{};
          var authorLabel=(authorInfo.full_name||authorInfo.username||authorInfo.email_prefix)||('用户#'+c.author_id);
          var avatarText=(authorLabel&&authorLabel.substring(0,1))||'用';
          var headStyle='display:flex;align-items:center;gap:8px;color:var(--text-main);';
          var avatarStyle='width:20px;height:20px;border-radius:50%;background:var(--border-color);color:var(--text-main);font-size:12px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;';
          if(c.replyTo!=null){
            var parent=map.get(c.replyTo);
            var parentInfo=parent&&parent.author||{};
            var parentLabel=(parentInfo.full_name||parentInfo.username||parentInfo.email_prefix)||('用户#'+(parent?parent.author_id:''));
            wrap.innerHTML='<div class="cm-head" style="'+headStyle+'"><span class="cm-avatar" style="'+avatarStyle+'" aria-hidden="true">'+avatarText+'</span><span class="cm-author">'+authorLabel+'</span><span class="cm-arrow" style="color:var(--text-secondary);" aria-hidden="true">▸</span><span class="cm-replyto">'+parentLabel+'</span><div style="margin-left:auto;display:flex;gap:8px;align-items:center;"><a class="cm-action-reply" href="javascript:void(0)" role="button" data-comment-id="'+c.id+'" style="color:var(--primary)">回复</a><a class="cm-action-menu" href="javascript:void(0)" role="button" aria-haspopup="menu" aria-expanded="false" data-comment-id="'+c.id+'" style="color:var(--primary)">•••</a></div></div>'+
              '<div class="comment-content" style="color:var(--text-main);">'+(c.content||'')+'</div>'+
              '<div style="color:var(--text-secondary); font-size:12px;">'+__fmtCST(c.created_at)+'</div>';
          } else {
            wrap.innerHTML='<div class="cm-head" style="'+headStyle+'"><span class="cm-avatar" style="'+avatarStyle+'" aria-hidden="true">'+avatarText+'</span><span class="cm-author">'+authorLabel+'</span><div style="margin-left:auto;display:flex;gap:8px;align-items:center;"><a class="cm-action-reply" href="javascript:void(0)" role="button" data-comment-id="'+c.id+'" style="color:var(--primary)">回复</a><a class="cm-action-menu" href="javascript:void(0)" role="button" aria-haspopup="menu" aria-expanded="false" data-comment-id="'+c.id+'" style="color:var(--primary)">•••</a></div></div>'+
              '<div class="comment-content" style="color:var(--text-main);">'+(c.content||'')+'</div>'+
              '<div style="color:var(--text-secondary); font-size:12px;">'+__fmtCST(c.created_at)+'</div>';
          } try{ var contentEl=wrap.querySelector('.comment-content'); if(contentEl){ contentEl.querySelectorAll('.mention').forEach(function(m){ var a=document.createElement('a'); a.href='#comment-'+c.id; a.textContent=m.textContent; contentEl.replaceChild(a,m); }); } }catch(_){ }
          if(window.__commentsLoading){ try{ var dup=document.getElementById('comment-'+c.id); if(dup&&dup!==wrap){ /* 合并渲染：移除旧实例 */ dup.remove(); } }catch(_){ } }
          var attachDiv=document.createElement('div'); attachDiv.style.marginTop='6px'; attachDiv.id='att-'+c.id; wrap.appendChild(attachDiv);
          
          var parent=target||list; parent.appendChild(wrap);
          await loadAttachments(c.id);
          var kids=(children.get(c.id)||[]).sort(function(a,b){ return new Date(a.created_at)-new Date(b.created_at); });
          var expanded=(window.__expandedByComment&&window.__expandedByComment[c.id])||false;
          var replies=document.createElement('div'); replies.id='replies-'+c.id; wrap.appendChild(replies);
          if(window.__anim && window.__anim.id===c.id && window.__anim.type==='collapse'){ try{ replies.style.transition='opacity 0.2s ease'; replies.style.opacity='0'; requestAnimationFrame(function(){ replies.style.opacity='1'; }); }catch(_){ } }
          var nextDepth=Math.min((depth||0)+1,MAX_INDENT);
          var pagerBar=document.createElement('div'); pagerBar.style.fontSize='12px'; pagerBar.style.marginLeft='16px'; pagerBar.style.display='flex'; pagerBar.style.alignItems='center'; pagerBar.style.gap='8px';
          async function renderReplyPage(){ var info=(window.__replyPager&&window.__replyPager[c.id])||{page:1,size:10}; var total=kids.length; var pageCount=Math.max(1,Math.ceil(total/info.size)); var page=Math.min(info.page,pageCount); window.__replyPager=window.__replyPager||{}; window.__replyPager[c.id]={page:page,size:info.size}; replies.innerHTML=''; var start=(page-1)*info.size; var end=Math.min(start+info.size,total); for(var i=start;i<end;i++){ await renderOne(kids[i],nextDepth,replies); } pagerBar.innerHTML=''; var prev=document.createElement('a'); prev.href='javascript:void(0)'; prev.textContent='上一页'; prev.style.color=page>1?'var(--primary)':'var(--text-secondary)'; if(page>1){ prev.onclick=async function(){ window.__replyPager[c.id].page=page-1; await renderReplyPage(); }; } var infoSpan=document.createElement('span'); infoSpan.style.color='var(--text-secondary)'; infoSpan.textContent=page+'/'+pageCount; var next=document.createElement('a'); next.href='javascript:void(0)'; next.textContent='下一页'; next.style.color=page<pageCount?'var(--primary)':'var(--text-secondary)'; if(page<pageCount){ next.onclick=async function(){ window.__replyPager[c.id].page=page+1; await renderReplyPage(); }; } pagerBar.appendChild(prev); pagerBar.appendChild(infoSpan); pagerBar.appendChild(next); }
          function appendToggle(exp){ if(kids.length>1){ var t=document.createElement('a'); t.href='javascript:void(0)'; t.textContent=exp?'收起回复':'展开全部'; t.className='cm-toggle'; t.style.color='var(--primary)'; t.style.fontSize='12px'; t.style.marginLeft='16px'; t.setAttribute('data-comment-id', String(c.id)); t.setAttribute('role','button'); t.setAttribute('aria-controls','replies-'+c.id); t.setAttribute('aria-expanded', exp?'true':'false'); wrap.appendChild(t); } }
          if(kids.length>0){
            if(!expanded){
              replies.style.opacity='0';
              await renderOne(kids[0],nextDepth,replies);
              requestAnimationFrame(function(){ replies.style.transition='opacity 0.2s ease'; replies.style.opacity='1'; });
              appendToggle(false);
            } else {
              await renderReplyPage();
              appendToggle(true);
              if(kids.length>10){ wrap.appendChild(pagerBar); }
            }
          }
        }
        for(var t=0;t<tops.length;t++){ await renderOne(map.get(tops[t].id),0,null); }
        try{ if(typeof window.__highlightCid==='number'){ var hi=document.getElementById('comment-'+window.__highlightCid); if(hi){ hi.style.boxShadow='0 0 0 2px var(--primary) inset'; setTimeout(function(){ try{ hi.style.boxShadow=''; }catch(_){ } },1000); } window.__highlightCid=undefined; } }catch(_){ }
        var historyListId=sel.historyListId||'';
        if(historyListId&&hooks.PageHistory&&hooks.PageHistory.renderTo){ hooks.PageHistory.renderTo(historyListId); }
        try{ var h2=(location.hash||'').trim(); var qId2=new URLSearchParams(location.search).get('commentId'); var targetId2=h2&&h2.startsWith('#comment-')?h2.slice(1):(qId2?('comment-'+qId2):''); if(targetId2){ var target=document.getElementById(targetId2); if(target){ try{ target.style.boxShadow='0 0 0 2px var(--primary) inset'; setTimeout(function(){ try{ target.style.boxShadow=''; }catch(_){ } },1500); }catch(_){ } } } }catch(_){ }
        try{ var onHashChange=async function(){ var h3=(location.hash||'').trim(); var tidStr=h3&&h3.startsWith('#comment-')?h3.slice(9):''; var tid=parseInt(tidStr||'',10); if(Number.isFinite(tid)){ try{ window.__expandedReplies=window.__expandedReplies||{}; window.__expandedByComment=window.__expandedByComment||{}; window.__replyPager=window.__replyPager||{}; var root2=map.get(tid); while(root2&&root2.replyTo!=null){ root2=map.get(root2.replyTo); } if(root2){ window.__expandedReplies[root2.id]=true; window.__expandedByComment[root2.id]=true; var kids2=(children.get(root2.id)||[]).sort(function(a,b){ return new Date(a.created_at)-new Date(b.created_at); }); var idx2=kids2.findIndex(function(x){ return Number(x.id)===tid; }); if(idx2>=0){ var size2=10; var page2=Math.floor(idx2/size2)+1; window.__replyPager[root2.id]={page:page2,size:size2}; } } await load(); }catch(_){ } } }; try{ if(window.__cmOnHashChange){ window.removeEventListener('hashchange', window.__cmOnHashChange); } }catch(_){ } window.__cmOnHashChange=onHashChange; window.addEventListener('hashchange',window.__cmOnHashChange); }catch(_){ }
        if(typeof window.__restoreScrollY==='number'){ try{ window.scrollTo({top:window.__restoreScrollY}); }catch(_){ window.scrollTo(0,window.__restoreScrollY); } window.__restoreScrollY=undefined; }
      }catch(e){ var list2=document.getElementById(listId); if(list2){ list2.textContent='评论加载失败'; }
      }
      window.__commentsLoading=false;
      if(window.__commentsLoadPending){ window.__commentsLoadPending=false; try{ await load(); }catch(_){ } }
    }
    (function(){ var wrap=document.getElementById(editorId); var btn=document.getElementById(addBtnId); var cancel=document.getElementById(cancelBtnId); var ed=null; function currentEntityId(){ try{ if(entityType==='work_item'){ return (window.__currentJobId||window.__currentTaskId||entityId)||0; } return entityId||0; }catch(_){ return entityId||0; } } function ensureEditor(){ if(!ed){ ed=createRichEditor(editorId,{ entityType: entityType, entityId: currentEntityId(), saveText:'发布', onSave: async function(html,ev){ if(ev&&ev.preventDefault) ev.preventDefault(); var errEl=errorId?document.getElementById(errorId):null; if(errEl) errEl.textContent=''; var content=(html||'').trim(); if(!content){ if(errEl) errEl.textContent='请输入内容'; return false; } var idVal=currentEntityId(); if(!(Number.isFinite(idVal)&&idVal>0)){ if(errEl) errEl.textContent='加载未完成，请稍后再试'; return false; } try{ if(window.__commentsSubmitting) return false; window.__commentsSubmitting=true; var res=await fetch(API+'/comments/',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:JSON.stringify({ entity_type: entityType, entity_id: idVal, content: content })}); if(!res.ok){ if(hooks.__showErrorFromResponse){ await hooks.__showErrorFromResponse(res); } else { if(errEl) errEl.textContent='发布失败'; } window.__commentsSubmitting=false; return false; } if(hooks.PageHistory&&hooks.PageHistory.log){ hooks.PageHistory.log('发布评论',(entityType==='project'?'项目#':'')+idVal); } window.__restoreScrollY=window.scrollY; __clearHash(); await load(); if(wrap){ wrap.style.display='none'; } if(btn){ btn.style.display='inline-flex'; } if(cancel){ cancel.style.display='none'; } window.__commentsSubmitting=false; return true; }catch(e){ if(errEl) errEl.textContent='网络错误'; window.__commentsSubmitting=false; return false; } }}); } } if(wrap){ wrap.style.display='none'; } if(btn){ btn.onclick=function(ev){ if(ev&&ev.preventDefault) ev.preventDefault(); ensureEditor(); if(wrap){ wrap.style.display='block'; try{ wrap.scrollIntoView({behavior:'smooth',block:'end'}); }catch(_){ } } btn.style.display='none'; if(cancel){ cancel.style.display='inline-flex'; } try{ ed && ed.expand && ed.expand(); }catch(_){ } try{ ed && ed.focus && ed.focus(); }catch(_){ } }; } if(cancel){ cancel.onclick=function(ev){ if(ev&&ev.preventDefault) ev.preventDefault(); if(wrap){ wrap.style.display='none'; } if(btn){ btn.style.display='inline-flex'; } cancel.style.display='none'; try{ ed && ed.collapse && ed.collapse(); }catch(_){ } }; }
      window.showLoadingFor=function(commentId){ try{ var w=document.getElementById('comment-'+commentId); if(!w) return; var ex=w.querySelector('.cm-loading'); if(ex) return; var s=document.createElement('span'); s.className='cm-loading'; s.textContent='加载中…'; s.style.color='var(--text-secondary)'; s.style.fontSize='12px'; s.style.marginLeft='8px'; w.appendChild(s);}catch(_){}};
      window.hideLoadingFor=function(commentId){ try{ var w=document.getElementById('comment-'+commentId); if(!w) return; var ex=w.querySelector('.cm-loading'); if(ex){ ex.remove(); } }catch(_){}};
      // 事件委托：统一处理折叠/展开按钮点击，保持互斥显示与跨端一致性
      try{ var listEl=document.getElementById(listId); if(listEl && !listEl.__cmDelegated){ listEl.addEventListener('click', async function(ev){ var tgt=ev.target; if(ev&&ev.preventDefault) ev.preventDefault(); var el=tgt&&tgt.closest? tgt.closest('a') : null; if(!el) return; var cid=parseInt(el.getAttribute('data-comment-id')||'',10); var cls=el.className||''; if(!Number.isFinite(cid)) return; if(cls.indexOf('cm-toggle')!==-1){ var exp=(window.__expandedByComment&&window.__expandedByComment[cid])||false; window.__expandedByComment=window.__expandedByComment||{}; window.__expandedByComment[cid]=!exp; if(window.showLoadingFor) window.showLoadingFor(cid); window.__restoreScrollY=window.scrollY; await load(); if(window.hideLoadingFor) window.hideLoadingFor(cid); return; }
        if(cls.indexOf('cm-action-menu')!==-1){
          var menu=document.getElementById('cm-ctx-menu'); if(menu) menu.remove();
          menu=document.createElement('div'); menu.id='cm-ctx-menu';
          menu.style.cssText='position:absolute;z-index:9999;background:var(--bg-surface);border:1px solid var(--border-color);border-radius:6px;box-shadow:0 4px 12px rgba(0,0,0,0.15);padding:4px 0;min-width:100px;';
          var mk=function(txt,col,fn){
            var d=document.createElement('div'); d.textContent=txt;
            d.style.cssText='padding:8px 12px;font-size:13px;cursor:pointer;color:'+(col||'var(--text-main)');
            d.onmouseenter=function(){this.style.background='var(--bg-hover)'};
            d.onmouseleave=function(){this.style.background='transparent'};
            d.onclick=function(e){ e.stopPropagation(); menu.remove(); fn(); };
            return d;
          };
          menu.appendChild(mk('编辑',null,function(){
            var wrap=document.getElementById('comment-'+cid); var cEl=wrap?wrap.querySelector('.comment-content'):null; if(!cEl) return;
            var old=cEl.innerHTML; cEl.style.display='none';
            var eid='ed-'+cid; var box=document.getElementById(eid);
            if(!box){ box=document.createElement('div'); box.id=eid; box.style.marginTop='8px'; cEl.parentNode.insertBefore(box,cEl.nextSibling); }
            box.style.display='block';
            var edDiv=document.createElement('div'); edDiv.id='real-ed-'+cid; box.innerHTML=''; box.appendChild(edDiv);
            var can=document.createElement('button'); can.textContent='取消'; can.className='ghost-btn';
            can.style.cssText='margin-top:8px;padding:4px 12px;font-size:12px;border:1px solid var(--border-color);border-radius:4px;background:var(--bg-surface);cursor:pointer;';
            can.onclick=function(){ box.style.display='none'; cEl.style.display='block'; };
            box.appendChild(can);
            var editor=createRichEditor(edDiv.id, { entityType: entityType, entityId: entityId, saveText:'保存', onSave: async function(h){
              try{ var r=await fetch(API+'/comments/'+cid, { method:'PATCH', headers:{'Content-Type':'application/json',Authorization:'Bearer '+token}, body:JSON.stringify({content:h}) });
              if(r.ok){ await load(); return true; } else { alert('保存失败'); return false; } }catch(e){ alert('网络错误'); return false; }
            }});
            editor.setHTML(old);
          }));
          menu.appendChild(mk('删除','var(--danger)',async function(){
            if(!confirm('确定删除?')) return;
            try{ await fetch(API+'/comments/'+cid, { method:'DELETE', headers:{Authorization:'Bearer '+token} }); await load(); }catch(e){}
          }));
          document.body.appendChild(menu);
          var rect=el.getBoundingClientRect(); menu.style.left=(rect.left+window.scrollX-80)+'px'; menu.style.top=(rect.bottom+window.scrollY+4)+'px';
          var closer=function(e){ if(!menu.contains(e.target)) { menu.remove(); document.removeEventListener('mousedown',closer); } };
          setTimeout(function(){ document.addEventListener('mousedown',closer); },0);
          return;
        } if(cls.indexOf('cm-action-reply')!==-1){ var holderId='reply-'+cid; var w=document.getElementById('comment-'+cid); var holder=document.getElementById(holderId); if(!holder){ holder=document.createElement('div'); holder.id=holderId; holder.style.marginTop='6px'; w&&w.appendChild(holder); } function currentEntityId(){ try{ if(entityType==='work_item'){ return (window.__currentJobId||window.__currentTaskId||entityId)||0; } return entityId||0; }catch(_){ return entityId||0; } } var ed=createRichEditor(holderId,{ entityType: entityType, entityId: currentEntityId(), saveText:'发布', onSave: async function(html,e){ if(e&&e.preventDefault) e.preventDefault(); var content=(html||'').trim(); if(!content) return false; var idVal=currentEntityId(); if(!(Number.isFinite(idVal)&&idVal>0)){ return false; } try{ if(window.showLoadingFor) window.showLoadingFor(cid); var r=await fetch(API+'/comments/',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:JSON.stringify({ entity_type: entityType, entity_id: idVal, content: '[reply:'+cid+'] '+content })}); if(!r.ok){ if(window.hideLoadingFor) window.hideLoadingFor(cid); return false; } var data=await r.json(); var newId=(data&&data.id)?data.id:null; window.__expandedByComment=window.__expandedByComment||{}; window.__expandedByComment[cid]=true; if(newId){ try{ location.hash='#comment-'+newId; }catch(_){ } } window.__restoreScrollY=window.scrollY; if(window.hideLoadingFor) window.hideLoadingFor(cid); return true; }catch(_){ if(window.hideLoadingFor) window.hideLoadingFor(cid); return false; } }}); try{ ed && ed.focus && ed.focus(); }catch(_){ } return; } if(cls.indexOf('cm-action-menu')!==-1){ var w2=document.getElementById('comment-'+cid); var head=w2&&w2.querySelector('.cm-head'); var existing=w2&&w2.querySelector('#menu-'+cid); if(existing){ existing.remove(); el.setAttribute('aria-expanded','false'); return; } var item=(window.__commentsCache||[]).find(function(x){ return Number(x.id)===cid; })||null; var me=window.__me||null; var isAdmin=!!window.__isAdmin; var canEditDel=!!(isAdmin||(me&&(item&&(String(me.id)===String(item.author_id))))); var menu=document.createElement('div'); menu.id='menu-'+cid; menu.className='cm-menu'; menu.setAttribute('role','menu'); menu.style.position='absolute'; menu.style.background='var(--bg-surface)'; menu.style.border='1px solid var(--border-color)'; menu.style.borderRadius='6px'; menu.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'; menu.style.padding='6px'; menu.style.fontSize='12px'; menu.style.zIndex='10'; menu.style.right='8px'; menu.style.marginTop='4px'; var html=''; if(canEditDel){ html+='<a href="javascript:void(0)" class="cm-menu-item" role="menuitem" data-action="edit" data-comment-id="'+cid+'" style="display:block;padding:4px 8px;color:var(--text-main)">编辑</a>'; html+='<a href="javascript:void(0)" class="cm-menu-item" role="menuitem" data-action="delete" data-comment-id="'+cid+'" style="display:block;padding:4px 8px;color:var(--danger)">删除</a>'; } menu.innerHTML=html; (head||w2).appendChild(menu); el.setAttribute('aria-expanded','true'); return; } if(cls.indexOf('cm-menu-item')!==-1){ var action=el.getAttribute('data-action'); if(action==='edit'){ var holderId='edit-'+cid; var w3=document.getElementById('comment-'+cid); var holder3=document.getElementById(holderId); if(!holder3){ holder3=document.createElement('div'); holder3.id=holderId; holder3.style.marginTop='6px'; w3&&w3.appendChild(holder3); } var item2=(window.__commentsCache||[]).find(function(x){ return Number(x.id)===cid; })||null; var prefix=(function(){ var m=rx.exec(item2&&item2.content||''); return m?m[0]:''; })(); var ed2=createRichEditor(holderId,{ entityType: entityType, entityId: currentEntityId(), saveText:'发布', onSave: async function(html,e){ if(e&&e.preventDefault) e.preventDefault(); var body=(html||'').trim(); if(!body) return false; try{ if(window.showLoadingFor) window.showLoadingFor(cid); var r=await fetch(API+'/comments/'+cid,{method:'PATCH',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:JSON.stringify({ content: prefix+body })}); if(!r.ok){ if(window.hideLoadingFor) window.hideLoadingFor(cid); return false; } window.__restoreScrollY=window.scrollY; window.__highlightCid=cid; await load(); if(window.hideLoadingFor) window.hideLoadingFor(cid); return true; }catch(_){ if(window.hideLoadingFor) window.hideLoadingFor(cid); return false; } }}); try{ ed2 && ed2.focus && ed2.focus(); }catch(_){ } ed2.setHTML(item2?(item2.content||'').replace(rx,''):('')); var mEl=document.getElementById('menu-'+cid); if(mEl) mEl.remove(); return; } if(action==='delete'){ if(!confirm('确定删除这条评论吗？')) return; try{ if(window.showLoadingFor) window.showLoadingFor(cid); var r=await fetch(API+'/comments/'+cid,{method:'DELETE',headers:{Authorization:'Bearer '+token}}); if(r.ok){ window.__restoreScrollY=window.scrollY; await load(); } if(window.hideLoadingFor) window.hideLoadingFor(cid); }catch(_){ if(window.hideLoadingFor) window.hideLoadingFor(cid); } var mEl2=document.getElementById('menu-'+cid); if(mEl2) mEl2.remove(); return; } } }); listEl.__cmDelegated=true; } }catch(_){ }
    })();
    return { load: load };
  }
  window.CommentsModule={ init: init };
})();
