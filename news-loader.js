(async()=>{
  const box=document.getElementById('cards');
  if(!box)return;
  const esc=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const southToday=[
    {id:'syt-2026-08-05-1',title:'مهرجان خريف حجر يحقق تداولاً تجارياً بـ235 مليون ريال',date:'5 أغسطس 2026',link:'https://aljanoubalyoum.tv/',summary:'حقق مهرجان خريف حجر السنوي في موسمه الثالث تداولاً تجارياً تجاوز 235 مليون ريال، واستقطب نحو 40 ألفاً و840 زائراً، وفق قناة الجنوب اليوم.'},
    {id:'syt-2026-08-05-2',title:'وزير الأشغال ومحافظ عدن يدشنان مشروع صيانة جسر البريقة وتأهيل كورنيش كود النمر',date:'5 أغسطس 2026',link:'https://aljanoubalyoum.tv/',summary:'دُشن مشروع صيانة وترميم جسر البريقة القديم وتأهيل كورنيش كود النمر في العاصمة عدن، بتمويل من صندوق صيانة الطرق والجسور.'},
    {id:'syt-2026-08-05-3',title:'وزارة النقل تدين استهداف سفينة شحن هندية في البحر الأحمر',date:'5 أغسطس 2026',link:'https://aljanoubalyoum.tv/',summary:'وزارة النقل أدانت استهداف سفينة شحن هندية في البحر الأحمر، مؤكدة أن استهداف السفن التجارية يهدد أمن الملاحة البحرية.'},
    {id:'syt-2026-08-05-4',title:'القوات المسلحة الجنوبية تُسقط طائرة مسيّرة حوثية شمالي لحج',date:'5 أغسطس 2026',link:'https://aljanoubalyoum.tv/',summary:'أفادت قناة الجنوب اليوم بأن الدفاعات الجوية للقوات المسلحة الجنوبية أسقطت طائرة مسيّرة شمالي محافظة لحج.'},
    {id:'syt-2026-08-05-5',title:'مجلس القيادة الرئاسي يشدد على تعزيز الإصلاحات الاقتصادية',date:'5 أغسطس 2026',link:'https://aljanoubalyoum.tv/',summary:'ناقش مجلس القيادة الرئاسي التطورات الأمنية والاقتصادية والإصلاحات المالية ومستوى الجاهزية العسكرية والأمنية.'},
    {id:'syt-2026-08-03-1',title:'تحذيرات من أمطار رعدية واضطراب شديد للبحر في عدة محافظات',date:'3 أغسطس 2026',link:'https://aljanoubalyoum.tv/',summary:'توقع مركز التنبؤات الجوية أمطاراً رعدية متفرقة وأجواء شديدة الحرارة في عدد من المحافظات، مع تحذيرات من اضطراب البحر.'}
  ];
  try{
    const r=await fetch('data/news.json?v='+Date.now(),{cache:'no-store'});
    if(!r.ok)throw new Error('news unavailable');
    const data=await r.json();
    const items=Array.isArray(data)?data:(data.news||[]);
    const south=items.filter(x=>/عدن|حضرموت|شبوة|أبين|لحج|الضالع|المهرة|سقطرى|الجنوب|الجنوبي/i.test((x.title||'')+' '+(x.summary||''))).slice(0,6);
    const local=south.map(x=>({title:x.title,source:x.source||x.source_name||'المصدر',date:x.published||x.date||x.published_at||'',summary:x.summary||x.description||'',href:'article.html?id='+encodeURIComponent(x.id||x.url||x.link||'')}));
    const channel=southToday.map(x=>({title:x.title,source:'قناة الجنوب اليوم',date:x.date,summary:x.summary,href:x.link,external:true}));
    const all=[...channel,...local].slice(0,12);
    box.innerHTML=all.map(x=>{
      const href=esc(x.href);
      const attrs=x.external?' data-external="true" target="_blank" rel="noopener noreferrer"':'';
      return `<article class="card"><a class="card-image" href="${href}"${attrs}><img src="logo.jpg" alt="${esc(x.title)}" loading="lazy"></a><div class="card-body"><div class="label">${esc(x.source)}</div><h3><a href="${href}"${attrs}>${esc(x.title)}</a></h3><p>${esc(x.summary)}</p><div class="card-meta">المصدر: ${esc(x.source)} · ${esc(x.date)}</div></div></article>`;
    }).join('');
  }catch(e){console.warn('News feed unavailable',e)}
})();
