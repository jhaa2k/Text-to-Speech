import os,platform,time,threading
from pathlib import Path
class VoiceEngine:
    def __init__(self,output_dir):
        self.output_dir=Path(output_dir)/"exports"; self.output_dir.mkdir(parents=True,exist_ok=True)
        self._tts=None; self._ready=False; self._voices=[]; self._lock=threading.Event()
        self.android=os.environ.get("ANDROID_ARGUMENT") is not None
    def list_voices(self):
        if self.android:return self.android_voices()
        try:
            import pyttsx3
            e=pyttsx3.init(); result=[{"name":v.name,"id":v.id,"locale":str(getattr(v,"languages",[""])[0])} for v in e.getProperty("voices")]; e.stop()
            self._voices=result; return result
        except Exception:return []
    def android_voices(self):
        from jnius import autoclass,PythonJavaClass,java_method
        TTS=autoclass("android.speech.tts.TextToSpeech")
        class Init(PythonJavaClass):
            __javainterfaces__=["android/speech/tts/TextToSpeech$OnInitListener"]; __javacontext__="app"
            @java_method("(I)V")
            def onInit(inner,status): self._ready=(status==TTS.SUCCESS); self._lock.set()
        self._listener=Init(); activity=autoclass("org.kivy.android.PythonActivity").mActivity
        self._tts=TTS(activity,self._listener); self._lock.wait(20)
        if not self._ready:raise RuntimeError("Android TTS service failed to initialize.")
        out=[]; it=self._tts.getVoices().iterator()
        while it.hasNext():
            v=it.next(); out.append({"name":str(v.getName()),"locale":str(v.getLocale().toLanguageTag()),"quality":int(v.getQuality())})
        self._voices=sorted(out,key=lambda x:(x["locale"],x["name"])); return self._voices
    def synthesize(self,text,voice,rate,pitch,volume):
        path=self.output_dir/("VOX_"+time.strftime("%Y%m%d_%H%M%S")+".wav")
        if self.android:self.android_synthesize(text,voice,rate,pitch,volume,path)
        else:self.desktop_synthesize(text,voice,rate,volume,path)
        return str(path)
    def android_synthesize(self,text,voice,rate,pitch,volume,path):
        from jnius import autoclass,PythonJavaClass,java_method
        TTS=autoclass("android.speech.tts.TextToSpeech"); Bundle=autoclass("android.os.Bundle"); File=autoclass("java.io.File")
        if self._tts is None or not self._ready:self.android_voices()
        it=self._tts.getVoices().iterator()
        while it.hasNext():
            v=it.next()
            if str(v.getName())==voice:self._tts.setVoice(v);break
        self._tts.setSpeechRate(float(rate)); self._tts.setPitch(float(pitch))
        class Progress(PythonJavaClass):
            __javainterfaces__=["android/speech/tts/UtteranceProgressListener"]; __javacontext__="app"
            def __init__(inner):super().__init__();inner.event=threading.Event();inner.error=None
            @java_method("(Ljava/lang/String;)V")
            def onStart(inner,u):pass
            @java_method("(Ljava/lang/String;)V")
            def onDone(inner,u):inner.event.set()
            @java_method("(Ljava/lang/String;Ljava/lang/String;)V")
            def onError(inner,u,e):inner.error=str(e);inner.event.set()
            @java_method("(Ljava/lang/String;I)V")
            def onStop(inner,u,c):inner.event.set()
        listener=Progress(); self._tts.setOnUtteranceProgressListener(listener)
        bundle=Bundle(); bundle.putFloat("volume",float(volume)); uid="vox"+str(int(time.time()*1000))
        if self._tts.synthesizeToFile(text,bundle,File(str(path)),uid)!=TTS.SUCCESS:raise RuntimeError("TTS engine rejected the request.")
        if not listener.event.wait(180):raise TimeoutError("Speech synthesis timed out.")
        if listener.error:raise RuntimeError(listener.error)
        if not path.exists() or path.stat().st_size<100:raise RuntimeError("TTS returned an empty file.")
    def desktop_synthesize(self,text,voice,rate,volume,path):
        import pyttsx3
        e=pyttsx3.init(); selected=next((v for v in e.getProperty("voices") if v.name==voice),None)
        if selected:e.setProperty("voice",selected.id)
        e.setProperty("rate",int(190*float(rate)));e.setProperty("volume",float(volume))
        e.save_to_file(text,str(path));e.runAndWait();e.stop()
        if not path.exists() or path.stat().st_size<100:raise RuntimeError("No audio produced; check installed system voices.")
    def play(self,path):
        if self.android:
            from jnius import autoclass
            p=autoclass("android.media.MediaPlayer")();p.setDataSource(path);p.prepare();p.start();self._player=p
        else:
            import subprocess,sys
            if sys.platform.startswith("win"):os.startfile(path)
            elif sys.platform=="darwin":subprocess.Popen(["afplay",path])
            else:subprocess.Popen(["xdg-open",path])
