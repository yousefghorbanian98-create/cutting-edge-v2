"use client";
import React, { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Play, Pause, SkipBack, SkipForward, Dumbbell, Palette, Brain, Scissors, Volume2, Maximize2 } from "lucide-react";

type Panel = "editor" | "style" | "ai" | "muscle";

export default function App() {
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [dur, setDur] = useState(0);
  const [panel, setPanel] = useState<Panel>("editor");
  const [msgs, setMsgs] = useState<{r:string;t:string}[]>([{r:"ai",t:"سلام! ویدیوت رو آپلود کن تا آنالیزش کنم 🎬"}]);
  const [input, setInput] = useState("");
  const [intensity, setIntensity] = useState(60);
  const vRef = useRef<HTMLVideoElement>(null);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f?.type.startsWith("video/")) setVideoSrc(URL.createObjectURL(f));
  }, []);

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) setVideoSrc(URL.createObjectURL(f));
  };

  const toggle = () => {
    if (!vRef.current) return;
    playing ? vRef.current.pause() : vRef.current.play();
    setPlaying(!playing);
  };

  const fmt = (s: number) => `${Math.floor(s/60)}:${Math.floor(s%60).toString().padStart(2,"0")}`;

  const send = async () => {
    if (!input.trim()) return;
    setMsgs(p => [...p, {r:"user",t:input}]);
    const q = input; setInput("");
    try {
      const r = await fetch("http://127.0.0.1:8001/ai/chat", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({message:q, language:"fa"})
      });
      const d = await r.json();
      setMsgs(p => [...p, {r:"ai",t:d.reply||d.error}]);
    } catch { setMsgs(p => [...p, {r:"ai",t:"⚠️ سرور AI در دسترس نیست"}]); }
  };

  const panels: {id:Panel;icon:React.ElementType;label:string}[] = [
    {id:"editor",icon:Scissors,label:"ادیتور"},
    {id:"style",icon:Palette,label:"استایل"},
    {id:"ai",icon:Brain,label:"دستیار AI"},
    {id:"muscle",icon:Dumbbell,label:"عضلات"},
  ];

  return (
    <div className="h-screen w-screen bg-[#09090b] text-white flex flex-col overflow-hidden" dir="rtl">
      {/* Header */}
      <header className="h-12 bg-[#0f0f12] border-b border-white/5 flex items-center px-4 gap-3 shrink-0">
        <h1 className="text-sm font-bold bg-gradient-to-l from-indigo-400 to-purple-400 bg-clip-text text-transparent">✦ Cutting Edge v2.0</h1>
        <div className="flex-1"/>
        {panels.map(p => (
          <button key={p.id} onClick={()=>setPanel(p.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all ${panel===p.id?"bg-white/10 text-white":"text-white/40 hover:text-white/70"}`}>
            <p.icon className="w-3.5 h-3.5"/>{p.label}
          </button>
        ))}
        <div className="flex-1"/>
        <div className="flex items-center gap-1.5 text-[10px] text-white/30">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"/>Reheal فعال
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Video Area */}
        <div className="flex-1 flex flex-col bg-black/50">
          <div className="flex-1 flex items-center justify-center" onDragOver={e=>e.preventDefault()} onDrop={onDrop}>
            {videoSrc ? (
              <video ref={vRef} src={videoSrc} className="max-w-full max-h-full object-contain"
                onTimeUpdate={()=>vRef.current&&setTime(vRef.current.currentTime)}
                onLoadedMetadata={()=>setDur(vRef.current?.duration||0)}
                onEnded={()=>setPlaying(false)}/>
            ) : (
              <label className="flex flex-col items-center gap-4 p-12 border-2 border-dashed border-white/10 rounded-2xl cursor-pointer hover:border-indigo-500/50 transition-all group">
                <Upload className="w-12 h-12 text-white/20 group-hover:text-indigo-400"/>
                <span className="text-white/40 text-sm">ویدیو را بکشید و رها کنید</span>
                <input type="file" accept="video/*" className="hidden" onChange={onFile}/>
              </label>
            )}
          </div>
          {videoSrc && (
            <>
              <div className="h-14 bg-[#0f0f12] border-t border-white/5 flex items-center px-4 gap-3 shrink-0">
                <button onClick={()=>{if(vRef.current)vRef.current.currentTime=Math.max(0,time-5)}}><SkipBack className="w-4 h-4 text-white/50"/></button>
                <button onClick={toggle}>{playing?<Pause className="w-5 h-5 text-white"/>:<Play className="w-5 h-5 text-white fill-white"/>}</button>
                <button onClick={()=>{if(vRef.current)vRef.current.currentTime=Math.min(dur,time+5)}}><SkipForward className="w-4 h-4 text-white/50"/></button>
                <span className="text-xs text-white/40 font-mono w-24 text-center">{fmt(time)} / {fmt(dur)}</span>
                <input type="range" min={0} max={dur||100} value={time} onChange={e=>{if(vRef.current)vRef.current.currentTime=+e.target.value}} className="flex-1 h-1 accent-indigo-500"/>
                <Volume2 className="w-4 h-4 text-white/40"/><Maximize2 className="w-4 h-4 text-white/40"/>
              </div>
              <div className="h-16 bg-[#111114] border-t border-white/5 px-4 py-2 shrink-0">
                <div className="text-[10px] text-white/30 mb-1">Living Timeline</div>
                <div className="flex h-8 gap-[2px] items-end">
                  {Array.from({length:50},(_,i)=>{
                    const e=Math.sin(i*0.3)*0.3+0.5+Math.random()*0.2;
                    return <div key={i} className={`flex-1 rounded-t ${i/50<=time/(dur||1)?"bg-indigo-500":"bg-white/10"}`} style={{height:`${e*100}%`,opacity:0.4+e*0.6}}/>;
                  })}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Side Panel */}
        <AnimatePresence mode="wait">
          <motion.div key={panel} initial={{x:50,opacity:0}} animate={{x:0,opacity:1}} exit={{x:50,opacity:0}} transition={{duration:0.2}}
            className="w-80 bg-[#0f0f12] border-r border-white/5 flex flex-col shrink-0">
            <div className="p-4 border-b border-white/5"><h2 className="text-sm font-bold text-white/80">{panels.find(p=>p.id===panel)?.label}</h2></div>
            <div className="flex-1 overflow-y-auto p-4">
              {panel==="ai" && (
                <div className="flex flex-col h-full">
                  <div className="flex-1 space-y-3 mb-4 overflow-y-auto">
                    {msgs.map((m,i)=>(
                      <div key={i} className={`text-xs leading-relaxed p-2.5 rounded-lg ${m.r==="ai"?"bg-violet-500/10 text-violet-200 border border-violet-500/20":"bg-white/5 text-white/70"}`}>
                        {m.r==="ai"&&<span className="text-violet-400 text-[10px] block mb-1">🤖 AI</span>}{m.t}
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()}
                      placeholder="سؤالت رو بپرس..." className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-violet-500/50"/>
                    <button onClick={send} className="px-3 py-2 bg-violet-600 rounded-lg text-xs hover:bg-violet-500">ارسال</button>
                  </div>
                </div>
              )}
              {panel==="muscle" && (
                <div className="space-y-5">
                  <div><label className="text-xs text-white/50 block mb-2">شدت تعریف عضلات</label>
                    <input type="range" min={0} max={100} value={intensity} onChange={e=>setIntensity(+e.target.value)} className="w-full accent-orange-500"/>
                    <div className="text-xs text-orange-400 mt-1">{intensity}%</div></div>
                  {["Competition Ready","Natural Gym","Cinematic","Instagram"].map(p=>(
                    <button key={p} className="w-full text-right px-3 py-2.5 bg-white/5 hover:bg-white/10 rounded-lg text-xs text-white/70 border border-white/5 hover:border-orange-500/30">💪 {p}</button>
                  ))}
                  <button className="w-full py-3 bg-gradient-to-l from-orange-600 to-red-600 rounded-xl text-sm font-bold hover:opacity-90">✨ اعمال روی ویدیو</button>
                </div>
              )}
              {panel==="style" && (
                <div className="space-y-3">
                  <p className="text-xs text-white/40">ویدیوی مرجع را آپلود کنید:</p>
                  <label className="block p-6 border-2 border-dashed border-purple-500/20 rounded-xl text-center cursor-pointer hover:border-purple-500/50">
                    <Palette className="w-8 h-8 text-purple-400/50 mx-auto mb-2"/><span className="text-xs text-white/40">آپلود مرجع</span>
                    <input type="file" accept="video/*" className="hidden"/>
                  </label>
                  <div className="p-3 bg-purple-500/5 border border-purple-500/10 rounded-lg">
                    <div className="text-[10px] text-purple-300 mb-2">🧬 Mood DNA</div>
                    <div className="text-[10px] text-white/40 space-y-1"><div>انرژی: —</div><div>ریتم: —</div><div>رنگ: —</div></div>
                  </div>
                </div>
              )}
              {panel==="editor" && (
                <div className="space-y-3">
                  {[{i:"🎵",l:"Beat Sync خودکار",d:"کات روی ضرب آهنگ"},{i:"🎤",l:"فرمان صوتی",d:"ادیت با صدای فارسی"},
                    {i:"🎬",l:"One-Click Viral",d:"بهترین ۳۰ ثانیه"},{i:"🎨",l:"Emotion Color",d:"رنگ بر اساس احساس"}].map(x=>(
                    <button key={x.l} className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg border border-white/5 hover:border-indigo-500/30 text-right">
                      <span className="text-lg">{x.i}</span><div><div className="text-xs text-white/80">{x.l}</div><div className="text-[10px] text-white/30">{x.d}</div></div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      <footer className="h-6 bg-[#09090b] border-t border-white/5 flex items-center px-4 gap-4 text-[10px] text-white/30 shrink-0">
        <div className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500"/>Reheal Loop</div>
        <span>GTX 1650</span><span className="mr-auto">Ctrl+K: Command Palette</span>
      </footer>
    </div>
  );
}
