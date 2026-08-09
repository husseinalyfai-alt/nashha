(async function(){
  const archive=document.querySelector('#archive');
  if(!archive) return;
  try{
    const r=await fetch('data/heritage-images.json?v='+Date.now());
    const images=await r.json();
    if(!Array.isArray(images)||!images.length) return;
    const old=archive.querySelector('.archive-gallery');
    if(old) old.remove();
    const box=document.createElement('div');
    box.className='archive-gallery';
    box.innerHTML='<div class="section-title"><h2>صور من الأرشيف</h2><small style="color:var(--muted)">مصادر مفتوحة ومرخّصة</small></div><div class="archive-grid"></div>';
    archive.appendChild(box);
    const grid=box.querySelector('.archive-grid');
    images.slice(0,24).forEach(x=>{
      const card=document.createElement('article'); card.className='archive-card';
      card.innerHTML=`<a href="${x.source_url}" target="_blank" rel="noopener"><img src="${x.image_url}" loading="lazy" alt="${x.title||'صورة من الأرشيف'}"><div><b>${x.title||'صورة أرشيفية'}</b><small>${x.license||''}</small><small>${x.source||'Wikimedia Commons'}</small></div></a>`;
      grid.appendChild(card);
    });
  }catch(e){console.warn('Archive gallery unavailable',e)}
})();