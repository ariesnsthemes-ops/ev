(function(){
var $=function(i){return document.getElementById(i)},grid=$('cat-grid');if(!grid)return;
var cards=[].slice.call(grid.children),side=$('cat-side'),scrim=$('cat-scrim'),total=cards.length;
var inputs=[].slice.call(side.querySelectorAll('input'));
function sel(name){return inputs.filter(function(i){return i.name===name&&i.checked}).map(function(i){return i.value})}
function apply(push){
  var k=sel('k'),b=sel('b'),d=+(sel('d')[0]||0),n=0;
  cards.forEach(function(c){var t=c.dataset.t.split(' ');
    var ok=(!k.length||k.some(function(x){return t.indexOf(x)>-1}))&&(!b.length||b.indexOf(c.dataset.b)>-1)&&(+c.dataset.r>=d);
    c.hidden=!ok;if(ok)n++;});
  var s=$('cat-sort').value;
  cards.slice().sort(function(a,z){return s==='n'?a.dataset.n.localeCompare(z.dataset.n,'sr'):(+z.dataset.r)-(+a.dataset.r)}).forEach(function(c){grid.appendChild(c)});
  $('cat-count').textContent='Prikazano '+n+' od '+total+' modela';
  $('cat-empty').hidden=n>0;
  var active=k.length+b.length+(d?1:0);$('cat-n').hidden=!active;$('cat-n').textContent='('+active+')';
  $('cat-apply').textContent=n?('Prikaži '+n+(n===1?' model':' modela')):'Nema rezultata';
  evcFacets(side,cards,function(c,f){var t=c.dataset.t.split(' ');return (!f.k.length||f.k.some(function(x){return t.indexOf(x)>-1}))&&(!f.b.length||f.b.indexOf(c.dataset.b)>-1)&&(+c.dataset.r>=+(f.d[0]||0))});
  if(push!==false){var q=new URLSearchParams();if(b.length)q.set('brend',b.join(','));if(d)q.set('domet',d);if(k.length)q.set('karoserija',k.join(','));if(s!=='r')q.set('sort',s);
    try{history.replaceState(null,'',location.pathname+(q.toString()?'?'+q:''))}catch(e){}}
}
/* "Prikaži više" per group; a group opens by itself when one of its hidden options is selected */
function setOpen(g,o){g.classList.toggle('open-all',o);var bt=g.querySelector('.fmore');if(bt){bt.setAttribute('aria-expanded',o);bt.textContent=o?'Prikaži manje':'Prikaži više ('+bt.dataset.more+')'}}
function openSelected(){[].slice.call(side.querySelectorAll('.fgroup')).forEach(function(g){if(g.querySelector('.fopt.more input:checked'))setOpen(g,true)})}
[].slice.call(side.querySelectorAll('.fmore')).forEach(function(bt){bt.addEventListener('click',function(){var g=bt.closest('.fgroup');setOpen(g,!g.classList.contains('open-all'))})});
/* sort: small custom listbox */
var sb=$('cat-sort-btn'),sm=$('cat-sort-menu'),opts=[].slice.call(sm.children);
function setSort(v,silent){$('cat-sort').value=v;opts.forEach(function(o){o.setAttribute('aria-selected',o.dataset.v===v)});$('cat-sort-val').textContent=opts.filter(function(o){return o.dataset.v===v})[0].textContent;if(!silent)apply()}
function menu(o){sm.hidden=!o;sb.setAttribute('aria-expanded',o);if(o){var cur=sm.querySelector('[aria-selected="true"]')||opts[0];cur.focus()}}
sb.addEventListener('click',function(){menu(sm.hidden)});
sb.addEventListener('keydown',function(e){if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();menu(true)}});
opts.forEach(function(o,i){o.addEventListener('click',function(){setSort(o.dataset.v);menu(false);sb.focus()});
  o.addEventListener('keydown',function(e){if(e.key==='ArrowDown'){e.preventDefault();opts[Math.min(i+1,opts.length-1)].focus()}else if(e.key==='ArrowUp'){e.preventDefault();opts[Math.max(i-1,0)].focus()}else if(e.key==='Enter'||e.key===' '){e.preventDefault();o.click()}else if(e.key==='Escape'||e.key==='Tab'){menu(false);if(e.key==='Escape')sb.focus()}})});
document.addEventListener('click',function(e){if(!sm.hidden&&!$('cat-sort-wrap').contains(e.target))menu(false)});
function reset(){inputs.forEach(function(i){i.checked=false});apply()}
var q=new URLSearchParams(location.search);
(q.get('karoserija')||'').split(',').concat((q.get('brend')||'').split(',')).forEach(function(v){inputs.forEach(function(i){if(v&&i.type==='checkbox'&&i.value===v)i.checked=true})});
if(q.get('domet'))inputs.forEach(function(i){if(i.name==='d')i.checked=i.value===q.get('domet')});
/* range works as single choice that can be cleared: ticking one unticks the others */
side.addEventListener('change',function(e){var t=e.target;if(t.name==='d'&&t.checked)inputs.forEach(function(i){if(i.name==='d'&&i!==t)i.checked=false})},true);
if(q.get('sort')==='n')setSort('n',true);
openSelected();
side.addEventListener('change',function(){apply()});
$('freset').addEventListener('click',reset);$('cat-empty-reset').addEventListener('click',reset);
function open(o){side.classList.toggle('open',o);scrim.hidden=!o;document.body.classList.toggle('no-scroll',o);if(o)$('cat-close').focus()}
$('cat-open').addEventListener('click',function(){open(true)});[$('cat-close'),$('cat-apply'),scrim].forEach(function(x){x.addEventListener('click',function(){open(false)})});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&side.classList.contains('open'))open(false)});
apply(false);
})();