
(function(){
  /* cookie consent: nothing from Google Analytics loads until the visitor clicks "Prihvati" */
  var GA='__GA__',K='evc-consent',MAX=1000*60*60*24*180;
  function read(){try{var v=JSON.parse(localStorage.getItem(K)||'null');if(v&&Date.now()-v.t<MAX)return v.c}catch(e){}return null}
  function save(c){try{localStorage.setItem(K,JSON.stringify({c:c,t:Date.now()}))}catch(e){}}
  var loaded=false;
  function loadGA(){if(loaded||!GA)return;loaded=true;
    window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};
    gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'granted'});
    gtag('js',new Date());gtag('config',GA,{cookie_expires:15552000,allow_google_signals:false,allow_ad_personalization_signals:false});
    var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(s)}
  function clearGA(){document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();if(/^_ga/.test(n)){
    ['',location.hostname,'.'+location.hostname.replace(/^www\./,'')].forEach(function(d){document.cookie=n+'=; Max-Age=0; path=/'+(d?'; domain='+d:'')})}})}
  var box=null;
  function show(){
    if(!box){box=document.createElement('div');box.className='ck';box.setAttribute('role','dialog');box.setAttribute('aria-live','polite');box.setAttribute('aria-label','Kolačići');
      var base=/\/(modeli|brendovi)\//.test(location.pathname)?'../':'';
      box.innerHTML='<p>Koristimo kolačiće za anonimnu statistiku poseta (Google Analytics), samo uz vašu saglasnost. <a href="'+base+'politika-privatnosti#kolacici">Saznajte više</a></p>'
        +'<div class="ck-btns"><button type="button" class="btn btn-ghost" data-ck="denied">Odbij</button><button type="button" class="btn btn-dark" data-ck="granted">Prihvati</button></div>';
      box.addEventListener('click',function(e){var b=e.target.closest('[data-ck]');if(!b)return;var c=b.getAttribute('data-ck');save(c);box.hidden=true;
        if(c==='granted')loadGA();else{clearGA();if(loaded)location.reload()}});
      document.body.appendChild(box)}
    box.hidden=false}   /* no auto-focus: it drew a focus ring around "Prihvati" before the visitor did anything */
  document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-cookie-settings]');if(a){e.preventDefault();show()}});
  function init(){var c=read();if(c==='granted')loadGA();else if(c!=='denied')show()}
  if(document.readyState!=='loading')init();else document.addEventListener('DOMContentLoaded',init);
})();
