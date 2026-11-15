import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from tts_engine import VoiceEngine
from presets import PRESETS

BG=(.055,.065,.085,1); PANEL=(.095,.11,.14,1); ACCENT=(.42,.72,1,1); MUTED=(.62,.68,.76,1)
def lab(text,size=14,color=(.92,.94,.97,1),**kw):
    return Label(text=text,font_size=dp(size),color=color,halign="left",valign="middle",**kw)
def button(text,fn,height=42):
    b=Button(text=text,size_hint_y=None,height=dp(height),background_normal="",background_color=(.16,.2,.27,1))
    b.bind(on_release=lambda *_:fn()); return b
class VoxStudio(App):
    def build(self):
        self.title="VOX STUDIO"; self.engine=VoiceEngine(self.user_data_dir); self.voices=[]
        root=BoxLayout(orientation="vertical",padding=dp(14),spacing=dp(9))
        with root.canvas.before:
            from kivy.graphics import Color,Rectangle
            Color(*BG); self.bg=Rectangle(pos=root.pos,size=root.size)
        root.bind(pos=lambda w,v:setattr(self.bg,"pos",v),size=lambda w,v:setattr(self.bg,"size",v))
        head=BoxLayout(size_hint_y=None,height=dp(44))
        head.add_widget(lab("[b]VOX[/b]  STUDIO",19,markup=True)); head.add_widget(lab("AI VOICE WORKSHOP",10,MUTED,halign="right")); root.add_widget(head)
        self.editor=TextInput(hint_text="Write or paste your script…",multiline=True,size_hint_y=None,height=dp(155),padding=dp(12),background_color=PANEL,foreground_color=(.96,.97,1,1),hint_text_color=MUTED)
        root.add_widget(self.editor); root.add_widget(lab("VOICE PROFILE",11,ACCENT))
        self.voice=Spinner(text="Loading voices…",values=(),size_hint_y=None,height=dp(42),background_normal="",background_color=PANEL); root.add_widget(self.voice)
        root.add_widget(lab("STYLE PRESETS",11,ACCENT))
        grid=GridLayout(cols=2,spacing=dp(6),size_hint_y=None); grid.bind(minimum_height=grid.setter("height"))
        for n in PRESETS: grid.add_widget(button(n,lambda name=n:self.apply_preset(name),38))
        sc=ScrollView(size_hint_y=None,height=dp(116),do_scroll_x=False); sc.add_widget(grid); root.add_widget(sc)
        root.add_widget(lab("VOICE CONTROL",11,ACCENT))
        self.rate=self.slider_row(root,"Speed",.5,2,1,"1.00×")
        self.pitch=self.slider_row(root,"Pitch",.5,2,1,"1.00×")
        self.volume=self.slider_row(root,"Volume",0,1,1,"100%")
        root.add_widget(lab("OUTPUT FORMAT  ·  WAV",11,ACCENT))
        row=BoxLayout(size_hint_y=None,height=dp(42),spacing=dp(7)); row.add_widget(button("REFRESH VOICES",self.load_voices)); root.add_widget(row)
        actions=GridLayout(cols=2,spacing=dp(8),size_hint_y=None,height=dp(48))
        actions.add_widget(button("▶  PREVIEW",self.preview)); actions.add_widget(button("↓  EXPORT AUDIO",self.export)); root.add_widget(actions)
        self.status=lab("Ready. Enter text and choose a voice.",11,MUTED); root.add_widget(self.status)
        Clock.schedule_once(lambda *_:self.load_voices(),.5)
        return root
    def slider_row(self,root,title,lo,hi,value,initial):
        row=BoxLayout(size_hint_y=None,height=dp(38),spacing=dp(7)); row.add_widget(lab(title,12,MUTED,size_hint_x=.2))
        s=Slider(min=lo,max=hi,value=value); out=lab(initial,11,ACCENT,size_hint_x=.16,halign="right")
        s.bind(value=lambda _,v:setattr(out,"text",f"{int(v*100)}%" if title=="Volume" else f"{v:.2f}×"))
        row.add_widget(s); row.add_widget(out); root.add_widget(row); return s
    def load_voices(self):
        self.status.text="Scanning installed speech voices…"
        def run():
            try: data=self.engine.list_voices()
            except Exception as e: data=[]
            Clock.schedule_once(lambda *_:self.show_voices(data),0)
        threading.Thread(target=run,daemon=True).start()
    def show_voices(self,data):
        self.voices=data; names=[v["name"] for v in data]; self.voice.values=names
        self.voice.text=names[0] if names else "No voices found"
        self.status.text=f"{len(names)} installed voice(s) found. Add more in device TTS settings."
    def apply_preset(self,name):
        p=PRESETS[name]; self.rate.value=p["rate"]; self.pitch.value=p["pitch"]; self.volume.value=p["volume"]
        hint=p.get("voice_hint","")
        match=next((v["name"] for v in self.voices if hint and hint in (v["name"]+" "+v.get("locale","")).lower()),None)
        if match:self.voice.text=match
        self.status.text=f"{name} applied. Adjust the controls to taste."
    def args(self):
        text=self.editor.text.strip()
        if not text: raise ValueError("Please enter text first.")
        if len(text)>20000: raise ValueError("Maximum length is 20,000 characters per export.")
        return text,self.voice.text,self.rate.value,self.pitch.value,self.volume.value
    def preview(self): self.generate(True)
    def export(self): self.generate(False)
    def generate(self,preview):
        try: args=self.args()
        except Exception as e:self.status.text=str(e);return
        self.status.text="Generating speech…"
        def run():
            try:
                path=self.engine.synthesize(*args)
                if preview:self.engine.play(path)
                Clock.schedule_once(lambda *_:self.complete(path,preview),0)
            except Exception as e:Clock.schedule_once(lambda *_:setattr(self.status,"text","Error: "+str(e)),0)
        threading.Thread(target=run,daemon=True).start()
    def complete(self,path,preview):
        self.status.text=("Preview ready: " if preview else "Export saved: ")+path
        if not preview:
            content=BoxLayout(orientation="vertical",padding=dp(12),spacing=dp(8))
            content.add_widget(lab("WAV audio created successfully.",14)); content.add_widget(lab(path,10,MUTED))
            pop=Popup(title="EXPORT COMPLETE",content=content,size_hint=(.9,.35))
            content.add_widget(button("CLOSE",pop.dismiss)); pop.open()
if __name__=="__main__": VoxStudio().run()
