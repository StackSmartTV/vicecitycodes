/* vch-upnext v1: 'Up next' card after ~60% of a post */
(function(){
  var c=document.querySelector('.vun');if(!c)return;
  var body=document.querySelector('.post-body'),rn=document.querySelector('.read-next');
  try{if(sessionStorage.getItem('vun-x')==='1')return;}catch(e){}
  var blockers=[],shown=false,closed=false,tick=false;
  if(rn)blockers.push(rn);
  document.querySelectorAll('.ad-wrap,ins.adsbygoogle').forEach(function(el){blockers.push(el);});
  function onScreen(el){var r=el.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight;}
  function update(){
    tick=false;if(closed||!body)return;
    var r=body.getBoundingClientRect(),read=(innerHeight-r.top)/Math.max(r.height,1);
    var want=read>0.6&&!blockers.some(onScreen);
    if(want!==shown){shown=want;c.hidden=false;c.classList.toggle('vun-on',want);c.setAttribute('aria-hidden',want?'false':'true');
      c.querySelectorAll('a,button').forEach(function(x){x.tabIndex=want?0:-1;});}
  }
  addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(update);}},{passive:true});
  addEventListener('resize',update);
  c.querySelector('.vun-x').addEventListener('click',function(){closed=true;shown=false;c.classList.remove('vun-on');c.setAttribute('aria-hidden','true');
    try{sessionStorage.setItem('vun-x','1');}catch(e){}});
  c.querySelector('.vun-link').addEventListener('click',function(){try{if(window.gtag)gtag('event','up_next_click',{to:this.getAttribute('href')});}catch(e){}});
  update();
})();
