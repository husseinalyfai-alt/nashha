(async()=>{
  const box=document.getElementById('cards');
  if(!box)return;
  const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const regionImage={
    'عدن':'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=900&q=80',
    'حضرموت':'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=900&q=80',
    'شبوة':'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=900&q=80',
    'أبين':'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=900&q=80',
    'لحج':'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=900&q=80',
    'الضالع':'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=900&q=80',
    'سقطرى':'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=900&q=80',
    'المهرة':'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=900&q=80'
  };
  const fallback='logo.jpg';
  const southToday=[];
  function regionOf(x){
    const direct=x.region||x.category||'';
    if(regionImage[direct])return direct;
    const text=((x.title||'')+' '+(x.summary||'')+' '+(x.description||'')).toLowerCase();
    for(const r of Object.keys(regionImage)) if(text.includes(r.toLowerCase())) return r;
    return 'الجنوب';
  }
  try{
    const r=await fetch('data/news.json?v='+Date.now(),{cache:'no-store'});
    if(!r.ok)throw new Error('news unavailable');
    const data=await r.json();
    const items=Array.isArray(data)?data:(data.news||[]);
    const south=items.filter(x=>/عدن|حضرموت|شبوة|أبين|لحج|الضالع|المهرة|سقطرى|الجنوب|الجنوبي/i.test((x.title||'')+' '+(x.summary||'')+' '+(x.region||''))).slice(0,12);
    const all=south.map(x=>{
      const region=regionOf(x);
      return {title:x.title,source:x.source||x.source_name||'المصدر',date:x.published||x.date||x.published_at||'',summary:x.summary||x.description||'',href:'article.html?id='+encodeURIComponent(x.id||x.url||x.link||''),image:x.image||x.image_url||x.thumbnail||regionImage[region]||fallback,region};
    });
    box.innerHTML=all.map(x=>{
      const href=esc(x.href);
      return `<article class="card"><a class="card-image" href="${href}"><img src="${esc(x.image)}" alt="${esc(x.title)}" loading="lazy" onerror="this.src='${fallback}'"><span class="tag">${esc(x.region)}</span></a><div class="card-body"><div class="label">${esc(x.source)}</div><h3><a href="${href}">${esc(x.title)}</a></h3><p>${esc(x.summary)}</p><div class="card-meta">${esc(x.region)} · المصدر: ${esc(x.source)} · ${esc(x.date)}</div></div></article>`;
    }).join('');

    // Make regional navigation filter the news cards.
    document.querySelectorAll('.nav a, .section-grid a').forEach(a=>{
      a.addEventListener('click',e=>{
        const label=(a.textContent||'').trim();
        if(!regionImage[label])return;
        e.preventDefault();
        const filtered=all.filter(x=>x.region===label);
        box.innerHTML=(filtered.length?filtered:all).map(x=>{
          const href=esc(x.href); return `<article class="card"><a class="card-image" href="${href}"><img src="${esc(x.image)}" alt="${esc(x.title)}" loading="lazy" onerror="this.src='${fallback}'"><span class="tag">${esc(x.region)}</span></a><div class="card-body"><div class="label">${esc(x.source)}</div><h3><a href="${href}">${esc(x.title)}</a></h3><p>${esc(x.summary)}</p><div class="card-meta">${esc(x.region)} · ${esc(x.date)}</div></div></article>`;
        }).join('');
        document.getElementById('news')?.scrollIntoView({behavior:'smooth'});
      });
    });
  }catch(e){console.warn('News feed unavailable',e)}
})();
