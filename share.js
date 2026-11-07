/* vch-share v1: copy-link + social share bar */
(function(){
  function toast(el,msg){
    var t=el.querySelector('.vshare-toast');if(!t)return;
    t.textContent=msg;t.hidden=false;
    clearTimeout(el._vshareT);el._vshareT=setTimeout(function(){t.hidden=true;t.textContent='';},1800);
  }
  function copy(url,btn,wrap){
    function ok(){
      toast(wrap,'Link copied');
      try{if(window.gtag){gtag('event','share_click',{method:'copy_link'});gtag('event','copy_link',{method:'clipboard'});}}catch(e){}
      btn.setAttribute('aria-pressed','true');
      setTimeout(function(){btn.removeAttribute('aria-pressed');},1800);
    }
    function fail(){
      try{
        var ta=document.createElement('textarea');ta.value=url;ta.setAttribute('readonly','');
        ta.style.position='fixed';ta.style.left='-9999px';document.body.appendChild(ta);
        ta.select();ta.setSelectionRange(0,url.length);
        var done=document.execCommand('copy');document.body.removeChild(ta);
        if(done)ok();else toast(wrap,'Copy failed — long-press the address bar');
      }catch(e){toast(wrap,'Copy failed — long-press the address bar');}
    }
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(url).then(ok).catch(fail);
    }else fail();
  }
  document.addEventListener('click',function(ev){
    var btn=ev.target.closest&&ev.target.closest('.vshare-copy');
    if(!btn)return;
    var wrap=btn.closest('.vshare');if(!wrap)return;
    var url=wrap.getAttribute('data-url')||location.href;
    copy(url,btn,wrap);
  });
  document.addEventListener('click',function(ev){
    var a=ev.target.closest&&ev.target.closest('a.vshare-x,a.vshare-fb');
    if(!a)return;
    try{if(window.gtag)gtag('event','share_click',{method:a.classList.contains('vshare-x')?'x':'facebook'});}catch(e){}
  });
})();
