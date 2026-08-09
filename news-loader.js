(async()=>{
  const box=document.getElementById('cards');
  if(!box)return;
  const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  try{
    const r=await fetch('data/news.json?v='+Date.now(),{cache:'no-store'});
    if(!r.ok)throw new Error('news unavailable');
    const data=await r.json();
    const items=Array.isArray(data)?data:(data.news||[]);
    const south=items.filter(x=>/عدن|حضرموت|شبوة|أبين|لحج|الضالع|المهرة|سقطرى|الجنوب|الجنوبي/i.test((x.title||'')+' '+(x.summary||''))).slice(0,12);
    box.innerHTML=south.map(x=>{
      const id=encodeURIComponent(x.id||x.url||x.link||'');
      const image=x.image||x.image_url||x.thumbnail||'logo.jpg';
      const date=x.published||x.date||x.published_at||'';
      return `<article class="card"><a class="card-image" href="article.html?id=${id}"><img src="${esc(image)}" alt="${esc(x.title)}" loading="lazy"></a><div class="card-body"><div class="label">${esc(x.source||x.source_name||'المصدر')}</div><h3><a href="article.html?id=${id}">${esc(x.title)}</a></h3><p>${esc(x.summary||x.description||'')}</p><div class="card-meta">المصدر: ${esc(x.source||x.source_name||'')} · ${esc(date)}</div></div></article>`;
    }).join('');
  }catch(e){console.warn('News feed unavailable',e)}
})();
