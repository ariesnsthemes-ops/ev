document.addEventListener('DOMContentLoaded',function(){
var $=function(i){return document.getElementById(i)},list=$('ch-list');if(!list)return;
var items=[].slice.call(list.children),side=$('cat-side'),scrim=$('cat-scrim'),total=items.length,PAGE=24,shown=PAGE;
var inputs=[].slice.call(side.querySelectorAll('input'));
function sel(n){return inputs.filter(function(i){return i.name===n&&i.checked}).map(function(i){return i.value})}
/* map: OpenFreeMap street map (free, no key); Kosovo is shown as part of Serbia */
var map=null,popup=null,ready=false,FEATS={};
items.forEach(function(li){FEATS[li.dataset.id]={type:'Feature',geometry:{type:'Point',coordinates:[+li.dataset.lng,+li.dataset.lat]},properties:{id:li.dataset.id,fast:+li.dataset.kw>=50?1:0}}});
var KOS=['Kosovo','Kosova','Kosovë','Kosova / Kosovo','Kosovo / Kosova','Косово'],SRB=['Serbia','Srbija','Србија'];
function isLegacy(f){if(!Array.isArray(f))return false;if(f[0]==='all'||f[0]==='any'||f[0]==='none')return f.slice(1).some(isLegacy);return typeof f[1]==='string'}
function guardBoundary(f){
  var leg=['none',['==','disputed',1],['all',['in','adm0_l'].concat(KOS),['in','adm0_r'].concat(SRB)],['all',['in','adm0_l'].concat(SRB),['in','adm0_r'].concat(KOS)]];
  var g=function(k){return ['coalesce',['get',k],'']};
  var ex=['!',['any',['==',['to-number',['coalesce',['get','disputed'],0]],1],
      ['all',['in',g('adm0_l'),['literal',KOS]],['in',g('adm0_r'),['literal',SRB]]],
      ['all',['in',g('adm0_l'),['literal',SRB]],['in',g('adm0_r'),['literal',KOS]]],
      ['within',BORDER_ZONE]]];
  if(!f)return ex;return isLegacy(f)?['all',f,leg]:['all',f,ex];
}
function guardLabel(f){
  var leg=['any',['!=','class','country'],['all',['!in','name'].concat(KOS),['!in','name:en'].concat(KOS),['!in','name_en'].concat(KOS),['!in','name:latin'].concat(KOS)]];
  var ex=['any',['!=',['coalesce',['get','class'],''],'country'],['!',['any',
      ['in',['coalesce',['get','name'],''],['literal',KOS]],['in',['coalesce',['get','name:en'],''],['literal',KOS]],
      ['in',['coalesce',['get','name_en'],''],['literal',KOS]],['in',['coalesce',['get','name:latin'],''],['literal',KOS]]]]];
  if(!f)return ex;return isLegacy(f)?['all',f,leg]:['all',f,ex];
}
function tidyStyle(){
  (map.getStyle().layers||[]).forEach(function(l){
    try{if(l['source-layer']==='boundary')map.setFilter(l.id,guardBoundary(l.filter));
        else if(l['source-layer']==='place')map.setFilter(l.id,guardLabel(l.filter));}catch(e){}});
}
function addChargers(){
  if(!map.getSource('rs-outline'))map.addSource('rs-outline',{type:'geojson',data:OUTLINE});
  var first=(map.getStyle().layers||[]).filter(function(l){return l.type==='symbol'})[0];
  if(!map.getLayer('rs-fill'))map.addLayer({id:'rs-fill',type:'fill',source:'rs-outline',paint:{'fill-color':'#16a34a','fill-opacity':.04}},first&&first.id);
  if(!map.getSource('ch'))map.addSource('ch',{type:'geojson',data:{type:'FeatureCollection',features:[]}});
  if(!map.getLayer('ch-dots'))map.addLayer({id:'ch-dots',type:'circle',source:'ch',paint:{
    'circle-radius':['interpolate',['linear'],['zoom'],6,['case',['==',['get','fast'],1],6,4.5],12,['case',['==',['get','fast'],1],10,8]],
    'circle-color':['case',['==',['get','fast'],1],'#16a34a','#16202e'],'circle-stroke-color':'#ffffff','circle-stroke-width':2}});
  ready=true;apply(false,FIT);
}
var FALLBACK={version:8,sources:{},layers:[{id:'bg',type:'background',paint:{'background-color':'#eef2f1'}}]};
if(window.maplibregl){
  map=new maplibregl.Map({container:'ch-map',style:'https://tiles.openfreemap.org/styles/positron',center:[20.9,43.9],zoom:6.2,
    cooperativeGestures:true,attributionControl:{compact:false},locale:{'CooperativeGesturesHandler.WindowsHelpText':'Držite Ctrl i skrolujte za zumiranje mape','CooperativeGesturesHandler.MacHelpText':'Držite ⌘ i skrolujte za zumiranje mape','CooperativeGesturesHandler.MobileHelpText':'Pomerajte mapu sa dva prsta'}});
  map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-left');
  var styled=false;
  map.on('style.load',function(){if(map.getStyle().sources&&Object.keys(map.getStyle().sources).length&&!map.getSource('rs-outline'))styled=true;tidyStyle();addChargers()});
  /* if the street map cannot load (offline, blocked), keep the map usable with a plain background and the Serbia outline */
  var fb=function(){if(!styled&&!ready){map.setStyle(FALLBACK);map.once('style.load',function(){map.addLayer({id:'rs-line',type:'line',source:'rs-outline',paint:{'line-color':'#94a3b8','line-width':1}})})}};
  map.on('error',function(){setTimeout(fb,300)});setTimeout(fb,6000);
  map.on('click','ch-dots',function(e){openPop(e.features[0].properties.id)});
  map.on('mouseenter','ch-dots',function(){map.getCanvas().style.cursor='pointer'});map.on('mouseleave','ch-dots',function(){map.getCanvas().style.cursor=''});
}
function openPop(id){
  var li=list.querySelector('.ch[data-id="'+id+'"]');if(!li||!map)return;
  var box=document.createElement('div');box.className='ch-pop';
  box.innerHTML='<strong></strong><span class="k"></span><span class="a"></span><span class="t"></span><a target="_blank" rel="nofollow noopener">Navigacija ↗</a>';
  var ad=li.querySelector('.ch-addr');
  box.children[0].textContent=li.querySelector('h3').textContent;box.children[1].textContent=li.querySelector('.ch-kw').textContent;
  box.children[2].textContent=ad?ad.textContent:'';box.children[3].textContent=[].slice.call(li.querySelectorAll('.ch-tags .tag')).map(function(t){return t.textContent}).join(' · ');
  box.children[4].href=li.querySelector('.ch-act a').href;
  if(popup)popup.remove();popup=new maplibregl.Popup({offset:12,maxWidth:'260px',focusAfterOpen:false}).setLngLat(FEATS[id].geometry.coordinates).setDOMContent(box).addTo(map);
}
var FIT=true,FLY=0,RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
function apply(push,fit){
  var p=+(sel('p')[0]||0),k=sel('k'),a=sel('a'),vis=[];
  items.forEach(function(li){var c=li.dataset.c.split(' ');
    var ok=(+li.dataset.kw>=p)&&(!k.length||k.some(function(x){return c.indexOf(x)>-1}))&&(!a.length||a.indexOf(li.dataset.a)>-1);
    li.classList.toggle('off',!ok);if(ok)vis.push(li);});
  items.forEach(function(li){li.hidden=true});vis.slice(0,shown).forEach(function(li){li.hidden=false});
  $('ch-more').hidden=vis.length<=shown;$('ch-more').textContent='Prikaži još ('+(vis.length-shown)+')';
  $('cat-count').textContent='Prikazano '+vis.length+' od '+total+' punjača';
  $('cat-empty').hidden=vis.length>0;
  var act=k.length+a.length+(p?1:0);$('cat-n').hidden=!act;$('cat-n').textContent='('+act+')';
  $('cat-apply').textContent=vis.length?('Prikaži '+vis.length+' punjača'):'Nema rezultata';
  evcFacets(side,items,function(li,f){var c=li.dataset.c.split(' ');return (+li.dataset.kw>=+(f.p[0]||0))&&(!f.k.length||f.k.some(function(x){return c.indexOf(x)>-1}))&&(!f.a.length||f.a.indexOf(li.dataset.a)>-1)});
  if(map&&ready){map.getSource('ch').setData({type:'FeatureCollection',features:vis.map(function(li){return FEATS[li.dataset.id]})});
    if(popup)popup.remove();
    if(fit&&vis.length){var b=new maplibregl.LngLatBounds();vis.forEach(function(li){b.extend([+li.dataset.lng,+li.dataset.lat])});map.stop();map.fitBounds(b,{padding:40,maxZoom:13,duration:fit===2&&!RM?1000:0})}}
  if(push!==false){var q=new URLSearchParams();if(p)q.set('snaga',p);if(k.length)q.set('konektor',k.join(','));if(a.length)q.set('pristup',a.join(','));
    try{history.replaceState(null,'',location.pathname+(q.toString()?'?'+q:''))}catch(e){}}
}
side.addEventListener('change',function(e){var t=e.target;if(t.name==='p'&&t.checked)inputs.forEach(function(i){if(i.name==='p'&&i!==t)i.checked=false});shown=PAGE;apply(true,2)});
$('ch-more').addEventListener('click',function(){shown+=PAGE;apply(false)});
/* the whole card shows the charger on the map (the Navigacija link keeps its own job) */
list.addEventListener('click',function(e){if(e.target.closest('a'))return;var li=e.target.closest('.ch');if(!li||!map)return;
  if(window.getSelection&&String(getSelection()).length>2&&!e.target.closest('.ch-show'))return;
  items.forEach(function(x){x.classList.toggle('sel',x===li)});
  if(popup)popup.remove();
  var el=$('ch-map'),r=el.getBoundingClientRect(),inView=r.top>=0&&r.bottom<=innerHeight;
  if(!inView)el.scrollIntoView({behavior:RM?'auto':'smooth',block:'center'});
  var go=function(){map.stop();var t=++FLY;map.once('moveend',function(){if(t===FLY)openPop(li.dataset.id)});
    map.flyTo({center:[+li.dataset.lng,+li.dataset.lat],zoom:15,curve:1.42,duration:RM?0:1600,essential:true})};
  if(inView||RM)go();else setTimeout(go,350)});
function reset(){inputs.forEach(function(i){i.checked=false});shown=PAGE;apply(true,true)}
var q=new URLSearchParams(location.search);
if(q.get('snaga'))inputs.forEach(function(i){if(i.name==='p')i.checked=i.value===q.get('snaga')});
(q.get('konektor')||'').split(',').forEach(function(v){inputs.forEach(function(i){if(v&&i.name==='k'&&i.value===v)i.checked=true})});
(q.get('pristup')||'').split(',').forEach(function(v){inputs.forEach(function(i){if(v&&i.name==='a'&&i.value===v)i.checked=true})});
$('freset').addEventListener('click',reset);$('cat-empty-reset').addEventListener('click',reset);
function open(o){side.classList.toggle('open',o);scrim.hidden=!o;document.body.classList.toggle('no-scroll',o);if(o)$('cat-close').focus()}
$('cat-open').addEventListener('click',function(){open(true)});[$('cat-close'),$('cat-apply'),scrim].forEach(function(x){x.addEventListener('click',function(){open(false);if(map)setTimeout(function(){map.resize()},50)})});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&side.classList.contains('open'))open(false)});
apply(false,true);
});