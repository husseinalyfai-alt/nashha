<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>نهشل | Fresh News</title>

<style>

*{
  box-sizing:border-box;
}

body{
  margin:0;
  background:#f7efd8;
  color:#1c2b22;
  font-family:Tahoma,Arial,sans-serif;
}

/* =========================
   عاجل
========================= */

.ticker{
  height:50px;
  width:100%;
  display:flex;
  align-items:center;
  overflow:hidden;
  background:#1c2b22;
  color:#f7efd8;
}

.ticker-title{
  height:100%;
  padding:0 20px;
  display:flex;
  align-items:center;
  gap:9px;
  background:#2f7a52;
  font-weight:bold;
  white-space:nowrap;
}

.dot{
  width:9px;
  height:9px;
  border-radius:50%;
  background:#fff;
  animation:pulse 1s infinite;
}

@keyframes pulse{

  50%{
    opacity:.3;
  }

}

.ticker-window{
  flex:1;
  overflow:hidden;
}

.ticker-track{
  display:flex;
  gap:60px;
  width:max-content;
  white-space:nowrap;
  animation:newsMove 40s linear infinite;
}

.ticker-item{
  color:#f7efd8;
  font-size:14px;
}

.ticker-item strong{
  color:#a9884f;
  margin-left:7px;
}

@keyframes newsMove{

  from{
    transform:translateX(0);
  }

  to{
    transform:translateX(100vw);
  }

}


/* =========================
   المحتوى
========================= */

.container{
  width:min(1200px,92%);
  margin:40px auto;
}

.header{
  margin-bottom:30px;
}

.header h1{
  margin:0;
  font-size:30px;
}

.header p{
  color:#687268;
}


/* =========================
   المصادر
========================= */

.sources{
  display:grid;
  grid-template-columns:
  repeat(auto-fit,minmax(230px,1fr));

  gap:15px;
  margin-bottom:40px;
}

.source{
  background:#fff;
  border:1px solid #ddd;
  padding:18px;
  border-radius:10px;
}

.source h3{
  margin:0 0 8px;
  font-size:16px;
}

.source span{
  font-size:12px;
  color:#777;
}

.source a{
  display:block;
  margin-top:12px;
  color:#2f7a52;
  font-weight:bold;
  text-decoration:none;
}


/* =========================
   الأخبار
========================= */

.news-title{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:18px;
}

.news-title h2{
  margin:0;
}

.status{
  font-size:12px;
  color:#777;
}

.news-grid{
  display:grid;
  grid-template-columns:
  repeat(auto-fit,minmax(280px,1fr));

  gap:20px;
}

.news-card{
  background:#fff;
  border:1px solid #ddd;
  border-radius:10px;
  padding:20px;
  transition:.2s;
}

.news-card:hover{
  transform:translateY(-3px);
  border-color:#2f7a52;
}

.news-source{
  display:inline-block;
  padding:5px 9px;
  background:#1c2b22;
  color:#f7efd8;
  font-size:11px;
  border-radius:4px;
  margin-bottom:12px;
}

.news-card h3{
  margin:0 0 10px;
  font-size:17px;
  line-height:1.6;
}

.news-card p{
  color:#687268;
  font-size:13px;
  line-height:1.8;
}

.news-meta{
  display:flex;
  justify-content:space-between;
  align-items:center;
  border-top:1px solid #eee;
  padding-top:12px;
  margin-top:15px;
  font-size:11px;
  color:#777;
}

.news-meta a{
  color:#2f7a52;
  text-decoration:none;
  font-weight:bold;
}


/* =========================
   تقارير أممية
========================= */

.reports{
  margin-top:50px;
}

.report{
  background:#efe2bd;
  border:1px solid #d8cda9;
  padding:20px;
  border-radius:10px;
  margin-bottom:15px;
}

.report strong{
  color:#2f7a52;
}


/* =========================
   الجوال
========================= */

@media(max-width:600px){

  .ticker-title{
    padding:0 12px;
  }

  .ticker-item{
    font-size:13px;
  }

  .header h1{
    font-size:24px;
  }

}

</style>

</head>


<body>


<!-- =========================
     شريط العاجل
========================= -->

<div class="ticker">

  <div class="ticker-title">

    <span class="dot"></span>

    عاجل اليمن

  </div>


  <div class="ticker-window">

    <div
      class="ticker-track"
      id="tickerTrack">

      <span class="ticker-item">
        جاري تحميل آخر أخبار اليمن...
      </span>

    </div>

  </div>

</div>



<div class="container">


<!-- =========================
     العنوان
========================= -->

<div class="header">

  <h1>
    Fresh News
  </h1>

  <p>
    آخر أخبار اليمن من المصادر الرسمية والصحافة الدولية والمحلية
  </p>

</div>



<!-- =========================
     المصادر
========================= -->

<h2>
  المصادر
</h2>


<div class="sources">


  <!-- العمالقة -->

  <div class="source">

    <h3>
      المركز الإعلامي لألوية العمالقة الجنوبية
    </h3>

    <span>
      مصدر محلي رسمي
    </span>

    <a
      href="https://alamalika.net/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- الخارجية الأمريكية -->

  <div class="source">

    <h3>
      U.S. State Department
    </h3>

    <span>
      مصدر حكومي أمريكي
    </span>

    <a
      href="https://www.state.gov/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- الخزانة الأمريكية -->

  <div class="source">

    <h3>
      U.S. Treasury
    </h3>

    <span>
      العقوبات والإجراءات المالية
    </span>

    <a
      href="https://home.treasury.gov/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- Pentagon -->

  <div class="source">

    <h3>
      U.S. Department of Defense
    </h3>

    <span>
      مصدر حكومي عسكري أمريكي
    </span>

    <a
      href="https://www.defense.gov/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- بريطانيا -->

  <div class="source">

    <h3>
      UK Government
    </h3>

    <span>
      الحكومة البريطانية
    </span>

    <a
      href="https://www.gov.uk/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- الأمم المتحدة -->

  <div class="source">

    <h3>
      United Nations Yemen
    </h3>

    <span>
      مصدر أممي
    </span>

    <a
      href="https://yemen.un.org/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- Reuters -->

  <div class="source">

    <h3>
      Reuters
    </h3>

    <span>
      وكالة أنباء دولية
    </span>

    <a
      href="https://www.reuters.com/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- AP -->

  <div class="source">

    <h3>
      Associated Press
    </h3>

    <span>
      وكالة أنباء دولية
    </span>

    <a
      href="https://apnews.com/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- BBC -->

  <div class="source">

    <h3>
      BBC
    </h3>

    <span>
      مصدر إعلامي دولي
    </span>

    <a
      href="https://www.bbc.com/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- Guardian -->

  <div class="source">

    <h3>
      The Guardian
    </h3>

    <span>
      صحيفة بريطانية
    </span>

    <a
      href="https://www.theguardian.com/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- المصدر أونلاين -->

  <div class="source">

    <h3>
      المصدر أونلاين
    </h3>

    <span>
      مصدر يمني
    </span>

    <a
      href="https://almasdaronline.com/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- مأرب برس -->

  <div class="source">

    <h3>
      مأرب برس
    </h3>

    <span>
      مصدر يمني
    </span>

    <a
      href="https://marebpress.net/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>



  <!-- عدن الغد -->

  <div class="source">

    <h3>
      عدن الغد
    </h3>

    <span>
      مصدر يمني
    </span>

    <a
      href="https://adengad.net/"
      target="_blank">

      زيارة الموقع ←

    </a>

  </div>


</div>



<!-- =========================
     الأخبار
========================= -->

<div class="news-title">

  <h2>
    آخر الأخبار
  </h2>

  <span
    class="status"
    id="status">

    جاري التحديث...

  </span>

</div>


<div
  class="news-grid"
  id="newsGrid">

</div>



<!-- =========================
     التقارير الأممية
========================= -->

<div class="reports">

  <h2>
    التقارير الأممية الخاصة باليمن
  </h2>


  <div class="report">

    <strong>
      الأمم المتحدة
    </strong>

    <p>
      التقارير والبيانات الرسمية المتعلقة بالوضع السياسي والإنساني في اليمن.
    </p>

    <a
      href="https://yemen.un.org/"
      target="_blank">

      المصدر الرسمي ←

    </a>

  </div>


  <div class="report">

    <strong>
      مجلس الأمن
    </strong>

    <p>
      القرارات والإحاطات والتقارير المتعلقة باليمن.
    </p>

    <a
      href="https://www.un.org/securitycouncil/"
      target="_blank">

      المصدر الرسمي ←

    </a>

  </div>


  <div class="report">

    <strong>
      OCHA
    </strong>

    <p>
      التقارير الإنسانية والاحتياجات والاستجابة في اليمن.
    </p>

    <a
      href="https://www.unocha.org/"
      target="_blank">

      المصدر الرسمي ←

    </a>

  </div>

</div>


</div>



<script>

/* =================================
   مصادر Fresh News
================================= */

const SOURCES = [

  {
    name:"المركز الإعلامي لألوية العمالقة الجنوبية",
    type:"محلي",
    url:"https://alamalika.net/"
  },

  {
    name:"U.S. State Department",
    type:"حكومي أمريكي",
    url:"https://www.state.gov/"
  },

  {
    name:"U.S. Treasury",
    type:"حكومي أمريكي",
    url:"https://home.treasury.gov/"
  },

  {
    name:"U.S. Department of Defense",
    type:"حكومي أمريكي",
    url:"https://www.defense.gov/"
  },

  {
    name:"UK Government",
    type:"حكومي",
    url:"https://www.gov.uk/"
  },

  {
    name:"United Nations Yemen",
    type:"أممي",
    url:"https://yemen.un.org/"
  },

  {
    name:"Reuters",
    type:"دولي",
    url:"https://www.reuters.com/"
  },

  {
    name:"Associated Press",
    type:"دولي",
    url:"https://apnews.com/"
  },

  {
    name:"BBC",
    type:"دولي",
    url:"https://www.bbc.com/"
  },

  {
    name:"The Guardian",
    type:"دولي",
    url:"https://www.theguardian.com/"
  },

  {
    name:"المصدر أونلاين",
    type:"يمني",
    url:"https://almasdaronline.com/"
  },

  {
    name:"مأرب برس",
    type:"يمني",
    url:"https://marebpress.net/"
  },

  {
    name:"عدن الغد",
    type:"يمني",
    url:"https://adengad.net/"
  }

];


/* =================================
   أخبار تجريبية
================================= */

const demoNews = [

  {
    source:"المركز الإعلامي لألوية العمالقة الجنوبية",
    title:"آخر التطورات الميدانية في اليمن",
    description:"متابعة لأحدث المستجدات والتطورات في الساحة اليمنية.",
    date:"اليوم",
    link:"https://alamalika.net/"
  },

  {
    source:"U.S. State Department",
    title:"تطورات ومواقف أمريكية بشأن اليمن",
    description:"أحدث البيانات والمواقف الرسمية المتعلقة باليمن.",
    date:"اليوم",
    link:"https://www.state.gov/"
  },

  {
    source:"United Nations Yemen",
    title:"آخر التقارير الأممية المتعلقة باليمن",
    description:"بيانات وتقارير الأمم المتحدة حول التطورات في اليمن.",
    date:"اليوم",
    link:"https://yemen.un.org/"
  },

  {
    source:"Reuters",
    title:"آخر التطورات في اليمن",
    description:"تغطية دولية لأبرز الأحداث اليمنية.",
    date:"اليوم",
    link:"https://www.reuters.com/"
  }

];


/* =================================
   عرض الأخبار
================================= */

function renderNews(news){

  const grid =
    document.getElementById("newsGrid");

  const ticker =
    document.getElementById("tickerTrack");


  grid.innerHTML = "";

  ticker.innerHTML = "";


  news.forEach(item => {


    /* البطاقة */

    const card =
      document.createElement("article");

    card.className =
      "news-card";


    card.innerHTML = `

      <span class="news-source">
        ${item.source}
      </span>

      <h3>
        ${item.title}
      </h3>

      <p>
        ${item.description || ""}
      </p>

      <div class="news-meta">

        <span>
          ${item.date || "اليوم"}
        </span>

        <a
          href="${item.link}"
          target="_blank"
          rel="noopener noreferrer">

          المصدر الأصلي ←

        </a>

      </div>

    `;


    grid.appendChild(card);


    /* العاجل */

    const tickerItem =
      document.createElement("span");

    tickerItem.className =
      "ticker-item";


    tickerItem.innerHTML = `

      <strong>
        ${item.source}
      </strong>

      ${item.title}

    `;


    ticker.appendChild(tickerItem);

  });

}


/* =================================
   تشغيل الموقع
================================= */

function loadNews(){

  document.getElementById("status")
    .textContent =
    "آخر تحديث: الآن";


  renderNews(demoNews);

}


/* =================================
   تشغيل أول مرة
================================= */

loadNews();


/* =================================
   تحديث كل 10 دقائق
================================= */

setInterval(
  loadNews,
  10 * 60 * 1000
);

</script>


</body>
</html>
