(function(){
  function isInternalNav(a){
    const h=a.getAttribute('href')||'';
    return !h || a.hasAttribute('data-external') || h.startsWith('#') || h.startsWith('javascript:') || h.startsWith('mailto:') || h.startsWith('tel:') || /^(https?:)?\/\/nashhal\.github\.io/i.test(h) || /article\.html/i.test(h);
  }
  function isNewsLink(a){
    if(!a||isInternalNav(a)) return false;
    const h=a.getAttribute('href')||'';
    return /sabanew\.net|adenalghad\.net|almasdaronline\.com|south24\.net|telegram\.me|t\.me|twitter\.com|x\.com|facebook\.com|instagram\.com|youtube\.com/i.test(h) || a.closest('.card,.hero-main,.rank')!==null;
  }
  function updateHero(){
    const hero=document.querySelector('.hero-main');
    if(!hero) return;
    const link=hero.querySelector('h1 a');
    if(!link) return;
    const href=link.getAttribute('href')||'';
    if(/france24\.com\/ar\/رياضة|20260809-.*كأس.*أفريقيا.*للسيدات/i.test(href) || /منتخبا الجزائر والمغرب/i.test(link.textContent||'')){
      link.removeAttribute('target');
      link.removeAttribute('rel');
      link.setAttribute('href','#south');
      link.textContent='أحدث أخبار الجنوب وتطوراته المحلية';
      const summary=hero.querySelector('.summary');
      if(summary) summary.textContent='تابع أحدث الأخبار والتطورات في عدن وحضرموت وشبوة وأبين ولحج والضالع، مع ذكر المصدر وتاريخ النشر.';
      const meta=hero.querySelector('.meta');
      if(meta) meta.innerHTML='<span>آخر تحديث: 10 أغسطس 2026</span><span>مصادر يمنية ودولية</span>';
    }
  }
  function route(){
    updateHero();
    document.querySelectorAll('a').forEach(function(a){
      if(!isNewsLink(a)) return;
      const href=a.getAttribute('href')||'';
      if(!href || /article\.html/i.test(href)) return;
      a.setAttribute('href','article.html?id='+encodeURIComponent(href));
      a.removeAttribute('target');
      a.removeAttribute('rel');
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',route); else route();
  new MutationObserver(route).observe(document.documentElement,{childList:true,subtree:true});
})();
