/* vch-fixfinder v1: platform filter + open tracking */
(function(){
  var ls;try{ls=window.localStorage;}catch(e){ls=null;}
  document.querySelectorAll('.vfx').forEach(function(box){
    var bar=box.querySelector('.vfx-filter'),btns=box.querySelectorAll('.vfx-filter button'),cards=box.querySelectorAll('.vfx-item'),out=box.querySelector('.vfx-count');
    function show(p,announce){
      var n=0;cards.forEach(function(c){var pl=c.getAttribute('data-pl'),on=(p==='all'||pl==='both'||pl===p);c.parentNode.hidden=!on;if(on)n++;});
      btns.forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-pl')===p?'true':'false');});
      if(announce&&out)out.textContent=n+' fixes shown';
      if(ls){try{ls.setItem('vch-fix',p);}catch(e){}}
    }
    btns.forEach(function(b){b.addEventListener('click',function(){show(b.getAttribute('data-pl'),true);});});
    var saved=ls&&ls.getItem('vch-fix');show(saved==='ps'||saved==='xb'?saved:'all',false);
    bar.hidden=false;
    cards.forEach(function(c){c.addEventListener('toggle',function(){if(c.open){try{if(window.gtag)gtag('event','fix_finder_open',{issue_id:c.getAttribute('data-id')});}catch(e){}}});});
  });
})();
