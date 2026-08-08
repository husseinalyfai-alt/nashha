(function(){
  function isInternalNav(a){
    const h=a.getAttribute('href')||'';
    return !h || h.startsWith('#') || h.startsWith('javascript:') || h.startsWith('mailto:') || h.startsWith('tel:') || /^(https?:)?\/\/nashhal\.github\.io/i.test(h) || /article\.html/i.test(h);
  }
  function isNewsLink(a){
    if(!a||isInternalNav(a)) return false;
    const h=a.getAttribute('href')||'';
    return /sabanew\.net|adenalghad\.net|almasdaronline\.com|south24\.net|telegram\.me|t\.me|twitter\.com|x\.com|facebook\.com|instagram\.com|youtube\.com/i.test(h) || a.closest('.card,.hero-main,.rank')!==null;
  }
  function route(){
    document.querySelectorAll('a').forEach(function(a){
      if(!isNewsLink(a)) return;
      const href=a.getAttribute('href')||'';
      if(!href || /article\.html/i.test(href)) return;
      const title=((a.dataset.title||a.textContent||'').replace(/\s+/g,' ').trim()).slice(0,300);
      a.setAttribute('href','article.html?source='+encodeURIComponent(href)+'&title='+encodeURIComponent(title));
      a.removeAttribute('target');
      a.removeAttribute('rel');
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',route); else route();
  new MutationObserver(route).observe(document.documentElement,{childList:true,subtree:true});
})();
