
/* sidebar filters: live counts per option for the current selection; options with 0 results are hidden */
window.evcFacets=function(side,items,test){
  var inputs=[].slice.call(side.querySelectorAll('.fopt input')),cur={};
  inputs.forEach(function(i){cur[i.name]=cur[i.name]||[];if(i.checked)cur[i.name].push(i.value)});
  inputs.forEach(function(i){var f={},n=0;for(var k in cur)f[k]=cur[k];f[i.name]=[i.value];
    items.forEach(function(it){if(test(it,f))n++});
    var l=i.closest('.fopt'),em=l.querySelector('em');if(em)em.textContent=n;l.classList.toggle('zero',!n&&!i.checked)});
  [].slice.call(side.querySelectorAll('.fgroup')).forEach(function(g){
    var all=[].slice.call(g.querySelectorAll('.fopt')),vis=all.filter(function(l){return !l.classList.contains('zero')}),bt=g.querySelector('.fmore');
    if(bt){all.forEach(function(l){l.classList.remove('more')});vis.forEach(function(l,k){if(k>=4)l.classList.add('more')});
      var m=Math.max(0,vis.length-4);bt.dataset.more=m;bt.hidden=!m;if(!g.classList.contains('open-all'))bt.textContent='Prikaži više ('+m+')'}
    g.hidden=!vis.length});
};

(function(){
  // a new page always opens at its top (also inside embedding frames), unless the link points to a section
  try{if('scrollRestoration' in history)history.scrollRestoration='manual'}catch(e){}
  var toTop=function(){if(location.hash)return;var t=document.getElementById('top')||document.body;window.scrollTo(0,0);try{t.scrollIntoView({block:'start'})}catch(e){}window.scrollTo(0,0)};
  if(document.readyState!=='loading')toTop();else document.addEventListener('DOMContentLoaded',toTop);
  window.addEventListener('pageshow',function(e){if(!e.persisted)toTop()});
  /* when the page sits in an embedding frame that resizes after load, repeat the jump to the top a few times,
     unless the visitor has already started scrolling */
  var moved=false;['wheel','touchstart','keydown'].forEach(function(t){window.addEventListener(t,function(){moved=true},{passive:true,once:true})});
  var again=function(){if(!moved)toTop()};window.addEventListener('load',function(){again();setTimeout(again,150);setTimeout(again,500)});
  var mb=document.getElementById('menu-btn'),nl=document.getElementById('nav-links');
  if(mb&&nl)mb.addEventListener('click',function(){var o=nl.classList.toggle('open');mb.setAttribute('aria-expanded',o)});
  // dealer contact: every dealer is in the HTML; the city picker only shows one city at a time
  var sel=document.getElementById('city-sel');
  if(sel){var cards=[].slice.call(document.querySelectorAll('#dealer-main .dcard'));
    var show=function(){cards.forEach(function(c){c.hidden=c.getAttribute('data-city')!==sel.value})};
    sel.addEventListener('change',show);show();
    /* city picker: same dropdown list as the homepage search filters (.dd-pop / .dd-opt) instead of the system list */
    var wrap=sel.parentNode,lab=document.querySelector('label[for="city-sel"]');
    var cb=document.createElement('button');cb.type='button';cb.className='city-btn';cb.id='city-btn';
    cb.setAttribute('aria-haspopup','listbox');cb.setAttribute('aria-expanded','false');cb.setAttribute('aria-controls','city-list');
    cb.innerHTML='<span class="dd-val"></span><svg class="dd-chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var cp=document.createElement('div');cp.className='dd-pop';cp.hidden=true;
    cp.innerHTML='<div class="dd-list" role="listbox" id="city-list" aria-label="Grad"></div>';
    sel.classList.add('enh');sel.tabIndex=-1;sel.setAttribute('aria-hidden','true');if(lab)lab.htmlFor='city-btn';
    wrap.appendChild(cb);wrap.appendChild(cp);
    var cl=cp.firstChild,ck='<svg class="dd-check" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 7.5 5.8 10 11 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var csync=function(){cb.firstChild.textContent=sel.value};
    var cclose=function(back){if(cp.hidden)return;cp.hidden=true;cb.setAttribute('aria-expanded','false');wrap.classList.remove('open');if(back)cb.focus()};
    var copen=function(){cl.innerHTML=[].map.call(sel.options,function(o){var t=document.createElement('span');t.textContent=o.text;
        return '<div class="dd-opt" role="option" tabindex="-1" data-v="'+t.innerHTML.replace(/"/g,'&quot;')+'" aria-selected="'+(o.value===sel.value)+'"><span class="dd-txt">'+t.innerHTML+'</span>'+ck+'</div>'}).join('');
      cp.hidden=false;cb.setAttribute('aria-expanded','true');wrap.classList.add('open');
      var cur=cl.querySelector('[aria-selected="true"]')||cl.querySelector('.dd-opt');if(cur){cur.scrollIntoView({block:'nearest'});cur.focus({preventScroll:true})}};
    var cchoose=function(v){sel.value=v;sel.dispatchEvent(new Event('change'));csync();cclose(true)};
    cb.addEventListener('click',function(){cp.hidden?copen():cclose()});
    cb.addEventListener('keydown',function(e){if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();copen()}});
    cl.addEventListener('click',function(e){var o=e.target.closest('.dd-opt');if(o)cchoose(o.getAttribute('data-v'))});
    cp.addEventListener('keydown',function(e){var os=[].slice.call(cl.querySelectorAll('.dd-opt')),k=os.indexOf(document.activeElement);
      if(e.key==='ArrowDown'){e.preventDefault();(os[k+1]||os[0]).focus()}else if(e.key==='ArrowUp'){e.preventDefault();(os[k-1]||os[os.length-1]).focus()}
      else if(e.key==='Enter'||e.key===' '){e.preventDefault();if(k>=0)cchoose(os[k].getAttribute('data-v'))}else if(e.key==='Escape'){e.preventDefault();cclose(true)}else if(e.key==='Tab')cclose()});
    document.addEventListener('click',function(e){if(!wrap.contains(e.target))cclose()});
    csync();}
})();
