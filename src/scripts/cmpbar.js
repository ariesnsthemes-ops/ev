(function(){
  /* "Uporedi": pick up to 3 models on any page, then open the comparison */
  var K='evc-cmp',base=/\/(modeli|brendovi)\//.test(location.pathname)?'../':'';
  function get(){try{return (JSON.parse(sessionStorage.getItem(K)||'[]')||[]).slice(0,3)}catch(e){return []}}
  function put(a){try{sessionStorage.setItem(K,JSON.stringify(a))}catch(e){}}
  var bar=null,msg=null;
  function sync(){
    var a=get();
    [].slice.call(document.querySelectorAll('.cmp-add')).forEach(function(b){var on=a.indexOf(b.dataset.cmp)>-1;b.setAttribute('aria-pressed',on);var l=on?'Ukloni iz poređenja':'Dodaj u poređenje';b.setAttribute('aria-label',l);b.title=l});
    if(document.getElementById('cmp-tbl'))return;
    if(!bar){bar=document.createElement('div');bar.className='cmp-bar';bar.setAttribute('role','region');bar.setAttribute('aria-label','Poređenje modela');
      bar.innerHTML='<span class="cmp-bar-t"></span><button type="button" class="cmp-bar-x">Očisti</button><a class="btn btn-dark cmp-bar-go"></a>';
      document.body.appendChild(bar);bar.querySelector('.cmp-bar-x').addEventListener('click',function(){put([]);sync()})}
    bar.hidden=!a.length;
    bar.querySelector('.cmp-bar-t').textContent=msg||(a.length===1?'Izaberite još jedan model za poređenje':'Izabrano '+a.length+' od 3 modela');
    var go=bar.querySelector('.cmp-bar-go');go.href=base+'uporedi?modeli='+a.join(',');go.textContent='Uporedi ('+a.length+') →';
  }
  window.evcCmpSync=sync;
  document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.cmp-add');if(!b)return;e.preventDefault();
    var a=get(),i=a.indexOf(b.dataset.cmp);msg=null;
    if(i>-1)a.splice(i,1);else if(a.length>=3)msg='Najviše 3 modela. Uklonite jedan da biste dodali novi.';else a.push(b.dataset.cmp);
    put(a);sync();if(msg)setTimeout(function(){msg=null;sync()},3500)});
  if(document.readyState!=='loading')sync();else document.addEventListener('DOMContentLoaded',sync);
  window.addEventListener('pageshow',sync);
})();