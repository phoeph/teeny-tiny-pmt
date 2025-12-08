;(function(){
  function hideDropdown(id){ try{ var el=document.getElementById(id); if(el){ el.style.display='none'; } }catch(_){ }
  }
  function hideAllDropdowns(){ try{ document.querySelectorAll('.dropdown').forEach(function(el){ el.style.display='none'; }); }catch(_){ }
    hideDropdown('assigneeDropdown');
    hideDropdown('priorityDropdown');
    hideDropdown('ganttModeDropdown');
    hideDropdown('mentionPanel');
    hideDropdown('colorPanel');
  }
  function closeModalBackdrops(){ try{ document.querySelectorAll('.modal-backdrop').forEach(function(b){ b.style.display='none'; }); }catch(_){ }
    try{ if(typeof closeEditTaskModal==='function') closeEditTaskModal(); }catch(_){ }
    try{ if(typeof closeEditJobModal==='function') closeEditJobModal(); }catch(_){ }
    try{ if(typeof closeCreateTaskModal==='function') closeCreateTaskModal(); }catch(_){ }
    try{ if(typeof closeCreateJobModal==='function') closeCreateJobModal(); }catch(_){ }
  }
  function removeAllCommentModals(){ try{ document.querySelectorAll('.cm-backdrop').forEach(function(b){ try{ document.body.removeChild(b); }catch(_){ b.remove(); } }); }catch(_){ }
  }
  function hideCommentEditor(){ try{ var wrap=document.getElementById('commentEditor'); var add=document.getElementById('addCommentBtn'); var cancel=document.getElementById('cancelCommentBtn'); if(wrap && wrap.style.display!=='none'){ wrap.style.display='none'; if(add) add.style.display='inline-flex'; if(cancel) cancel.style.display='none'; } }catch(_){ }
  }
  function onEsc(e){ if(e.key==='Escape'){ hideAllDropdowns(); closeModalBackdrops(); } }
  document.addEventListener('keydown', onEsc, true);
  var mo=new MutationObserver(function(){ try{
    document.querySelectorAll('.modal-backdrop').forEach(function(b){ var vis=window.getComputedStyle(b).display!=='none'; if(vis){ var m=b.querySelector('.modal'); if(m && !m.__focused){ var inp=m.querySelector('input, textarea, [contenteditable="true"]'); if(inp){ inp.focus(); if(typeof inp.select==='function') inp.select(); } m.__focused=true; } } });
    document.querySelectorAll('.cm-backdrop').forEach(function(b){ var vis=window.getComputedStyle(b).display!=='none'; if(vis){ var m=b.querySelector('.cm-modal'); if(m && !m.__focused){ var inp=m.querySelector('input, textarea, [contenteditable="true"]'); if(inp){ inp.focus(); if(typeof inp.select==='function') inp.select(); } m.__focused=true; } } });
  }catch(_){ }
  });
  mo.observe(document.body, { attributes:true, childList:true, subtree:true });
})();
