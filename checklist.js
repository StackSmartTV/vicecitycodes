/* vch-checklist v1: launch-night checklist (device-only storage) */
(function(){
  var ls;try{ls=window.localStorage;ls.setItem('vck-t','1');ls.removeItem('vck-t');}catch(e){ls=null;}
  var K='vch-ckl',done=[];if(ls){try{done=JSON.parse(ls.getItem(K)||'[]')||[];}catch(e){done=[];}}
  document.querySelectorAll('.vck').forEach(function(box){
    var cbs=box.querySelectorAll('input[type=checkbox][data-ck]'),bar=box.querySelector('.vck-bar'),
        prog=box.querySelector('progress'),out=box.querySelector('.vck-count'),reset=box.querySelector('.vck-reset'),fired=false;
    function render(){
      var n=0;cbs.forEach(function(c){if(c.checked)n++;c.closest('li').classList.toggle('vck-done',c.checked);});
      prog.value=n;prog.max=cbs.length;
      out.textContent=n===cbs.length?'All '+n+' done. You are ready for Vice City.':n+' of '+cbs.length+' done';
      box.classList.toggle('vck-all',n===cbs.length);
      return n;
    }
    cbs.forEach(function(c){
      if(done.indexOf(c.getAttribute('data-ck'))>=0)c.checked=true;
      c.addEventListener('change',function(){
        var id=c.getAttribute('data-ck');done=done.filter(function(x){return x!==id;});if(c.checked)done.push(id);
        if(ls){try{ls.setItem(K,JSON.stringify(done));}catch(e){}}
        if(render()===cbs.length&&!fired){fired=true;try{if(window.gtag)gtag('event','launch_checklist_complete');}catch(e){}}
      });
    });
    reset.addEventListener('click',function(){done=[];if(ls){try{ls.removeItem(K);}catch(e){}}cbs.forEach(function(c){c.checked=false;});render();cbs[0].focus();});
    bar.hidden=false;render();
  });
})();
