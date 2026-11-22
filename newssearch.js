/* vch-newssearch v1: news archive search + topic filter (no storage) */
(function(){
  var box=document.querySelector('.vns');if(!box)return;
  var tools=box.querySelector('.vns-tools'),q=box.querySelector('.vns-q'),btns=box.querySelectorAll('.vns-chips button'),
      items=box.querySelectorAll('.vns-list>li'),out=box.querySelector('.vns-count'),empty=box.querySelector('.vns-empty'),
      clear=box.querySelector('.vns-clear'),total=items.length,topic='all',timer;
  function norm(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim();}
  var txt=[];items.forEach(function(li){txt.push(norm(li.textContent+' '+li.getAttribute('data-topics')));});
  function sync(){try{var u=new URL(location.href);u.searchParams.delete('q');u.searchParams.delete('topic');
    if(q.value.trim())u.searchParams.set('q',q.value.trim().slice(0,60));if(topic!=='all')u.searchParams.set('topic',topic);
    history.replaceState(null,'',u.pathname+u.search+u.hash);}catch(e){}}
  function render(){
    var words=norm(q.value).split(' ').filter(Boolean),n=0;
    items.forEach(function(li,i){var ok=(topic==='all'||(' '+li.getAttribute('data-topics')+' ').indexOf(' '+topic+' ')>-1)&&
      words.every(function(w){return txt[i].indexOf(w)>-1;});li.hidden=!ok;if(ok)n++;});
    out.textContent=(n===total?'All '+total:n+' of '+total)+' stories';
    empty.hidden=n!==0;
  }
  function setTopic(t,track){topic=t;btns.forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-topic')===t));});
    render();sync();if(track){try{if(window.gtag)gtag('event','news_filter',{topic_id:t});}catch(e){}}}
  btns.forEach(function(b){b.addEventListener('click',function(){setTopic(b.getAttribute('data-topic'),true);});});
  q.addEventListener('input',function(){render();clearTimeout(timer);timer=setTimeout(sync,400);});
  q.addEventListener('keydown',function(ev){if(ev.key==='Escape'){q.value='';render();sync();}});
  clear.addEventListener('click',function(){q.value='';setTopic('all',false);q.focus();});
  try{var p=new URLSearchParams(location.search),pq=p.get('q'),pt=p.get('topic');if(pq)q.value=pq.slice(0,60);
    var ok=false;btns.forEach(function(b){if(b.getAttribute('data-topic')===pt)ok=true;});if(ok)topic=pt;}catch(e){}
  tools.hidden=false;setTopic(topic,false);
})();
