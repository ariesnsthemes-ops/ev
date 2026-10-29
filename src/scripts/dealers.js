(function(){
var $=function(i){return document.getElementById(i)},list=$('d-list');if(!list)return;
var cards=[].slice.call(list.querySelectorAll('.dcard')),blocks=[].slice.call(list.querySelectorAll('.city-block')),side=$('cat-side'),scrim=$('cat-scrim'),total=cards.length;
var inputs=[].slice.call(side.querySelectorAll('input'));
function sel(n){return inputs.filter(function(i){return i.name===n&&i.checked}).map(function(i){return i.value})}
function apply(push){
  var g=sel('g'),b=sel('b'),n=0;
  cards.forEach(function(c){var cb=c.dataset.b.split(' ');var ok=(!g.length||g.indexOf(c.dataset.c)>-1)&&(!b.length||b.some(function(x){return cb.indexOf(x)>-1}));c.hidden=!ok;if(ok)n++});
  blocks.forEach(function(bl){bl.hidden=!bl.querySelector('.dcard:not([hidden])')});
  $('cat-count').textContent='Prikazano '+n+' od '+total+' distributera';
  $('cat-empty').hidden=n>0;
  var a=g.length+b.length;list.classList.toggle('filtered',!!b.length);$('cat-n').hidden=!a;$('cat-n').textContent='('+a+')';
  $('cat-apply').textContent=n?('Prikaži '+n+' distributera'):'Nema rezultata';
  evcFacets(side,cards,function(c,f){var cb=c.dataset.b.split(' ');return (!f.g.length||f.g.indexOf(c.dataset.c)>-1)&&(!f.b.length||f.b.some(function(x){return cb.indexOf(x)>-1}))});
  if(push!==false){var q=new URLSearchParams();if(g.length)q.set('grad',g.join(','));if(b.length)q.set('brend',b.join(','));
    try{history.replaceState(null,'',location.pathname+(q.toString()?'?'+q:''))}catch(e){}}
}
function setOpen(gr,o){gr.classList.toggle('open-all',o);var bt=gr.querySelector('.fmore');if(bt){bt.setAttribute('aria-expanded',o);bt.textContent=o?'Prikaži manje':'Prikaži više ('+bt.dataset.more+')'}}
[].slice.call(side.querySelectorAll('.fmore')).forEach(function(bt){bt.addEventListener('click',function(){var gr=bt.closest('.fgroup');setOpen(gr,!gr.classList.contains('open-all'))})});
function reset(){inputs.forEach(function(i){i.checked=false});apply()}
var q=new URLSearchParams(location.search),h=location.hash.slice(1);
(q.get('grad')||'').split(',').concat((q.get('brend')||'').split(',')).forEach(function(v){inputs.forEach(function(i){if(v&&i.value===v)i.checked=true})});
if(h&&!q.get('grad'))inputs.forEach(function(i){if(i.name==='g'&&i.value===h)i.checked=true});
[].slice.call(side.querySelectorAll('.fgroup')).forEach(function(gr){if(gr.querySelector('.fopt.more input:checked'))setOpen(gr,true)});
side.addEventListener('change',function(){apply()});
$('freset').addEventListener('click',reset);$('cat-empty-reset').addEventListener('click',reset);
function open(o){side.classList.toggle('open',o);scrim.hidden=!o;document.body.classList.toggle('no-scroll',o);if(o)$('cat-close').focus()}
$('cat-open').addEventListener('click',function(){open(true)});[$('cat-close'),$('cat-apply'),scrim].forEach(function(x){x.addEventListener('click',function(){open(false)})});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&side.classList.contains('open'))open(false)});
apply(false);
})();