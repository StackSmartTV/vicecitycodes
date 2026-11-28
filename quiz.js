/* vch-quiz v1: GTA 6 quick quiz (no storage, no network) */
(function(){
  document.querySelectorAll('.vqz').forEach(function(box){
    var qs=box.querySelectorAll('.vqz-q'),out=box.querySelector('.vqz-score'),bar=box.querySelector('.vqz-bar'),
        again=box.querySelector('.vqz-again'),fired=false;
    function render(){
      var a=0,c=0;qs.forEach(function(q){if(q.dataset.done){a++;if(q.dataset.done==='y')c++;}});
      out.textContent=a===qs.length?'You got '+c+' of '+qs.length+' right. '+(c===qs.length?'Vice City legend!':c>=4?'Nice work.':'Read the linked stories and try again.'):a+' of '+qs.length+' answered, '+c+' correct';
      box.classList.toggle('vqz-fin',a===qs.length);again.hidden=a===0;
      if(a===qs.length&&!fired){fired=true;try{if(window.gtag)gtag('event','quiz_complete',{score:c});}catch(e){}}
    }
    qs.forEach(function(q){
      var ok=q.getAttribute('data-ok'),det=q.querySelector('.vqz-ans'),res=q.querySelector('.vqz-res');
      det.classList.add('vqz-js');
      q.querySelectorAll('input[type=radio]').forEach(function(r){
        r.addEventListener('change',function(){
          if(q.dataset.done)return;
          var right=r.value===ok;q.dataset.done=right?'y':'n';
          q.querySelectorAll('input[type=radio]').forEach(function(x){x.disabled=true;
            var li=x.closest('li');if(x.value===ok)li.classList.add('vqz-right');else if(x===r)li.classList.add('vqz-wrong');});
          res.textContent=right?'Correct!':'Not quite.';res.className='vqz-res '+(right?'is-right':'is-wrong');
          det.open=true;render();
        });
      });
    });
    again.addEventListener('click',function(){
      fired=false;qs.forEach(function(q){delete q.dataset.done;q.querySelector('.vqz-ans').open=false;
        var res=q.querySelector('.vqz-res');res.textContent='';res.className='vqz-res';
        q.querySelectorAll('input[type=radio]').forEach(function(x){x.disabled=false;x.checked=false;x.closest('li').classList.remove('vqz-right','vqz-wrong');});});
      render();qs[0].querySelector('input').focus();
    });
    bar.hidden=false;render();
  });
})();
