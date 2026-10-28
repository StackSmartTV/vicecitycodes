/* vch-fitcheck v1 */
(function(){
  document.querySelectorAll('.fitcheck').forEach(function(box){
    var f=box.querySelector('form'),inp=box.querySelector('input'),out=box.querySelector('.fc-out'),need=+box.getAttribute('data-need')||210;
    if(!f||!inp||!out)return;
    f.addEventListener('submit',function(ev){
      ev.preventDefault();
      var v=parseFloat(String(inp.value).replace(',','.'));
      out.className='fc-out';
      if(isNaN(v)||v<0){out.textContent='Enter your free space in GB, for example 180.';out.classList.add('fc-warn');inp.focus();return;}
      var d=Math.round(v-need),res;
      if(d>=50){res='fit';out.textContent='Good to go: about '+d+' GB to spare after a '+need+' GB install. Keep some room for patches.';out.classList.add('fc-ok');}
      else if(d>=0){res='tight';out.textContent='It fits, but only just ('+d+' GB to spare). Free up a little more before pre-load on Nov 12 so updates have room.';out.classList.add('fc-tight');}
      else{res='short';out.textContent='Not yet: you need about '+(-d)+' GB more. Delete or move a game or two before pre-load opens on Nov 12.';out.classList.add('fc-warn');}
      try{if(window.gtag)gtag('event','fit_check',{result:res});}catch(e){}
    });
  });
})();
