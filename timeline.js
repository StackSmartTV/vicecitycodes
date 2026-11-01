/* vch-timeline v1 */
(function(){
  function ymd(d){return d.getFullYear()*10000+(d.getMonth()+1)*100+d.getDate();}
  var now=new Date(),today=ymd(now);
  document.querySelectorAll('.vtl-item[data-date]').forEach(function(li){
    var p=li.getAttribute('data-date').split('-'),d=new Date(+p[0],+p[1]-1,+p[2]),k=ymd(d),chip=li.querySelector('.vtl-chip');
    if(!chip)return;
    var days=Math.round((d-new Date(now.getFullYear(),now.getMonth(),now.getDate()))/864e5);
    if(k<today){chip.textContent='Done';li.classList.add('vtl-past');}
    else if(k===today){chip.textContent='Today';li.classList.add('vtl-today');}
    else{chip.textContent=days===1?'Tomorrow':'In '+days+' days';}
  });
  document.querySelectorAll('.vtl').forEach(function(ol){var n=ol.querySelector('.vtl-item:not(.vtl-past)');if(n)n.classList.add('vtl-next');});
  document.querySelectorAll('.vtl-cal').forEach(function(a){a.addEventListener('click',function(){try{if(window.gtag)gtag('event','add_to_calendar',{event_id:a.getAttribute('data-ev')});}catch(e){}});});
})();
