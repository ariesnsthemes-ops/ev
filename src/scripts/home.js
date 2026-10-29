
(function(){var d=[...document.querySelectorAll('.faq details')];d.forEach(function(x,i){x.addEventListener('toggle',function(){if(x.open)d.forEach(function(o){if(o!==x)o.open=false})})})})();
(function(){
  const $=id=>document.getElementById(id);
  const reduce=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ad annotations are off for visitors (owner preview removed)
  document.body.classList.remove('show-marks');

  // mobile menu
  const mb=$('menu-btn'), nl=$('nav-links');
  mb.addEventListener('click',()=>{const o=nl.classList.toggle('open');mb.setAttribute('aria-expanded',o)});
  nl.addEventListener('click',e=>{if(e.target.tagName==='A'){nl.classList.remove('open');mb.setAttribute('aria-expanded','false')}});

  // hero carousel (AD-01 rotation positions)
  const slides=[
    {free:true,b:'SLOBODNO',m:'Pozicija 1',bg:'../img/evomobil-bg-auto.webp'},
    {free:true,b:'SLOBODNO',m:'Pozicija 2',bg:'../img/evomobil-bg-punjac.webp'},
    {free:true,b:'SLOBODNO',m:'Pozicija 3',bg:'../img/evomobil-bg-ekran.webp'},
    {free:true,b:'SLOBODNO',m:'Pozicija 4',bg:'../img/evomobil-bg-svetlo.webp'},
    {free:true,b:'SLOBODNO',m:'Pozicija 5',bg:'../img/evomobil-bg-kabl.webp'}
  ];
  slides.forEach(s=>{if(s.img){const im=new Image();im.src=s.img}});
  const vb={sedan:'0 0 320 112',hatch:'0 0 320 112',suv:'0 0 320 120'};
  const stage=$('stage'), heroAd=$('hero-media'), tabs=$('hero-tabs');
  let i=0, visible=false, hover=false, focus=false, curV='1';
  const side=$('side');
  function tileHTML(k){
    const s=slides[k];
    if(s.free)return '<div class="tile tile-free ph-bg" data-k="'+k+'"'+(s.bg?' style="--ph:url('+s.bg+')"':'')+'><b>POZICIJA '+(k+1)+'</b><strong>Slobodna pozicija</strong></div>';
    return '<a class="tile" href="'+s.href+'" data-k="'+k+'"><img src="'+s.img+'" alt="'+s.alt+'"></a>';
  }
  function renderSide(){
    const n=slides.length;
    side.innerHTML=curV==='4'?tileHTML((i+1)%n)+tileHTML((i+2)%n):curV==='6'?tileHTML(1):'';
  }
  side.addEventListener('click',e=>{const t=e.target.closest('.tile');if(t&&curV==='4'&&!t.classList.contains('tile-free')){e.preventDefault();go(+t.dataset.k)}});

  // Analytics hook: listen for "evc:ad" on document to count views and clicks per rented position.
  function track(type){const s=slides[i];document.dispatchEvent(new CustomEvent('evc:ad',{detail:{type,slot:'AD-01',position:i+1,advertiser:s.b,model:s.m}}))}

  slides.forEach((s,k)=>{
    const b=document.createElement('button');b.type='button';b.className='sp'+(s.free?' sp-free':'');b.setAttribute('role','tab');
    b.setAttribute('aria-selected',k===0);b.setAttribute('aria-label','Pozicija '+(k+1)+': '+s.b+' '+s.m);
    b.innerHTML='<b>'+s.b+'</b><span>'+s.m+'</span><i></i>';
    b.onclick=()=>go(k);
    tabs.appendChild(b);
  });
  function render(){
    const s=slides[i], free=!!s.free;
    $('h-free').hidden=!free; $('h-link').hidden=free;
    if(free)$('h-free').style.setProperty('--ph',s.bg?'url('+s.bg+')':'none'); $('h-brand').parentNode.hidden=!free;
    if(!free){$('h-img').src=s.img;$('h-img').alt=s.alt;$('h-link').href=s.href}
    $('h-brand').textContent=free?'SLOBODNA POZICIJA':s.b+' '+s.m.toUpperCase();
    [...tabs.children].forEach((t,k)=>t.setAttribute('aria-selected',k===i));
    const t=tabs.children[i];if(tabs.scrollWidth>tabs.clientWidth)tabs.scrollTo({left:t.offsetLeft-tabs.offsetLeft,behavior:reduce()?'auto':'smooth'});
    renderSide();
    if(visible&&!free)track('view');
  }
  // rotation timer: 6 s per position, paused on hover, focus, off-screen or hidden tab; off for options 3 and 6
  let tid=null, left=6000, t0=0;
  function stopT(){if(tid){clearTimeout(tid);tid=null;left-=Date.now()-t0}}
  function startT(){if(tid||reduce()||curV==='3'||curV==='6')return;t0=Date.now();tid=setTimeout(()=>{tid=null;left=6000;go(i+1)},Math.max(left,300))}
  function go(k){
    if(tid){clearTimeout(tid);tid=null}left=6000;
    i=(k+slides.length)%slides.length;
    if(reduce()){render();syncPause();return}
    stage.classList.add('swap');setTimeout(()=>{render();stage.classList.remove('swap');syncPause()},280);
  }
  function syncPause(){const p=hover||focus||!visible||document.hidden;heroAd.classList.toggle('paused',p);if(p)stopT();else startT()}
  $('prev').onclick=()=>go(i-1);$('next').onclick=()=>go(i+1);
  heroAd.addEventListener('mouseenter',()=>{hover=true;syncPause()});heroAd.addEventListener('mouseleave',()=>{hover=false;syncPause()});
  heroAd.addEventListener('focusin',()=>{focus=true;syncPause()});heroAd.addEventListener('focusout',()=>{focus=false;syncPause()});
  document.addEventListener('visibilitychange',syncPause);
  if('IntersectionObserver' in window){
    new IntersectionObserver(([e])=>{const was=visible;visible=e.intersectionRatio>=.5;if(visible&&!was&&!slides[i].free)track('view');syncPause()},{threshold:[0,.5]}).observe(stage);
  }else{visible=true}
  syncPause();
  $('h-link').addEventListener('click',()=>track('click'));
  // swipe on touch screens
  let x0=null;
  stage.addEventListener('touchstart',e=>{x0=e.touches[0].clientX},{passive:true});
  stage.addEventListener('touchend',e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40)go(dx<0?i+1:i-1);x0=null});

  // hero: fixed layout 4, one large ad with two smaller ones on the side
  document.body.classList.add('hero-v4','hero-row'); curV='4';
  renderSide();

  // model filtering
  // category rail: no scrollbar; soft fade on the side that has more categories
  const rail=document.querySelector('.rail');
  if(rail){const edge=()=>{const max=rail.scrollWidth-rail.clientWidth;rail.classList.toggle('fade-r',max>2&&rail.scrollLeft<max-2);rail.classList.toggle('fade-l',rail.scrollLeft>2)};
    rail.addEventListener('scroll',edge,{passive:true});addEventListener('resize',edge);edge();}
  const cards=[...document.querySelectorAll('.mcard')], fbtns=[...document.querySelectorAll('[data-filter]')], cats=[...document.querySelectorAll('.cat')], empty=$('empty'), note=$('search-note');
  function apply(test,{filter=null,cat=null}={}){
    clearExtra();grid.classList.remove('many');let n=0;cards.forEach(c=>{const ok=test(c);c.hidden=!ok;if(ok)n++});
    fbtns.forEach(b=>b.setAttribute('aria-pressed',b.dataset.filter===filter));
    cats.forEach(b=>b.setAttribute('aria-pressed',b.dataset.f===cat));
    empty.hidden=n>0;return n;
  }
  const has=(c,t)=>c.dataset.tags.split(' ').includes(t);
  // search results come from every listed model (#ev-models), not only the featured cards
  const ALL=JSON.parse($('ev-models').textContent), grid=empty.parentElement, VB={sedan:'0 0 320 112',hatch:'0 0 320 112',suv:'0 0 320 120'};
  const byId={};cards.forEach(c=>{const a=c.querySelector('h3 a');if(a)byId[a.getAttribute('href').replace(/^.*modeli\//,'').replace(/\.html.*$/,'')]=c});
  let extra=[];
  // warm the browser cache with every model photo once the page has loaded, so filters and search show photos instantly
  addEventListener('load',()=>{(window.requestIdleCallback||(f=>setTimeout(f,300)))(()=>ALL.forEach(m=>{if(m.img){const i=new Image();i.decoding='async';i.src=m.img}}))});
  function clearExtra(){extra.forEach(e=>e.remove());extra=[]}
  // the picture opens the model page, like the button (kept out of the tab order: the button is the accessible link)
  const imgLink=(img,href)=>img.replace(/^<div /,'<a href="'+href+'" tabindex="-1" aria-hidden="true" ').replace(/ role="img"/,'').replace(/<\/div>$/,'</a>');
  function mkCard(m){
    const cmpBtn=id=>{let on=false;try{on=(JSON.parse(sessionStorage.getItem('evc-cmp')||'[]')||[]).indexOf(id)>-1}catch(e){}
      return '<button type="button" class="cmp-add" data-cmp="'+id+'" aria-pressed="'+on+'" aria-label="'+(on?'Ukloni iz poređenja':'Dodaj u poređenje')+'" title="'+(on?'Ukloni iz poređenja':'Dodaj u poređenje')+'"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h14m0 0-3.5-3.5M18 8l-3.5 3.5M20 16H6m0 0 3.5-3.5M6 16l3.5 3.5"/></svg></button>'};
    if(byId[m.id]){const c=byId[m.id].cloneNode(true);c.hidden=false;if(!c.querySelector('.cmp-add'))c.insertAdjacentHTML('afterbegin',cmpBtn(m.id));return c}
    const href='modeli/'+m.id+'', label=m.b+' '+m.n, a=document.createElement('article');a.className='mcard';
    const sm=m.img?m.img.replace(/\.webp$/,'-640.webp'):'';
    const img=m.img?'<div class="img photo"><img src="'+sm+'" srcset="'+sm+' 640w, '+m.img+' 1280w" sizes="(max-width: 620px) 48vw, (max-width: 1000px) 46vw, 400px" alt="'+esc(label)+'" decoding="async"></div>'
      :m.lg&&logoFor[m.b]?'<div class="img lg" role="img" aria-label="'+esc(label)+'"><span class="blogo has-img" aria-hidden="true"><img src="'+esc(logoFor[m.b])+'" alt="" decoding="async"></span></div>'
      :m.sil?'<div class="img"><svg viewBox="'+VB[m.sil]+'" role="img" aria-label="'+esc(label)+'"><use href="#car-'+m.sil+'"/></svg></div>'
      :'<div class="img ph">FOTOGRAFIJA USKORO</div>';
    a.innerHTML=cmpBtn(m.id)+imgLink(img,href)+'<div class="body"><div><div class="mk">'+esc(m.b.toUpperCase())+'</div><h3><a href="'+href+'">'+esc(m.n)+'</a></h3></div>'
      +'<div class="tags"><span class="tag">100% EV</span>'+(m.cls?'<span class="tag gray">'+esc(m.cls.toUpperCase())+'</span>':'')+'</div>'
      +'<dl class="specs"><div><dt>DOMET (WLTP)</dt><dd>'+(m.r?'do '+m.r+' km':'Na upit')+'</dd></div><div><dt>KLASA</dt><dd>'+(m.cls?esc(m.cls):'Na upit')+'</dd></div>'
      +'<div><dt>BATERIJA</dt><dd>'+(m.kwh?esc(m.kwh)+' kWh':'Na upit')+'</dd></div><div><dt>POGON</dt><dd>Električni</dd></div></dl>'
      +'<a href="'+href+'" class="btn btn-dark">Detalji modela <span class="arr">→</span></a></div>';
    return a;
  }
  // "Izdvojeni modeli": 6 random models that have a photo, one per brand, different on every visit
  setTimeout(function(){const pool=ALL.filter(m=>m.img),seen={},pick=[];
    for(let i=pool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[pool[i],pool[j]]=[pool[j],pool[i]]}
    pool.forEach(m=>{if(pick.length<6&&!seen[m.b]){seen[m.b]=1;pick.push(m)}});
    if(pick.length<6)return;
    const fresh=pick.map(m=>{const c=mkCard(m);c.hidden=false;c.dataset.tags=m.t.join(' ');c.dataset.name=m.n;c.dataset.range=m.r||0;c.dataset.brand=m.b;return c});
    cards.forEach(c=>c.remove());cards.length=0;Object.keys(byId).forEach(k=>delete byId[k]);
    fresh.forEach((c,k)=>{grid.insertBefore(c,empty);cards.push(c);byId[pick[k].id]=c});
  },0);   /* after the rest of this script has run (mkCard needs helpers defined further down) */
  function searchAll(test,{cat=null}={}){
    clearExtra();cards.forEach(c=>c.hidden=true);
    const res=ALL.filter(test), frag=document.createDocumentFragment();
    res.forEach(m=>{const c=mkCard(m);extra.push(c);frag.append(c)});
    grid.insertBefore(frag,empty);grid.classList.toggle('many',res.length>6);
    fbtns.forEach(b=>b.setAttribute('aria-pressed','false'));
    cats.forEach(b=>b.setAttribute('aria-pressed',b.dataset.f===cat));
    empty.hidden=res.length>0;return res.length;
  }
  // section mode: featured models (default) or search results
  const plural=n=>n===1?'1 model':n+' modela';
  function setMode(results,label,n){
    $('models-title').textContent=results?'Rezultati pretrage':'Izdvojeni modeli';
    $('models-sub').hidden=!results; $('search-reset').hidden=!results; $('model-filters').hidden=results;
    if(results)$('models-sub').innerHTML=(label?'<strong>'+esc(label)+'</strong> · ':'')+(n?'Pronađeno: '+plural(n)+'.':'Nema rezultata.');
    $('empty-text').textContent=results?'Nijedan model ne odgovara pretrazi. Promenite kriterijume ili poništite pretragu.':'Nijedan model ne odgovara izabranom filteru.';
    note.textContent='';
  }
  function showFeatured(){
    apply(()=>true,{filter:'all'});setMode(false);
    ['f-brand','f-model','f-body','f-range'].forEach(id=>{$(id).value=''});
    if(typeof dds!=='undefined')dds.forEach(d=>{d.setOnly(null);d.sync()});
  }
  const toResults=()=>$('modeli').scrollIntoView({behavior:reduce()?'auto':'smooth'});
  // filter buttons: "Svi" shows the featured cards; a body type shows up to 6 matching models from all models, featured first
  function showType(f){
    clearExtra();cards.forEach(c=>c.hidden=true);
    const match=ALL.filter(m=>m.t.includes(f)), feat=match.filter(m=>byId[m.id]), groups={};
    match.filter(m=>!byId[m.id]).forEach(m=>{(groups[m.b]=groups[m.b]||[]).push(m)});
    Object.values(groups).forEach(g=>g.sort((a,b)=>(b.img?1:0)-(a.img?1:0)));
    const mix=[], keys=Object.keys(groups).sort(()=>Math.random()-.5);for(let k=0;mix.length<match.length-feat.length;k++)keys.forEach(b=>{if(groups[b][k])mix.push(groups[b][k])});
    const res=feat.concat(mix).slice(0,6), frag=document.createDocumentFragment();
    res.forEach(m=>{const c=mkCard(m);extra.push(c);frag.append(c)});
    grid.insertBefore(frag,empty);grid.classList.remove('many');
    fbtns.forEach(b=>b.setAttribute('aria-pressed',b.dataset.filter===f));
    cats.forEach(b=>b.setAttribute('aria-pressed','false'));
    empty.hidden=res.length>0;
  }
  fbtns.forEach(b=>b.onclick=()=>{const f=b.dataset.filter;if(f==='all')apply(()=>true,{filter:'all'});else showType(f);setMode(false)});
  cats.forEach(b=>b.onclick=()=>{
    const f=b.dataset.f;const n=searchAll(m=>m.t.includes(f),{cat:f});
    setMode(true,'Kategorija: '+b.querySelector('strong').textContent,n);toResults();
  });
  $('search-reset').onclick=()=>{showFeatured();$('pretraga').scrollIntoView({behavior:reduce()?'auto':'smooth'})};

  $('search-form').addEventListener('submit',e=>{
    e.preventDefault();
    const brand=$('f-brand').value, model=$('f-model').value, body=$('f-body').value, minR=+$('f-range').value||0;
    const n=searchAll(m=>(!brand||m.b===brand)&&(!model||m.n===model)&&(!body||m.t.includes(body))&&(!minR||m.r>=minR));
    const parts=[brand,model,body&&$('f-body').selectedOptions[0].text,minR&&$('f-range').selectedOptions[0].text].filter(Boolean);
    setMode(true,parts.length?parts.join(', '):'Svi modeli',n);toResults();
  });


  // custom dropdowns for the search panel
  const logoFor={};document.querySelectorAll('.btile[data-brand-page]').forEach(t=>{const l=t.querySelector('.blogo img');if(l)logoFor[t.dataset.brandPage]=l.getAttribute('src')});
  const esc=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const dds=[];
  const checkSvg='<svg class="dd-check" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 7.5 5.8 10 11 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  function enhance(sel,cfg){
    const f=sel.closest('.field'), lab=f.querySelector('label');
    sel.classList.add('enh');sel.tabIndex=-1;sel.setAttribute('aria-hidden','true');
    const btn=document.createElement('button');btn.type='button';btn.className='dd-btn';btn.id=sel.id+'-btn';
    btn.setAttribute('aria-haspopup','listbox');btn.setAttribute('aria-expanded','false');btn.setAttribute('aria-controls',sel.id+'-list');
    btn.innerHTML='<span class="dd-val"></span><svg class="dd-chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    lab.htmlFor=btn.id;
    const pop=document.createElement('div');pop.className='dd-pop';pop.hidden=true;
    pop.innerHTML='<div class="dd-list" role="listbox" id="'+sel.id+'-list" aria-label="'+esc(lab.textContent)+'"></div>';
    f.append(btn,pop);
    const list=pop.querySelector('.dd-list'), q=pop.querySelector('.dd-q');
    let only=null;
    const optHTML=o=>{
      const logo=cfg.logos&&o.value&&logoFor[o.value]?'<span class="dd-logo" aria-hidden="true"><span class="blogo has-img"><img src="'+esc(logoFor[o.value])+'" alt="" decoding="async"></span></span>':'';
      return '<div class="dd-opt" role="option" tabindex="-1" data-v="'+esc(o.value)+'" aria-selected="'+(o.value===sel.value)+'">'+logo+'<span class="dd-txt">'+esc(o.text)+'</span>'+checkSvg+'</div>';
    };
    function build(){
      const term=q?q.value.trim().toLowerCase():'';let html='',groups=0;
      [...sel.children].forEach(ch=>{
        if(ch.tagName==='OPTGROUP'){
          if(only&&ch.label!==only)return;
          const os=[...ch.children].filter(o=>!term||o.text.toLowerCase().includes(term)||ch.label.toLowerCase().includes(term));
          if(!os.length)return;groups++;
          html+='<div class="dd-group">'+esc(ch.label)+'</div>'+os.map(optHTML).join('');
        }else if(!term||ch.text.toLowerCase().includes(term))html+=optHTML(ch);
      });
      if(cfg.models&&only&&!groups&&!term)html+='<div class="dd-empty">Za brend '+esc(only)+' još nema električnih modela u listi.</div>';
      list.innerHTML=html||'<div class="dd-empty">Nema rezultata.</div>';
    }
    function sync(){const o=sel.options[sel.selectedIndex];btn.querySelector('.dd-val').textContent=o?o.text:'';btn.classList.toggle('set',!!sel.value)}
    function open(){
      dds.forEach(d=>d!==api&&d.close());build();pop.hidden=false;btn.setAttribute('aria-expanded','true');f.classList.add('open');
      pop.classList.remove('right');if(pop.getBoundingClientRect().right>innerWidth-12)pop.classList.add('right');
      const cur=list.querySelector('[aria-selected="true"]');if(cur)cur.scrollIntoView({block:'nearest'});
      if(q){q.value='';build();q.focus()}else (cur||list.querySelector('.dd-opt'))?.focus();
    }
    function close(back){if(pop.hidden)return;pop.hidden=true;btn.setAttribute('aria-expanded','false');f.classList.remove('open');if(back)btn.focus()}
    function choose(v){sel.value=v;sel.dispatchEvent(new Event('change'));sync();close(true)}
    btn.addEventListener('click',()=>pop.hidden?open():close());
    btn.addEventListener('keydown',e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();open()}});
    list.addEventListener('click',e=>{const o=e.target.closest('.dd-opt');if(o)choose(o.dataset.v)});
    if(q)q.addEventListener('input',build);
    pop.addEventListener('keydown',e=>{
      const opts=[...list.querySelectorAll('.dd-opt')],k=opts.indexOf(document.activeElement);
      if(e.key==='ArrowDown'){e.preventDefault();(opts[k+1]||opts[0])?.focus()}
      else if(e.key==='ArrowUp'){e.preventDefault();if(k<=0&&q)q.focus();else (opts[k-1]||opts[opts.length-1])?.focus()}
      else if(e.key==='Enter'){e.preventDefault();const o=k>=0?opts[k]:opts[0];if(o)choose(o.dataset.v)}
      else if(e.key==='Escape'){e.preventDefault();close(true)}
      else if(e.key==='Tab')close();
    });
    const api={close,sync,setOnly(b){only=b}};dds.push(api);sync();return api;
  }
  document.addEventListener('click',e=>{if(!e.target.closest('.field'))dds.forEach(d=>d.close())});
  const brandDD=enhance($('f-brand'),{logos:true}), modelDD=enhance($('f-model'),{models:true});
  enhance($('f-body'),{});enhance($('f-range'),{});
  $('f-brand').addEventListener('change',()=>{
    const b=$('f-brand').value, o=$('f-model').selectedOptions[0];
    modelDD.setOnly(b||null);
    if(b&&o&&o.value&&o.parentElement.label!==b){$('f-model').value='';modelDD.sync()}
  });
  $('f-model').addEventListener('change',()=>{
    const o=$('f-model').selectedOptions[0];
    if(o&&o.value&&o.parentElement.tagName==='OPTGROUP'&&!$('f-brand').value){$('f-brand').value=o.parentElement.label;brandDD.sync();modelDD.setOnly(o.parentElement.label)}
  });

})();
