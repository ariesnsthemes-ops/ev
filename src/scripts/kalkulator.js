
(function(){
var MODELS=__MODELS__,FUEL=__FUEL__;
var LOSS=1.10,AVG=17,$=function(id){return document.getElementById('kc-'+id)};
var nf=new Intl.NumberFormat('sr-Latn-RS',{maximumFractionDigits:0});
var nf1=new Intl.NumberFormat('sr-Latn-RS',{minimumFractionDigits:1,maximumFractionDigits:1});
var rsd=function(v){return nf.format(Math.round(v))+' RSD'};
function fd(s){var d=String(s).split('-');return (+d[2])+'. '+(+d[1])+'. '+d[0]+'.'}
var dt=fd(FUEL.provereno||FUEL.datum);
var F={b:{name:'Benzin',price:FUEL.benzin,l:6.5,hint:'BMB 95, najviša maloprodajna cena na dan '+dt},
       d:{name:'Dizel',price:FUEL.dizel,l:5.5,hint:'Evrodizel, najviša maloprodajna cena na dan '+dt}};
$('fuelLi').textContent='Cene goriva su najviše maloprodajne cene koje Ministarstvo trgovine utvrđuje petkom, a mi ih proveravamo svakog dana. Cene na dan '+dt+': BMB 95 '+FUEL.benzin+' RSD/l, Evrodizel '+FUEL.dizel+' RSD/l.';
var sel=$('model'),brand='',og=null;
MODELS.forEach(function(m,i){
  if(m.b!==brand){og=document.createElement('optgroup');og.label=m.b;sel.appendChild(og);brand=m.b}
  var o=document.createElement('option');o.value=i;o.textContent=m.n;og.appendChild(o);
});
var q=null;try{q=new URLSearchParams(location.search).get('model')}catch(e){}
var ph=document.createElement('option');ph.value='';ph.textContent='Izaberite model';sel.insertBefore(ph,sel.firstChild);
var start=MODELS.findIndex(function(m){return m.id===q});   /* preselected only when coming from a model page */
sel.value=start<0?'':String(start);

/* custom dropdowns, same behaviour and look as the homepage search filters (.dd-* styles in site.css) */
var DDS=[],CHECK='<svg class="dd-check" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 7.5 5.8 10 11 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
function escH(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function enhance(s){
  var f=s.closest('.kc-fld'),lab=f.querySelector('label');
  s.classList.add('enh');s.tabIndex=-1;s.setAttribute('aria-hidden','true');
  var btn=document.createElement('button');btn.type='button';btn.className='dd-btn';btn.id=s.id+'-btn';
  btn.setAttribute('aria-haspopup','listbox');btn.setAttribute('aria-expanded','false');btn.setAttribute('aria-controls',s.id+'-list');
  btn.innerHTML='<span class="dd-val"></span><svg class="dd-chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  lab.htmlFor=btn.id;
  var pop=document.createElement('div');pop.className='dd-pop';pop.hidden=true;
  pop.innerHTML='<div class="dd-list" role="listbox" id="'+s.id+'-list" aria-label="'+escH(lab.textContent)+'"></div>';
  f.appendChild(btn);f.appendChild(pop);
  var list=pop.querySelector('.dd-list');
  function opt(o){return '<div class="dd-opt" role="option" tabindex="-1" data-v="'+escH(o.value)+'" aria-selected="'+(o.value===s.value)+'"><span class="dd-txt">'+escH(o.text)+'</span>'+CHECK+'</div>'}
  function build(){var h='';[].forEach.call(s.children,function(ch){if(ch.tagName==='OPTION'&&ch.value==='')return;
    if(ch.tagName==='OPTGROUP')h+='<div class="dd-group">'+escH(ch.label)+'</div>'+[].map.call(ch.children,opt).join('');else h+=opt(ch)});list.innerHTML=h}
  function sync(){var o=s.options[s.selectedIndex];btn.querySelector('.dd-val').textContent=o?o.text:'';btn.classList.toggle('set',!!s.value)}
  function open(){DDS.forEach(function(d){if(d!==api)d.close()});build();pop.hidden=false;btn.setAttribute('aria-expanded','true');f.classList.add('open');
    pop.classList.remove('right');if(pop.getBoundingClientRect().right>innerWidth-12)pop.classList.add('right');
    var cur=list.querySelector('[aria-selected="true"]');if(cur){cur.scrollIntoView({block:'nearest'});cur.focus({preventScroll:true})}else{var o=list.querySelector('.dd-opt');if(o)o.focus()}}
  function close(back){if(pop.hidden)return;pop.hidden=true;btn.setAttribute('aria-expanded','false');f.classList.remove('open');if(back)btn.focus()}
  function choose(v){s.value=v;s.dispatchEvent(new Event('change'));sync();close(true)}
  btn.addEventListener('click',function(){pop.hidden?open():close()});
  btn.addEventListener('keydown',function(e){if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();open()}});
  list.addEventListener('click',function(e){var o=e.target.closest('.dd-opt');if(o)choose(o.dataset.v)});
  pop.addEventListener('keydown',function(e){
    var os=[].slice.call(list.querySelectorAll('.dd-opt')),k=os.indexOf(document.activeElement);
    if(e.key==='ArrowDown'){e.preventDefault();(os[k+1]||os[0]).focus()}
    else if(e.key==='ArrowUp'){e.preventDefault();(os[k-1]||os[os.length-1]).focus()}
    else if(e.key==='Enter'){e.preventDefault();if(k>=0)choose(os[k].dataset.v)}
    else if(e.key==='Escape'){e.preventDefault();close(true)}
    else if(e.key==='Tab')close();
  });
  var api={close:close,sync:sync};DDS.push(api);sync();return api;
}
document.addEventListener('click',function(e){if(!e.target.closest('.kc-fld'))DDS.forEach(function(d){d.close()})});
var verDD=null;
function fillVer(){
  var v=$('ver');v.innerHTML='';
  if(sel.value===''){$('verWrap').hidden=true;$('carGroup').classList.remove('kc-g2');if(verDD)verDD.sync();return}
  var m=MODELS[+sel.value];
  m.v.forEach(function(x,i){var o=document.createElement('option');o.value=i;
    o.textContent=nf1.format(x[0])+' kWh · '+nf.format(x[1])+' km';v.appendChild(o)});
  v.value=m.v.length-1;$('verWrap').hidden=m.v.length<2;$('carGroup').classList.toggle('kc-g2',m.v.length>1);if(verDD)verDD.sync();
}
function num(id,dflt){var x=parseFloat(String($(id).value).replace(',','.'));return isFinite(x)?x:dflt}
function calc(){
  var m=sel.value===''?null:MODELS[+sel.value],x=m?(m.v[+$('ver').value]||m.v[0]):null,own=$('own').checked,none=!m&&!own;
  var cons=own?num('ownKwh',AVG):(m&&m.ok?x[2]:AVG),base=cons;
  $('badNote').hidden=own||!m||m.ok;
  if($('winter').checked)cons*=1.25;
  $('consInfo').hidden=none;
  if(!none)$('consInfo').innerHTML=(own?'<span class="kc-chip">Vaša potrošnja '+nf1.format(base)+' kWh/100 km</span>':
    m.ok?'<span class="kc-chip">'+nf1.format(base)+' kWh/100 km</span> iz '+nf1.format(x[0])+' kWh i '+nf.format(x[1])+' km WLTP':
    '<span class="kc-chip fuel">'+nf1.format(AVG)+' kWh/100 km, prosek</span>')+
    ($('winter').checked?' <span class="kc-chip">zimi '+nf1.format(cons)+'</span>':'');
  var km=+$('km').value,hs=+$('home').value/100,pHome;
  [$('km'),$('home')].forEach(function(r){r.style.setProperty('--p',((r.value-r.min)/(r.max-r.min)*100)+'%')});
  $('kmOut').textContent=nf.format(km)+' km';
  $('homeOut').textContent=Math.round(hs*100)+'% kod kuće';
  if($('dual').checked){var n=Math.min(100,Math.max(0,num('nightShare',90)))/100;pHome=n*num('pNight',0)+(1-n)*num('pDay',0)}
  else pHome=num('pHome',0);
  var pKwh=hs*pHome+(1-hs)*num('pPub',0);
  var e100=cons*LOSS*pKwh,g100=num('lper',0)*num('pFuel',0),eYr=e100*km/100,gYr=g100*km/100,sv=gYr-eYr;
  var ev=function(v){return none?'–':rsd(v)};
  $('e100').textContent=ev(e100);$('g100').textContent=rsd(g100);
  $('eMo').textContent=ev(eYr/12);$('gMo').textContent=rsd(gYr/12);
  $('eYr').textContent=ev(eYr);$('gYr').textContent=rsd(gYr);
  $('hero').classList.toggle('kc-empty',none);
  if(none){
    $('hero').classList.remove('neg');$('heroK').textContent='Godišnja ušteda na energiji';
    $('save').textContent='Izaberite model';
    $('saveSub').textContent='Izaberite električni automobil i videćete koliko biste uštedeli u odnosu na gorivo. Gorivo vas sada košta '+rsd(gYr)+' godišnje.';
  }else{
  $('hero').classList.toggle('neg',sv<0);
  $('heroK').textContent=sv<0?'Struja je skuplja za':'Godišnja ušteda na energiji';
  $('save').innerHTML=nf.format(Math.abs(Math.round(sv)))+' <small>RSD</small>';
  $('saveSub').textContent=sv<0?'Sa ovim cenama punjenje košta više od goriva. Probajte veći udeo kućnog punjenja.':
    'Oko '+rsd(sv/12)+' mesečno. Prosečna cena struje '+nf1.format(pKwh)+' RSD/kWh.';
  }
  if(none)eYr=0;
  var top=Math.max(eYr,gYr)*5||1,h='';
  for(var y=1;y<=5;y++){
    h+='<div class="kc-bar-row"><span class="y">'+y+'. god.</span><div class="kc-pair">'+
      (none?'':'<div class="kc-bar ev" style="width:'+(eYr*y/top*100)+'%"></div>')+'<div class="kc-bar" style="width:'+(gYr*y/top*100)+'%"></div>'+
      '<div class="kc-vals"><b>'+ev(eYr*y)+'</b><span>'+rsd(gYr*y)+'</span></div></div></div>';
  }
  $('bars').innerHTML=h;
}
function setFuel(k){
  var f=F[k];
  $('fB').setAttribute('aria-pressed',k==='b');$('fD').setAttribute('aria-pressed',k==='d');
  $('pFuel').value=f.price;$('lper').value=f.l;$('fuelHint').textContent=f.hint;
  $('fuelTh').textContent=f.name;$('fuelLg').textContent=f.name;calc();
}
sel.addEventListener('change',function(){fillVer();calc()});
$('own').addEventListener('change',function(){$('ownWrap').hidden=!$('own').checked;calc()});
$('dual').addEventListener('change',function(){var d=$('dual').checked,pf=$('pPub').closest('.kc-fld');$('dualRow').hidden=!d;$('pubRow').hidden=!d;(d?$('pubRow'):$('singleRow')).appendChild(pf);$('singleRow').hidden=d;calc()});
$('fB').addEventListener('click',function(){setFuel('b')});$('fD').addEventListener('click',function(){setFuel('d')});
$('f').addEventListener('input',calc);$('f').addEventListener('submit',function(e){e.preventDefault()});
var modelDD=enhance(sel);verDD=enhance($('ver'));fillVer();setFuel('b');
})();
