(function(){
  function isNewsLink(a){
    if(!a||!a.href)return false;
    const u=a.href;
    return /data\/news\.json|news\.json|article/i.test(u) || a.matches('[data-news-id],[data-id]');
  }
  function route(){
    document.querySelectorAll('a').forEach(function(a){
      if(!isNewsLink(a)) return;
      let id=a.dataset.newsId||a.dataset.id;
      if(!id){
        try{const u=new URL(a.href,location.href); id=u.searchParams.get('id');}catch(e){}
      }
      if(id && !/article\.html/i.test(a.href)){
        a.href='article.html?id='+encodeURIComponent(id);
        a.removeAttribute('target');
      }
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',route); else route();
  new MutationObserver(route).observe(document.documentElement,{childList:true,subtree:true});
})();
