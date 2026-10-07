"use strict";

/* Micro capté à la demande ; WAV temporaire envoyé uniquement au serveur loopback. */
const DicteeNative = (() => {
  const disponible = () => ["localhost", "127.0.0.1", "[::1]"].includes(location.hostname)
    && Boolean(navigator.mediaDevices?.getUserMedia && window.AudioContext);
  let fluxReserve = null;
  const contraintesMicro = {audio:{channelCount:1,echoCancellation:true,noiseSuppression:true}};
  function libererPreparation() {
    fluxReserve?.getTracks().forEach(p=>p.stop()); fluxReserve=null;
  }
  async function autoriser() {
    libererPreparation();
    if (!disponible()) return false;
    try {
      // Attendre la décision : démarrer sur un délai ferait lire la question
      // alors que le dialogue d'autorisation est encore ouvert.
      fluxReserve=await navigator.mediaDevices.getUserMedia(contraintesMicro);
      return true;
    } catch { return false; }
  }
  function wav(blocs, frequence) {
    const total = blocs.reduce((n, b) => n + b.length, 0);
    const entree = new Float32Array(total);
    let offset = 0;
    for (const bloc of blocs) { entree.set(bloc, offset); offset += bloc.length; }
    const ratio = frequence / 16000;
    const taille = Math.floor(total / ratio);
    const buffer = new ArrayBuffer(44 + taille * 2), vue = new DataView(buffer);
    const texte = (pos, s) => [...s].forEach((c, i) => vue.setUint8(pos + i, c.charCodeAt(0)));
    texte(0,"RIFF");vue.setUint32(4,36+taille*2,true);texte(8,"WAVE");texte(12,"fmt ");
    vue.setUint32(16,16,true);vue.setUint16(20,1,true);vue.setUint16(22,1,true);
    vue.setUint32(24,16000,true);vue.setUint32(28,32000,true);vue.setUint16(32,2,true);vue.setUint16(34,16,true);
    texte(36,"data");vue.setUint32(40,taille*2,true);
    for(let i=0;i<taille;i++) {
      let somme=0;const a=Math.floor(i*ratio), b=Math.min(total,Math.max(a+1,Math.floor((i+1)*ratio)));
      for(let j=a;j<b;j++) somme+=entree[j];
      const x=Math.max(-1,Math.min(1,somme/(b-a)));
      vue.setInt16(44+i*2,x<0?x*32768:x*32767,true);
    }
    return new Uint8Array(buffer);
  }
  function demarrer({onDebut,onFin,onErreur,onResultat,onPartiel,onTraitement,enAttente=false}={}) {
    let flux, contexte, source, noeud, minuterie, apercu, annule=false, termine=false;
    let envoi=null, requete=null, dernierTexte="", tailleTranscrite=0;
    let captureAutorisee=!enAttente;
    const blocs=[];
    function nettoyer() {
      clearTimeout(minuterie);clearInterval(apercu);
      if(noeud){noeud.onaudioprocess=null;noeud.disconnect();}
      source?.disconnect();flux?.getTracks().forEach(p=>p.stop());
      if(contexte && contexte.state!=="closed") contexte.close().catch(()=>{});
    }
    function erreur(code) { if(!annule) onErreur?.(code); }
    async function transcrire(finale) {
      // Un seul appel natif à la fois. Le dernier inclut tout l'enregistrement.
      if(envoi){if(finale){await envoi;return transcrire(true);}return;}
      if(annule || !captureAutorisee)return;
      const taille=blocs.length;
      if(finale && taille===tailleTranscrite && dernierTexte){
        onResultat?.(dernierTexte);onFin?.();blocs.length=0;return;
      }
      if(!taille){if(finale)erreur("audio_vide");return;}
      envoi=(async()=>{
        const controleur=new AbortController();requete=controleur;
        const delai=setTimeout(()=>controleur.abort(),25000);
        try {
          const bytes=wav(blocs.slice(0,taille),contexte.sampleRate);
          let binaire="";
          for(let i=0;i<bytes.length;i+=8192)binaire+=String.fromCharCode(...bytes.subarray(i,i+8192));
          const r=await fetch("/api/capacites/dictee",{method:"POST",headers:{"Content-Type":"application/json"},
            body:JSON.stringify({audio_base64:btoa(binaire)}),signal:controleur.signal});
          const data=await r.json();
          if(!r.ok || !data.disponible)throw Error(data.raison||"indisponible");
          const texte=String(data.texte||"").trim();
          if(!texte)throw Error("parole_non_detectee");
          if(annule)return;
          dernierTexte=texte;tailleTranscrite=taille;
          if(finale){onResultat?.(texte);onFin?.();blocs.length=0;}
          else onPartiel?.(texte);
        }catch(e){if(finale)erreur(e.name==="AbortError"?"delai_depasse":e.message);}
        finally{clearTimeout(delai);}
      })();
      await envoi;envoi=null;
    }
    function lancerLimite() {
      if (!minuterie && captureAutorisee && contexte) minuterie=setTimeout(()=>controle.stop(),55000);
    }
    const controle={
      activer(){if(annule || termine)return;captureAutorisee=true;lancerLimite();},
      abort(){annule=true;termine=true;requete?.abort();nettoyer();blocs.length=0;},
      async stop(){
        if(termine)return;
        if(!contexte){controle.abort();onFin?.();return;}
        termine=true;nettoyer();
        if(annule)return;
        onTraitement?.();
        await transcrire(true);
      }
    };
    (async()=>{
      try {
        // Ouvrir le micro dès le clic : le serveur contrôlera le moteur au POST.
        const reserve=fluxReserve;fluxReserve=null;
        flux=reserve || await navigator.mediaDevices.getUserMedia(contraintesMicro);
        if(annule){nettoyer();return;}
        contexte=new AudioContext();await contexte.resume();
        if(annule){nettoyer();return;}
        source=contexte.createMediaStreamSource(flux);
        noeud=contexte.createScriptProcessor(2048,1,1);
        let captureCommencee=false;
        noeud.onaudioprocess=e=>{
          // Pendant la synthèse, le matériel chauffe mais aucun échantillon
          // n'est conservé ni envoyé au moteur de reconnaissance.
          if(termine || !captureAutorisee)return;
          blocs.push(new Float32Array(e.inputBuffer.getChannelData(0)));
          if(!captureCommencee){captureCommencee=true;onDebut?.();}
        };
        source.connect(noeud);noeud.connect(contexte.destination);
        apercu=setInterval(()=>{if(!termine)transcrire(false);},600);
        lancerLimite();
      }catch(e){nettoyer();erreur(e.name==="NotAllowedError"?"micro_refuse":e.message);}
    })();
    return controle;
  }
  return {disponible,demarrer,wav,autoriser,libererPreparation};
})();
