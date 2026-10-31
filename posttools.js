/* vch-posttools v1: reading progress bar + active section in 'In this article' */
(function(){
  var art=document.querySelector('.post-body'),bar=document.querySelector('.read-progress span');
  if(!art||!bar)return;
  var links=[].slice.call(document.querySelectorAll('.post-toc a[href^="#sec-"]')),heads=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));});
  var ticking=false;
  function upd(){
    ticking=false;
    var r=art.getBoundingClientRect(),h=r.height-window.innerHeight*0.6,p=h>0?Math.min(1,Math.max(0,-r.top/h)):1;
    bar.style.transform='scaleX('+p.toFixed(3)+')';
    var cur=-1;heads.forEach(function(el,i){if(el&&el.getBoundingClientRect().top<window.innerHeight*0.35)cur=i;});
    links.forEach(function(a,i){if(i===cur)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});
  }
  function on(){if(!ticking){ticking=true;requestAnimationFrame(upd);}}
  window.addEventListener('scroll',on,{passive:true});window.addEventListener('resize',on);upd();
  if(window.matchMedia&&matchMedia('(max-width:699px)').matches){var d=document.querySelector('.post-toc');if(d)d.removeAttribute('open');}
})();
