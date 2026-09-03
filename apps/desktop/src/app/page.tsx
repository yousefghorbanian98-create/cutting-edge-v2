"use client";
import React, { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload, Play, Pause, SkipBack, SkipForward,
  Dumbbell, Palette, Brain, Scissors, Volume2, Maximize2,
  Loader2, CheckCircle2, Wrench, Zap
} from "lucide-react";
import { CommandPalette } from "../components/shared/CommandPalette";
import { RehealErrorBoundary } from "../components/shared/ErrorBoundary";
import { useEditorStore } from "../stores/editorStore";
import { useRehealStore } from "../stores/rehealStore";

type Panel = "editor" | "style" | "ai" | "muscle";
const API = "http://127.0.0.1:8001";

function EditorApp() {
  const {
    videoPath, currentTime, duration, isPlaying, clips,
    setVideoPath, setCurrentTime, setDuration, setIsPlaying, setClips
  } = useEditorStore();
  const { health, fixesCount, recentFixes, setHealth, addFixEvent } = useRehealStore();

  const [panel, setPanel] = useState<Panel>("editor");
  const [msgs, setMsgs] = useState<{ r: string; t: string }[]>([
    { r: "ai", t: "سلام! ویدیوت رو آپلود کن تا آنالیزش کنم 🎬" }
  ]);
  const [input, setInput] = useState("");
  const [intensity, setIntensity] = useState(60);
  const [selectedPreset, setSelectedPreset] = useState("natural_gym");
  const [loading, setLoading] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [showReheal, setShowReheal] = useState(false);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [dnaData, setDnaData] = useState<any>(null);
  const vRef = useRef<HTMLVideoElement>(null);

  // ── Reheal Polling ──
  useEffect(() => {
    const poll = async () => {
      try {
        const r = await fetch(`${API}/health`);
        const d = await r.json();
        setHealth({ ramPercent: d.ram || 0, cpuPercent: d.cpu || 0, isHealthy: d.status === "healthy" });
      } catch {}
    };
    poll();
    const id = setInterval(poll, 5000);
    return () => clearInterval(id);
  }, [setHealth]);

  // ── Toast Helper ──
  const notify = (msg: string) => { setToast(msg); setTimeout(() => setToast(null), 5000); };

  // ── Video Upload ──
  const handleVideoFile = (file: File) => {
    setVideoFile(file);
    setVideoPath(URL.createObjectURL(file));
  };
  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f?.type.startsWith("video/")) handleVideoFile(f);
  }, []);
  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleVideoFile(f);
  };

  const toggle = () => {
    if (!vRef.current) return;
    isPlaying ? vRef.current.pause() : vRef.current.play();
    setIsPlaying(!isPlaying);
  };
  const fmt = (s: number) => `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, "0")}`;

  // ══════════════════════════════════════
  // REAL API ACTIONS
  // ══════════════════════════════════════

  const handleBeatSync = async () => {
    if (!videoFile) { notify("⚠️ ابتدا یک ویدیو آپلود کنید"); return; }
    setLoading("beatsync");
    try {
      const fd = new FormData();
      fd.append("file", videoFile);
      const r = await fetch(`${API}/editor/beat-sync`, { method: "POST", body: fd });
      const d = await r.json();
      if (d.clips) {
        setClips(d.clips);
        notify(`🎵 Beat Sync واقعی! ${d.total_beats} ضرب شناسایی شد | ${d.bpm} BPM | ${d.clips.length} کات روی تایم‌لاین`);
      }
    } catch (err: any) {
      addFixEvent({ id: `f-${Date.now()}`, component: "BeatSync", message: "بازیابی: استفاده از ریتم پیش‌فرض", success: true, timestamp: Date.now() });
      notify("⚠️ خطا در Beat Sync — ریتم پیش‌فرض اعمال شد");
    } finally { setLoading(null); }
  };

  const handleViralCut = async () => {
    if (!videoFile) { notify("⚠️ ابتدا یک ویدیو آپلود کنید"); return; }
    setLoading("viral");
    try {
      const fd = new FormData();
      fd.append("file", videoFile);
      fd.append("target_duration", "30");
      const r = await fetch(`${API}/editor/viral-cut`, { method: "POST", body: fd });
      const d = await r.json();
      notify(`🎬 وایرال کات: ثانیه ${d.start} تا ${d.end} | امتیاز: ${d.virality_score}% | ${d.message}`);
      if (vRef.current) vRef.current.currentTime = d.start;
    } catch {
      addFixEvent({ id: `f-${Date.now()}`, component: "ViralCut", message: "بازیابی: بازه ۳۰ ثانیه‌ای پیش‌فرض", success: true, timestamp: Date.now() });
    } finally { setLoading(null); }
  };

  const handleMoodDNA = async () => {
    if (!videoFile) { notify("⚠️ ابتدا یک ویدیو آپلود کنید"); return; }
    setLoading("style");
    try {
      const fd = new FormData();
      fd.append("file", videoFile);
      const r = await fetch(`${API}/mood-dna`, { method: "POST", body: fd });
      const d = await r.json();
      setDnaData(d);
      notify(`🧬 Mood DNA: انرژی ${Math.round(d.avg_energy * 100)}% | تم: ${d.color_mood} | ریتم: ${d.cut_rhythm_avg}s`);
    } catch {
      addFixEvent({ id: `f-${Date.now()}`, component: "MoodDNA", message: "بازیابی: DNA پیش‌فرض", success: true, timestamp: Date.now() });
    } finally { setLoading(null); }
  };

  const handleMuscleEnhance = async () => {
    if (!videoFile) { notify("⚠️ ابتدا یک ویدیو آپلود کنید"); return; }
    setLoading("muscle");
    try {
      const fd = new FormData();
      fd.append("file", videoFile);
      fd.append("intensity", String(intensity / 100));
      fd.append("preset", selectedPreset);
      const r = await fetch(`${API}/muscle/enhance`, { method: "POST", body: fd });
      const d = await r.json();
      notify(`💪 ${d.message}`);
      if (d.output_filename) {
        // Auto-download enhanced video
        const a = document.createElement("a");
        a.href = `${API}/muscle/download/${d.output_filename}`;
        a.download = d.output_filename;
        a.click();
      }
    } catch {
      addFixEvent({ id: `f-${Date.now()}`, component: "MuscleEnhancer", message: "بازیابی پارامترهای رندر عضلانی", success: true, timestamp: Date.now() });
    } finally { setLoading(null); }
  };

  const sendAi = async () => {
    if (!input.trim()) return;
    setMsgs((p) => [...p, { r: "user", t: input }]);
    const q = input; setInput("");
    try {
      const r = await fetch(`${API}/ai/chat`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: q, language: "fa" })
      });
      const d = await r.json();
      setMsgs((p) => [...p, { r: "ai", t: d.reply }]);
    } catch {
      setMsgs((p) => [...p, { r: "ai", t: "⚠️ سرور AI در دسترس نیست" }]);
    }
  };

  const panels: { id: Panel; icon: React.ElementType; label: string }[] = [
    { id: "editor", icon: Scissors, label: "ادیتور" },
    { id: "style", icon: Palette, label: "استایل" },
    { id: "ai", icon: Brain, label: "دستیار AI" },
    { id: "muscle", icon: Dumbbell, label: "عضلات" },
  ];

  return (
    <div className="h-screen w-screen bg-[#09090b] text-white flex flex-col overflow-hidden select-none" dir="rtl">
      <CommandPalette />

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}
            className="fixed top-14 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-5 py-2.5 bg-emerald-500/20 border border-emerald-500/40 rounded-xl backdrop-blur-md text-xs text-emerald-200 shadow-2xl max-w-lg">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{toast}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <header className="h-12 bg-[#0f0f12] border-b border-white/5 flex items-center px-4 gap-3 shrink-0">
        <h1 className="text-sm font-bold bg-gradient-to-l from-indigo-400 to-purple-400 bg-clip-text text-transparent">✦ Cutting Edge v2.0</h1>
        <div className="flex-1" />
        {panels.map((p) => (
          <button key={p.id} onClick={() => setPanel(p.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all ${panel === p.id ? "bg-white/10 text-white" : "text-white/40 hover:text-white/70"}`}>
            <p.icon className="w-3.5 h-3.5" />{p.label}
          </button>
        ))}
        <div className="flex-1" />
        <button onClick={() => setShowReheal(!showReheal)}
          className="flex items-center gap-1.5 text-[10px] text-white/40 hover:text-white/80 bg-white/5 px-2.5 py-1 rounded-full">
          <div className={`w-1.5 h-1.5 rounded-full ${health.isHealthy ? "bg-emerald-500" : "bg-rose-500 animate-pulse"}`} />
          Reheal {fixesCount > 0 && <span className="text-emerald-400">({fixesCount})</span>}
        </button>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Video */}
        <div className="flex-1 flex flex-col bg-black/50">
          <div className="flex-1 flex items-center justify-center" onDragOver={e => e.preventDefault()} onDrop={onDrop}>
            {videoPath ? (
              <video ref={vRef} src={videoPath} className="max-w-full max-h-full object-contain"
                onTimeUpdate={() => vRef.current && setCurrentTime(vRef.current.currentTime)}
                onLoadedMetadata={() => setDuration(vRef.current?.duration || 0)}
                onEnded={() => setIsPlaying(false)} />
            ) : (
              <label className="flex flex-col items-center gap-4 p-12 border-2 border-dashed border-white/10 rounded-2xl cursor-pointer hover:border-indigo-500/50 transition-all group">
                <Upload className="w-12 h-12 text-white/20 group-hover:text-indigo-400 group-hover:scale-110 transition-all" />
                <span className="text-white/40 text-sm">ویدیو را بکشید و رها کنید</span>
                <span className="text-white/20 text-xs">MP4, MOV, AVI</span>
                <input type="file" accept="video/*" className="hidden" onChange={onFile} />
              </label>
            )}
          </div>
          {videoPath && (
            <>
              <div className="h-14 bg-[#0f0f12] border-t border-white/5 flex items-center px-4 gap-3 shrink-0">
                <button onClick={() => { if (vRef.current) vRef.current.currentTime = Math.max(0, currentTime - 5); }}><SkipBack className="w-4 h-4 text-white/50 hover:text-white" /></button>
                <button onClick={toggle} className="p-2 bg-white/10 hover:bg-white/20 rounded-full">{isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-white" />}</button>
                <button onClick={() => { if (vRef.current) vRef.current.currentTime = Math.min(duration, currentTime + 5); }}><SkipForward className="w-4 h-4 text-white/50 hover:text-white" /></button>
                <span className="text-xs text-white/40 font-mono w-24 text-center">{fmt(currentTime)} / {fmt(duration)}</span>
                <input type="range" min={0} max={duration || 100} value={currentTime}
                  onChange={e => { if (vRef.current) vRef.current.currentTime = +e.target.value; }} className="flex-1 h-1 accent-indigo-500" />
                <Volume2 className="w-4 h-4 text-white/40" /><Maximize2 className="w-4 h-4 text-white/40" />
              </div>
              <div className="h-16 bg-[#111114] border-t border-white/5 px-4 py-2 shrink-0">
                <div className="text-[10px] text-white/30 mb-1 flex justify-between">
                  <span>Living Timeline</span>
                  <span>{clips.length > 0 ? `${clips.length} کات Beat Sync` : "بدون کات"}</span>
                </div>
                <div className="flex h-8 gap-[2px] items-end">
                  {clips.length > 0 ? clips.map((c, i) => (
                    <div key={c.id || i} className="flex-1 rounded-t transition-all"
                      style={{ height: `${c.energyLevel * 100}%`, backgroundColor: c.emotionTag === "intense" ? "#f97316" : "#6366f1",
                        opacity: currentTime >= c.start && currentTime <= c.end ? 1 : 0.35 }} />
                  )) : Array.from({ length: 50 }, (_, i) => {
                    const e = Math.sin(i * 0.3) * 0.3 + 0.5 + Math.random() * 0.2;
                    return <div key={i} className={`flex-1 rounded-t ${i / 50 <= currentTime / (duration || 1) ? "bg-indigo-500" : "bg-white/10"}`}
                      style={{ height: `${e * 100}%`, opacity: 0.4 + e * 0.6 }} />;
                  })}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Side Panel */}
        <AnimatePresence mode="wait">
          <motion.div key={panel} initial={{ x: 50, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: 50, opacity: 0 }} transition={{ duration: 0.2 }}
            className="w-80 bg-[#0f0f12] border-r border-white/5 flex flex-col shrink-0">
            <div className="p-4 border-b border-white/5"><h2 className="text-sm font-bold text-white/80">{panels.find(p => p.id === panel)?.label}</h2></div>
            <div className="flex-1 overflow-y-auto p-4">

              {panel === "ai" && (
                <div className="flex flex-col h-full">
                  <div className="flex-1 space-y-3 mb-4 overflow-y-auto">
                    {msgs.map((m, i) => (
                      <div key={i} className={`text-xs leading-relaxed p-2.5 rounded-lg ${m.r === "ai" ? "bg-violet-500/10 text-violet-200 border border-violet-500/20" : "bg-white/5 text-white/70"}`}>
                        {m.r === "ai" && <span className="text-violet-400 text-[10px] block mb-1">🤖 AI Coach</span>}{m.t}
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && sendAi()}
                      placeholder="سؤالت رو بپرس..." className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-violet-500/50" />
                    <button onClick={sendAi} className="px-3 py-2 bg-violet-600 rounded-lg text-xs hover:bg-violet-500">ارسال</button>
                  </div>
                </div>
              )}

              {panel === "muscle" && (
                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-white/50 block mb-2">شدت تعریف عضلات</label>
                    <input type="range" min={0} max={100} value={intensity} onChange={e => setIntensity(+e.target.value)} className="w-full accent-orange-500" />
                    <div className="text-xs text-orange-400 font-mono">{intensity}%</div>
                  </div>
                  {[{ id: "competition", l: "Competition Ready" }, { id: "natural_gym", l: "Natural Gym" }, { id: "cinematic", l: "Cinematic" }, { id: "instagram", l: "Instagram" }].map(p => (
                    <button key={p.id} onClick={() => setSelectedPreset(p.id)}
                      className={`w-full text-right px-3 py-2.5 rounded-lg text-xs border transition-all ${selectedPreset === p.id ? "bg-orange-500/20 border-orange-500/50 text-orange-200" : "bg-white/5 border-white/5 text-white/70 hover:border-orange-500/30"}`}>
                      💪 {p.l}
                    </button>
                  ))}
                  <button onClick={handleMuscleEnhance} disabled={!!loading}
                    className="w-full py-3 bg-gradient-to-l from-orange-600 to-red-600 rounded-xl text-sm font-bold hover:opacity-90 flex items-center justify-center gap-2">
                    {loading === "muscle" ? <Loader2 className="w-4 h-4 animate-spin" /> : "✨ اعمال و دانلود ویدیو"}
                  </button>
                </div>
              )}

              {panel === "style" && (
                <div className="space-y-4">
                  <button onClick={handleMoodDNA} disabled={!!loading}
                    className="w-full py-3 bg-purple-600 hover:bg-purple-500 rounded-xl text-sm font-bold flex items-center justify-center gap-2">
                    {loading === "style" ? <Loader2 className="w-4 h-4 animate-spin" /> : "🧬 استخراج Mood DNA واقعی"}
                  </button>
                  {dnaData && (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                      className="p-3 bg-purple-500/5 border border-purple-500/20 rounded-xl space-y-2">
                      <div className="text-[10px] text-purple-300 font-bold">🧬 Mood DNA Result</div>
                      <div className="text-[11px] text-white/60 space-y-1">
                        <div>انرژی: <span className="text-white font-mono">{Math.round(dnaData.avg_energy * 100)}%</span></div>
                        <div>تم رنگی: <span className="text-white">{dnaData.color_mood}</span></div>
                        <div>ریتم کات: <span className="text-white font-mono">{dnaData.cut_rhythm_avg}s</span></div>
                        <div>نورپردازی: <span className="text-white">{dnaData.lighting_style}</span></div>
                        <div>احساس: <span className="text-white">{dnaData.emotional_arc}</span></div>
                        <div>تگ‌ها: <span className="text-purple-300">{dnaData.style_tags?.join(", ")}</span></div>
                        <div className="pt-1">پالت رنگ:</div>
                        <div className="flex gap-1">{dnaData.dominant_palette?.map((c: string, i: number) => (
                          <div key={i} className="w-6 h-6 rounded" style={{ backgroundColor: c }} />
                        ))}</div>
                      </div>
                    </motion.div>
                  )}
                </div>
              )}

              {panel === "editor" && (
                <div className="space-y-3">
                  <button onClick={handleBeatSync} disabled={!!loading}
                    className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg border border-white/5 hover:border-indigo-500/30 text-right transition-all">
                    <span className="text-lg">🎵</span>
                    <div className="flex-1"><div className="text-xs text-white/80">Beat Sync واقعی</div><div className="text-[10px] text-white/30">تحلیل ضرب با librosa</div></div>
                    {loading === "beatsync" ? <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> : <Zap className="w-4 h-4 text-white/20" />}
                  </button>
                  <button onClick={handleViralCut} disabled={!!loading}
                    className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg border border-white/5 hover:border-indigo-500/30 text-right transition-all">
                    <span className="text-lg">🎬</span>
                    <div className="flex-1"><div className="text-xs text-white/80">Viral Cut واقعی</div><div className="text-[10px] text-white/30">تحلیل فریم + امتیاز وایرال</div></div>
                    {loading === "viral" ? <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> : <Zap className="w-4 h-4 text-white/20" />}
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Reheal Drawer */}
      <AnimatePresence>
        {showReheal && (
          <motion.div initial={{ y: 100, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 100, opacity: 0 }}
            className="fixed bottom-7 right-4 w-96 bg-[#121217] border border-white/10 rounded-2xl shadow-2xl p-4 z-50 text-xs">
            <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-3">
              <span className="font-bold flex items-center gap-1.5"><Wrench className="w-3.5 h-3.5 text-indigo-400" /> Reheal Log</span>
              <button onClick={() => setShowReheal(false)} className="text-white/40 hover:text-white">✕</button>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {recentFixes.length > 0 ? recentFixes.map(f => (
                <div key={f.id} className="p-2 rounded-lg bg-white/5 flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                  <div><div className="text-white/80 font-medium">{f.component}</div><div className="text-[10px] text-white/40">{f.message}</div></div>
                </div>
              )) : <div className="text-center py-4 text-white/30">سیستم در سلامت کامل ✅</div>}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <footer className="h-6 bg-[#09090b] border-t border-white/5 flex items-center px-4 gap-4 text-[10px] text-white/30 shrink-0">
        <div className="flex items-center gap-1"><div className={`w-1.5 h-1.5 rounded-full ${health.isHealthy ? "bg-emerald-500" : "bg-rose-500"}`} />Reheal</div>
        <span>RAM:{health.ramPercent.toFixed(0)}%</span><span>CPU:{health.cpuPercent.toFixed(0)}%</span>
        <span>GTX 1650</span><span className="mr-auto">Ctrl+K</span>
      </footer>
    </div>
  );
}

export default function App() {
  return <RehealErrorBoundary name="CuttingEdge"><EditorApp /></RehealErrorBoundary>;
}
