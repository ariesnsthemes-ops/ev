(function(){
var $=function(i){return document.getElementById(i)},tbl=$('cmp-tbl');if(!tbl)return;
var by={};CMP.forEach(function(m){by[m.id]=m});
var sel=[0,1,2].map(function(k){return $('cmp-s'+k)});
var fmt=function(v,u){return v?String(v).replace(/\B(?=(\d{3})+(?!\d))/g,'.')+(u||''):''};
var ROWS=[['Brend',function(m){return m.b}],['Klasa',function(m){return m.cls}],
  ['Domet (WLTP)',function(m){return m.rt}],['Baterija',function(m){return m.kt}],
  ['Dužina',function(m){return m.L||''}],['Širina',function(m){return m.W||''}],['Visina',function(m){return m.H||''}],
  ['Klirens',function(m){return m.C||''}],['Broj sedišta',function(m){return m.S?String(m.S):''}]];
function ids(){return sel.map(function(s){return s.value}).filter(function(v,i,a){return v&&a.indexOf(v)===i})}
function esc(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML}
function render(){
  if(typeof pickers!=='undefined')pickers.forEach(function(p){p.sync()});
  var list=ids().map(function(i){return by[i]}).filter(Boolean),diff=$('cmp-diff').checked;
  try{sessionStorage.setItem('evc-cmp',JSON.stringify(list.map(function(m){return m.id})))}catch(e){}
  if(window.evcCmpSync)window.evcCmpSync();
  $('cmp-empty').hidden=!!list.length;$('cmp-wrap').hidden=!list.length;
  var q=list.length?'?modeli='+list.map(function(m){return m.id}).join(','):'';try{history.replaceState(null,'',location.pathname+q)}catch(e){}
  if(!list.length){tbl.innerHTML='';return}
  var h='<thead><tr><th scope="col"><span class="sr">Podatak</span></th>'+list.map(function(m){
    return '<th scope="col"><div class="cmp-imgw"><a class="cmp-img'+(m.k==='photo'?' photo':'')+'" href="modeli/'+m.id+'">'+m.img+'</a>'
      +'<button type="button" class="cmp-x" data-id="'+m.id+'" aria-label="Ukloni '+esc(m.full)+' iz poređenja">×</button></div><span class="mk">'+esc(m.b.toUpperCase())+'</span><a class="cmp-name" href="modeli/'+m.id+'">'+esc(m.n)+'</a>'
      +'</th>'}).join('')+'</tr></thead><tbody>';
  ROWS.forEach(function(r){
    var vals=list.map(r[1]),same=vals.every(function(v){return v===vals[0]});
    if(diff&&list.length>1&&same)return;
    var best=null;if(r[3]&&list.length>1){var nums=list.map(r[2]);var mx=Math.max.apply(null,nums);if(mx>0&&nums.filter(function(n){return n===mx}).length<list.length)best=mx}
    h+='<tr><th scope="row">'+r[0]+'</th>'+list.map(function(m,k){var v=vals[k],b=best!==null&&r[2](m)===best;
      return '<td'+(b?' class="best"':'')+'>'+(v?esc(v):'<span class="na">–</span>')+'</td>'}).join('')+'</tr>'});
  tbl.innerHTML=h+'</tbody>';tbl.setAttribute('data-n',list.length);
  var fn=[];if(list.some(function(m){return /\*$/.test(m.W||'')}))fn.push('* Širina sa sklopljenim retrovizorima (proizvođač ne objavljuje širinu bez retrovizora).');
  if(list.some(function(m){return /\*\*$/.test(m.C||'')}))fn.push('** Klirens pod opterećenjem, kako ga navodi proizvođač.');
  $('cmp-fn').textContent=fn.join(' ');$('cmp-fn').hidden=!fn.length;
}
sel.forEach(function(s){s.addEventListener('change',render)});
/* custom model picker on top of each (visually hidden) select: search + list grouped by brand */
var norm=function(t){return (t||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/đ/g,'dj')};
var pickers=sel.map(function(s,k){
  var w=document.createElement('div');w.className='cpick';
  var btn=document.createElement('button');btn.type='button';btn.className='cpick-btn';btn.setAttribute('aria-haspopup','listbox');btn.setAttribute('aria-expanded','false');
  btn.innerHTML='<span class="cpick-val"></span>';
  var pop=document.createElement('div');pop.className='cpick-pop';pop.hidden=true;
  pop.innerHTML='<input type="search" class="cpick-q" placeholder="Pretražite model ili brend" autocomplete="off" aria-label="Pretraga modela"><ul class="cpick-list" role="listbox"></ul><p class="cpick-none" hidden>Nema modela za ovu pretragu.</p>';
  var list=pop.querySelector('ul'),q=pop.querySelector('input'),none=pop.querySelector('.cpick-none');
  [].slice.call(s.querySelectorAll('optgroup')).forEach(function(g){
    var h=document.createElement('li');h.className='cpick-g';h.textContent=g.label;h.setAttribute('role','presentation');list.appendChild(h);
    [].slice.call(g.children).forEach(function(o){var li=document.createElement('li');li.className='cpick-o';li.setAttribute('role','option');li.dataset.v=o.value;
      li.dataset.s=norm(g.label+' '+o.textContent);li.textContent=o.textContent;li.tabIndex=-1;list.appendChild(li)})});
  s.parentNode.appendChild(w);w.appendChild(btn);w.appendChild(pop);s.classList.add('cpick-native');s.tabIndex=-1;s.setAttribute('aria-hidden','true');
  btn.id='cmp-b'+k;var lab=s.parentNode.querySelector('label');if(lab){lab.setAttribute('for','cmp-b'+k)}
  function items(){return [].slice.call(list.querySelectorAll('.cpick-o')).filter(function(li){return !li.hidden&&!li.classList.contains('off')})}
  function filter(){var t=norm(q.value.trim()),n=0;var last=null,shown=false;
    [].slice.call(list.children).forEach(function(li){if(li.classList.contains('cpick-g')){if(last)last.hidden=!shown;last=li;shown=false;return}
      var ok=!t||li.dataset.s.indexOf(t)>-1;li.hidden=!ok;if(ok){shown=true;n++}});if(last)last.hidden=!shown;none.hidden=n>0}
  function open(o){pickers.forEach(function(p){if(p!==api)p.close()});pop.hidden=!o;btn.setAttribute('aria-expanded',o);w.classList.toggle('open',o);
    if(o){var taken=sel.filter(function(x){return x!==s}).map(function(x){return x.value});
      [].slice.call(list.querySelectorAll('.cpick-o')).forEach(function(li){li.classList.toggle('off',taken.indexOf(li.dataset.v)>-1);li.setAttribute('aria-selected',li.dataset.v===s.value)});
      q.value='';filter();q.focus({preventScroll:true});var cur=list.querySelector('[aria-selected="true"]');if(cur)cur.scrollIntoView({block:'nearest'})}}
  function choose(v){s.value=v;s.dispatchEvent(new Event('change'));open(false);btn.focus({preventScroll:true})}
  btn.addEventListener('click',function(){open(pop.hidden)});
  q.addEventListener('input',filter);
  q.addEventListener('keydown',function(e){var it=items();if(e.key==='ArrowDown'){e.preventDefault();if(it[0])it[0].focus()}else if(e.key==='Enter'){e.preventDefault();if(it[0])choose(it[0].dataset.v)}else if(e.key==='Escape'){open(false);btn.focus()}});
  list.addEventListener('click',function(e){var li=e.target.closest('.cpick-o');if(li&&!li.classList.contains('off'))choose(li.dataset.v)});
  list.addEventListener('keydown',function(e){var it=items(),i=it.indexOf(document.activeElement);
    if(e.key==='ArrowDown'){e.preventDefault();if(it[i+1])it[i+1].focus()}else if(e.key==='ArrowUp'){e.preventDefault();if(i>0)it[i-1].focus();else q.focus()}
    else if(e.key==='Enter'||e.key===' '){e.preventDefault();if(document.activeElement.dataset.v)choose(document.activeElement.dataset.v)}else if(e.key==='Escape'){open(false);btn.focus()}});
  var api={close:function(){if(!pop.hidden)open(false)},sync:function(){var o=s.options[s.selectedIndex];var has=!!s.value;
    btn.querySelector('.cpick-val').textContent=has?o.textContent:'Izaberite model';btn.classList.toggle('empty',!has)}};
  return api});
document.addEventListener('click',function(e){if(!e.target.closest('.cpick'))pickers.forEach(function(p){p.close()})});
document.addEventListener('keydown',function(e){if(e.key==='Escape')pickers.forEach(function(p){p.close()})});
$('cmp-diff').addEventListener('change',render);
$('cmp-clear').addEventListener('click',function(){sel.forEach(function(s){s.value=''});render()});
tbl.addEventListener('click',function(e){var b=e.target.closest('.cmp-x');if(!b)return;var keep=ids().filter(function(i){return i!==b.dataset.id});sel.forEach(function(s,k){s.value=keep[k]||''});render()});
var start=(new URLSearchParams(location.search).get('modeli')||'').split(',').filter(function(i){return by[i]});
if(!start.length){try{start=(JSON.parse(sessionStorage.getItem('evc-cmp')||'[]')||[]).filter(function(i){return by[i]})}catch(e){}}
start.slice(0,3).forEach(function(i,k){sel[k].value=i});
render();
})();