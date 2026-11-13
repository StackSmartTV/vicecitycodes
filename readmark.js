/* vch-readmark v1: New / Read chips on story cards (device-only storage) */
(function(){
  var ls,ss;try{ls=window.localStorage;ss=window.sessionStorage;ls.setItem('vrm-t','1');ls.removeItem('vrm-t');}catch(e){return;}
  var now=Date.now(),DAY=864e5;
  var base=ss.getItem('vch-lv0');
  if(base===null){base=ls.getItem('vch-lv')||'';ss.setItem('vch-lv0',base);}
  ls.setItem('vch-lv',String(now));
  var since=base?+base:now-3*DAY;
  var read=[];try{read=JSON.parse(ls.getItem('vch-read')||'[]')||[];}catch(e){read=[];}
  function slugOf(h){var m=/([a-z0-9-]+)\.html(?:[#?].*)?$/.exec(h||'');return m?m[1]:'';}
  // mark the current post as read after ~40% of the body
  var body=document.querySelector('.post-body'),canon=document.querySelector('link[rel="canonical"]');
  var me=canon?slugOf(canon.getAttribute('href')):'';
  if(body&&me&&read.indexOf(me)<0){
    var tick=false;
    var chk=function(){tick=false;var r=body.getBoundingClientRect(),p=(innerHeight-r.top)/Math.max(r.height,1);
      if(p>0.4){if(read.indexOf(me)<0){read.unshift(me);read=read.slice(0,60);try{ls.setItem('vch-read',JSON.stringify(read));}catch(e){}}
        removeEventListener('scroll',on);}};
    var on=function(){if(!tick){tick=true;requestAnimationFrame(chk);}};
    addEventListener('scroll',on,{passive:true});chk();
  }
  var cards=document.querySelectorAll('a.rn-card[data-vrm-date]'),fresh=0;
  cards.forEach(function(a){
    var s=slugOf(a.getAttribute('href')),d=Date.parse(a.getAttribute('data-vrm-date')+'T12:00:00-05:00'),k=a.querySelector('.rn-kicker');
    if(!k||a.querySelector('.vrm-chip'))return;
    var c=document.createElement('span');c.className='vrm-chip';
    if(read.indexOf(s)>=0){c.className+=' vrm-read';c.textContent='\u2713 Read';a.classList.add('vrm-is-read');}
    else if(d>since){c.className+=' vrm-new';c.textContent='New';fresh++;}
    else return;
    k.appendChild(document.createTextNode(' '));k.appendChild(c);
  });
  var sum=document.querySelector('.vrm-sum');
  if(sum&&fresh&&base){sum.textContent=fresh+(fresh===1?' new story':' new stories')+' since your last visit';sum.hidden=false;}
})();
