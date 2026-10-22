  // copy advertising email
  $('copy-email').addEventListener('click',e=>{
    const btn=e.currentTarget, txt=$('zakup-email').textContent;
    const done=()=>{btn.textContent='Adresa kopirana';setTimeout(()=>btn.textContent='Kopiraj adresu',2000)};
    const fallback=()=>{const r=document.createRange();r.selectNodeContents($('zakup-email'));const s=getSelection();s.removeAllRanges();s.addRange(r);btn.textContent='Adresa je označena'};
    try{navigator.clipboard.writeText(txt).then(done,fallback)}catch(err){fallback()}
  });
