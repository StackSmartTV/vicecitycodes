/* vch-shorts v1: click-to-load YouTube Shorts from the current channel only.
   Channel URL and label live in sitegen/youtube.py. Nothing loads before a click. */
(function(){
  document.addEventListener('click',function(ev){
    var a=ev.target.closest&&ev.target.closest('a.vsh-play');
    if(!a||ev.metaKey||ev.ctrlKey||ev.shiftKey||ev.altKey||ev.button)return;
    var id=a.getAttribute('data-id');if(!/^[\w-]{11}$/.test(id))return;
    ev.preventDefault();
    var f=document.createElement('iframe');
    f.src='https://www.youtube-nocookie.com/embed/'+id+'?autoplay=1&playsinline=1&rel=0';
    f.title=a.getAttribute('data-title')||'YouTube Short';
    f.allow='autoplay; encrypted-media; picture-in-picture; web-share';
    f.setAttribute('allowfullscreen','');f.referrerPolicy='strict-origin-when-cross-origin';
    var box=a.parentNode;box.replaceChild(f,a);box.classList.add('vsh-on');f.focus();
    try{if(window.gtag)gtag('event','short_play',{video_id:id});}catch(e){}
  });
})();
