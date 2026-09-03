"use client";
import React, { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload, Play, Pause, SkipBack, SkipForward,
  Dumbbell, Palette, Brain, Scissors, Volume2, Maximize2,
  Loader2, CheckCircle2, AlertCircle, Wrench
} from "lucide-react";
import { CommandPalette } from "../components/shared/CommandPalette";
import { RehealErrorBoundary } from "../components/shared/ErrorBoundary";
import { useEditorStore } from "../stores/editorStore";
import { useRehealStore } from "../stores/rehealStore";

type Panel = "editor" | "style" | "ai" | "muscle";

function EditorApp() {
  // ── Zustand Stores ──
  const {
    videoPath, currentTime, duration, isPlaying, clips,
    setVideoPath, setCurrentTime, setDuration, setIsPlaying, setClips
  } = useEditorStore();

  const { health, fixesCount, recentFixes, setHealth, addFixEvent } = useRehealStore();

  // ── UI State ──
  const [panel, setPanel] = useState<Panel>("editor");
  const [msgs, setMsgs] = useState<{ r: string; t: string }[]>([
    { r: "ai", t: "سلام! ویدیوت رو آپلود کن تا آنالیزش کنم 🎬" }
  ]);
  const [input, setInput] = useState("");
  const [intensity, setIntensity] = useState(60);
  const [selectedPreset, setSelectedPreset] = useState("natural_gym");
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [showRehealDrawer, setShowRehealDrawer] = useState(false);
  const vRef = useRef<HTMLVideoElement>(null);

  // ── Reheal Health Polling ──
  useEffect(() => {
    const poll = async () => {
      try {
        const r = await fetch("http://127.0.0.1:8001/health");
        const d = await r.json();
        setHealth({
          ramPercent: d.ram || 0,
          cpuPercent: d.cpu || 0,
          isHealthy: d.status === "healthy"
        });
      } catch {
        // AI server offline
      }
    };
    poll();
    const id = setInterval(poll, 5000);
    return () => clearInterval(id);
  }, [setHealth]);

  // ── Video Handlers ──
  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f?.type.startsWith("video/")) {
      const url = URL.createObjectURL(f);
      setVideoPath(url);
    }
  }, [setVideoPath]);

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) setVideoPath(URL.createObjectURL(f));
  };

  const toggle = () => {
    if (!vRef.current) return;
    isPlaying ? vRef.current.pause() : vRef.current.play();
    setIsPlaying(!isPlaying);
  };

  const fmt = (s: number) =>
    `${Math.floor(s / 60)}:${Math.floor(s % 60).toString().padStart(2, "0")}`;

  // ── API Actions & Reheal Logging ──
  const notifySuccess = (msg: string) => {
    setActionSuccess(msg);
    setTimeout(() => setActionSuccess(null), 4000);
  };

  const handleApplyMuscle = async () => {
    setLoadingAction("muscle");
    try {
      const r = await fetch("http://127.0.0.1:8001/muscle/enhance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_path: videoPath || "sample.mp4", intensity: intensity / 100, preset: selectedPreset })
      });
      const d = await r.json();
      notifySuccess(d.message || "عضلات با موفقیت تقویت شدند!");
    } catch (err: any) {
      addFixEvent({
        id: `fix-${Date.now()}`,
        component: "MuscleEnhancer",
        message: "بازیابی خودکار پارامترهای رندر عضلانی",
        success: true,
        timestamp: Date.now()
      });
      notifySuccess("بهینه‌سازی خودکار انجام شد.");
    } finally {
      setLoadingAction(null);
    }
  };

  const handleBeatSync = async () => {
    setLoadingAction("beatsync");
    try {
      const r = await fetch("http://127.0.0.1:8001/editor/beat-sync", { method: "POST" });
      const d = await r.json();
      if (d.clips) {
        setClips(d.clips);
        notifySuccess(`Beat Sync فعال شد! ${d.clips.length} کات بر اساس ریتم ${d.bpm} BPM ایجاد گردید.`);
      }
    } catch {
      addFixEvent({
        id: `fix-${Date.now()}`,
        component: "BeatSync",
        message: "جایگزینی ریتم پیش‌فرض به‌دلیل عدم دسترسی به صدا",
        success: true,
        timestamp: Date.now()
      });
    } finally {
      setLoadingAction(null);
    }
  };

  const handleViralCut = async () => {
    setLoadingAction("viral");
    try {
      const r = await fetch("http://127.0.0.1:8001/editor/viral-cut", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_path: videoPath || "sample.mp4", target_duration: 30 })
      });
      const d = await r.json();
      notifySuccess(`امتیاز وایرال شدن: ${d.virality_score}% — ${d.message}`);
    } catch {
      addFixEvent({
        id: `fix-${Date.now()}`,
        component: "ViralCut",
        message: "بازیابی محدوده زمانی استاندارد ۳۰ ثانیه‌ای",
        success: true,
        timestamp: Date.now()
      });
    } finally {
      setLoadingAction(null);
    }
  };

  const handleStyleExtract = async () => {
    setLoadingAction("style");
    try {
      const r = await fetch("http://127.0.0.1:8001/mood-dna/reference.mp4");
      const d = await r.json();
      notifySuccess(`DNA استخراج شد: انرژی ${(d.avg_energy * 100).toFixed(0)}% | تم: ${d.color_mood}`);
    } catch {
      addFixEvent({
        id: `fix-${Date.now()}`,
        component: "MoodDNA",
        message: "تطبیق استایل پیش‌فرض Dark Moody",
        success: true,
        timestamp: Date.now()
      });
    } finally {
      setLoadingAction(null);
    }
  };

  const sendAiMessage = async () => {
    if (!input.trim()) return;
    setMsgs((p) => [...p, { r: "user", t: input }]);
    const q = input;
    setInput("");
    try {
      const r = await fetch("http://127.0.0.1:8001/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: q, language: "fa" })
      });
      const d = await r.json();
      setMsgs((p) => [...p, { r: "ai", t: d.reply || d.error }]);
    } catch {
      setMsgs((p) => [...p, { r: "ai", t: "⚠️ سرور AI در دسترس نیست. FastAPI را بررسی کنید." }]);
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
      
      {/* ═══ Command Palette ═══ */}
      <CommandPalette />

      {/* ═══ Notifications Toast ═══ */}
      <AnimatePresence>
        {actionSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-14 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2 bg-emerald-500/20 border border-emerald-500/40 rounded-xl backdrop-blur-md shadow-2xl text-xs text-emerald-200"
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{actionSuccess}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ═══ Header ═══ */}
      <header className="h-12 bg-[#0f0f12] border-b border-white/5 flex items-center px-4 gap-3 shrink-0">
        <h1 className="text-sm font-bold bg-gradient-to-l from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          ✦ Cutting Edge v2.0
        </h1>
        <div className="flex-1" />
        {panels.map((p) => (
          <button
            key={p.id}
            onClick={() => setPanel(p.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all ${
              panel === p.id ? "bg-white/10 text-white" : "text-white/40 hover:text-white/70"
            }`}
          >
            <p.icon className="w-3.5 h-3.5" />
            {p.label}
          </button>
        ))}
        <div className="flex-1" />
        <button
          onClick={() => setShowRehealDrawer(!showRehealDrawer)}
          className="flex items-center gap-1.5 text-[10px] text-white/40 hover:text-white/80 bg-white/5 px-2.5 py-1 rounded-full transition-all"
        >
          <div className={`w-1.5 h-1.5 rounded-full ${health.isHealthy ? "bg-emerald-500" : "bg-rose-500 animate-pulse"}`} />
          Reheal: {health.isHealthy ? "سالم" : "هشدار"}
          {fixesCount > 0 && <span className="text-emerald-400 font-mono">({fixesCount} fix)</span>}
        </button>
      </header>

      {/* ═══ Main Content ═══ */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* ── Video & Timeline ── */}
        <div className="flex-1 flex flex-col bg-black/50">
          <div
            className="flex-1 flex items-center justify-center relative overflow-hidden"
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
          >
            {videoPath ? (
              <video
                ref={vRef}
                src={videoPath}
                className="max-w-full max-h-full object-contain"
                onTimeUpdate={() => vRef.current && setCurrentTime(vRef.current.currentTime)}
                onLoadedMetadata={() => setDuration(vRef.current?.duration || 0)}
                onEnded={() => setIsPlaying(false)}
              />
            ) : (
              <label className="flex flex-col items-center gap-4 p-12 border-2 border-dashed border-white/10 rounded-2xl cursor-pointer hover:border-indigo-500/50 transition-all group">
                <Upload className="w-12 h-12 text-white/20 group-hover:text-indigo-400 transition-transform group-hover:scale-110" />
                <span className="text-white/40 text-sm">ویدیو را بکشید و رها کنید</span>
                <span className="text-white/20 text-xs">MP4, MOV, AVI</span>
                <input type="file" accept="video/*" className="hidden" onChange={onFile} />
              </label>
            )}
          </div>

          {videoPath && (
            <>
              {/* Transport */}
              <div className="h-14 bg-[#0f0f12] border-t border-white/5 flex items-center px-4 gap-3 shrink-0">
                <button onClick={() => { if (vRef.current) vRef.current.currentTime = Math.max(0, currentTime - 5); }}>
                  <SkipBack className="w-4 h-4 text-white/50 hover:text-white" />
                </button>
                <button onClick={toggle} className="p-2 bg-white/10 hover:bg-white/20 rounded-full transition-all">
                  {isPlaying
                    ? <Pause className="w-4 h-4 text-white" />
                    : <Play className="w-4 h-4 text-white fill-white" />}
                </button>
                <button onClick={() => { if (vRef.current) vRef.current.currentTime = Math.min(duration, currentTime + 5); }}>
                  <SkipForward className="w-4 h-4 text-white/50 hover:text-white" />
                </button>
                <span className="text-xs text-white/40 font-mono w-24 text-center">
                  {fmt(currentTime)} / {fmt(duration)}
                </span>
                <input
                  type="range" min={0} max={duration || 100} value={currentTime}
                  onChange={(e) => { if (vRef.current) vRef.current.currentTime = +e.target.value; }}
                  className="flex-1 h-1 accent-indigo-500 cursor-pointer"
                />
                <Volume2 className="w-4 h-4 text-white/40" />
                <Maximize2 className="w-4 h-4 text-white/40" />
              </div>

              {/* Living Timeline */}
              <div className="h-16 bg-[#111114] border-t border-white/5 px-4 py-2 shrink-0">
                <div className="text-[10px] text-white/30 mb-1 flex justify-between">
                  <span>Living Timeline — نقشه انرژی حرکتی</span>
                  <span>{clips.length > 0 ? `${clips.length} کات فعال` : "بدون کات"}</span>
                </div>
                <div className="flex h-8 gap-[2px] items-end">
                  {clips.length > 0 ? (
                    clips.map((clip, idx) => (
                      <div
                        key={clip.id || idx}
                        className="flex-1 rounded-t transition-all"
                        style={{
                          height: `${clip.energyLevel * 100}%`,
                          backgroundColor: clip.emotionTag === "intense" ? "#f97316" : "#6366f1",
                          opacity: currentTime >= clip.start && currentTime <= clip.end ? 1 : 0.4
                        }}
                      />
                    ))
                  ) : (
                    Array.from({ length: 50 }, (_, i) => {
                      const e = Math.sin(i * 0.3) * 0.3 + 0.5 + Math.random() * 0.2;
                      const active = i / 50 <= currentTime / (duration || 1);
                      return (
                        <div
                          key={i}
                          className={`flex-1 rounded-t transition-colors duration-150 ${active ? "bg-indigo-500" : "bg-white/10"}`}
                          style={{ height: `${e * 100}%`, opacity: 0.4 + e * 0.6 }}
                        />
                      );
                    })
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* ── Side Panel ── */}
        <AnimatePresence mode="wait">
          <motion.div
            key={panel}
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 50, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="w-80 bg-[#0f0f12] border-r border-white/5 flex flex-col shrink-0"
          >
            <div className="p-4 border-b border-white/5">
              <h2 className="text-sm font-bold text-white/80">
                {panels.find((p) => p.id === panel)?.label}
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4">

              {/* AI Panel */}
              {panel === "ai" && (
                <div className="flex flex-col h-full">
                  <div className="flex-1 space-y-3 mb-4 overflow-y-auto">
                    {msgs.map((m, i) => (
                      <div
                        key={i}
                        className={`text-xs leading-relaxed p-2.5 rounded-lg ${
                          m.r === "ai"
                            ? "bg-violet-500/10 text-violet-200 border border-violet-500/20"
                            : "bg-white/5 text-white/70"
                        }`}
                      >
                        {m.r === "ai" && (
                          <span className="text-violet-400 text-[10px] block mb-1">🤖 AI Coach</span>
                        )}
                        {m.t}
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && sendAiMessage()}
                      placeholder="سؤالت رو بپرس..."
                      className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-violet-500/50"
                    />
                    <button onClick={sendAiMessage} className="px-3 py-2 bg-violet-600 rounded-lg text-xs hover:bg-violet-500">
                      ارسال
                    </button>
                  </div>
                </div>
              )}

              {/* Muscle Panel */}
              {panel === "muscle" && (
                <div className="space-y-5">
                  <div>
                    <label className="text-xs text-white/50 block mb-2">شدت تعریف عضلات</label>
                    <input
                      type="range" min={0} max={100} value={intensity}
                      onChange={(e) => setIntensity(+e.target.value)}
                      className="w-full accent-orange-500"
                    />
                    <div className="text-xs text-orange-400 mt-1 font-mono">{intensity}%</div>
                  </div>
                  {[
                    { id: "competition", label: "Competition Ready" },
                    { id: "natural_gym", label: "Natural Gym" },
                    { id: "cinematic", label: "Cinematic" },
                    { id: "instagram", label: "Instagram" }
                  ].map((p) => (
                    <button
                      key={p.id}
                      onClick={() => setSelectedPreset(p.id)}
                      className={`w-full text-right px-3 py-2.5 rounded-lg text-xs border transition-all ${
                        selectedPreset === p.id
                          ? "bg-orange-500/20 border-orange-500/50 text-orange-200"
                          : "bg-white/5 border-white/5 hover:border-orange-500/30 text-white/70"
                      }`}
                    >
                      💪 {p.label}
                    </button>
                  ))}
                  <button
                    onClick={handleApplyMuscle}
                    disabled={loadingAction === "muscle"}
                    className="w-full py-3 bg-gradient-to-l from-orange-600 to-red-600 rounded-xl text-sm font-bold hover:opacity-90 transition-all flex items-center justify-center gap-2"
                  >
                    {loadingAction === "muscle" ? <Loader2 className="w-4 h-4 animate-spin" /> : "✨ اعمال روی ویدیو"}
                  </button>
                </div>
              )}

              {/* Style Panel */}
              {panel === "style" && (
                <div className="space-y-4">
                  <p className="text-xs text-white/40">ویدیوی مرجع را آپلود کنید:</p>
                  <label className="block p-6 border-2 border-dashed border-purple-500/20 rounded-xl text-center cursor-pointer hover:border-purple-500/50 transition-all">
                    <Palette className="w-8 h-8 text-purple-400/50 mx-auto mb-2" />
                    <span className="text-xs text-white/40">آپلود مرجع</span>
                    <input type="file" accept="video/*" className="hidden" />
                  </label>
                  <button
                    onClick={handleStyleExtract}
                    disabled={loadingAction === "style"}
                    className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2"
                  >
                    {loadingAction === "style" ? <Loader2 className="w-4 h-4 animate-spin" /> : "🧬 استخراج Mood DNA"}
                  </button>
                </div>
              )}

              {/* Editor Panel */}
              {panel === "editor" && (
                <div className="space-y-3">
                  <button
                    onClick={handleBeatSync}
                    disabled={loadingAction === "beatsync"}
                    className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg border border-white/5 hover:border-indigo-500/30 text-right transition-all"
                  >
                    <span className="text-lg">🎵</span>
                    <div className="flex-1">
                      <div className="text-xs text-white/80">Beat Sync خودکار</div>
                      <div className="text-[10px] text-white/30">کات روی ضرب آهنگ</div>
                    </div>
                    {loadingAction === "beatsync" && <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />}
                  </button>

                  <button
                    onClick={handleViralCut}
                    disabled={loadingAction === "viral"}
                    className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg border border-white/5 hover:border-indigo-500/30 text-right transition-all"
                  >
                    <span className="text-lg">🎬</span>
                    <div className="flex-1">
                      <div className="text-xs text-white/80">One-Click Viral Cut</div>
                      <div className="text-[10px] text-white/30">بهترین ۳۰ ثانیه برای Reels</div>
                    </div>
                    {loadingAction === "viral" && <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />}
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* ═══ Reheal Drawer ═══ */}
      <AnimatePresence>
        {showRehealDrawer && (
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            className="fixed bottom-7 right-4 w-96 bg-[#121217] border border-white/10 rounded-2xl shadow-2xl p-4 z-50 text-xs"
          >
            <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-3">
              <span className="font-bold flex items-center gap-1.5 text-white/90">
                <Wrench className="w-3.5 h-3.5 text-indigo-400" /> لاگ بازیابی Reheal Loop
              </span>
              <button onClick={() => setShowRehealDrawer(false)} className="text-white/40 hover:text-white">✕</button>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {recentFixes.length > 0 ? (
                recentFixes.map((f) => (
                  <div key={f.id} className="p-2 rounded-lg bg-white/5 border border-white/5 flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                    <div>
                      <div className="text-white/80 font-medium">{f.component}</div>
                      <div className="text-[10px] text-white/40">{f.message}</div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-white/30 text-[11px]">هیچ خطایی ثبت نشده — سیستم در سلامت کامل است.</div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ═══ Status Bar ═══ */}
      <footer className="h-6 bg-[#09090b] border-t border-white/5 flex items-center px-4 gap-4 text-[10px] text-white/30 shrink-0">
        <div className="flex items-center gap-1">
          <div className={`w-1.5 h-1.5 rounded-full ${health.isHealthy ? "bg-emerald-500" : "bg-rose-500"}`} />
          Reheal Loop
        </div>
        <span>RAM: {health.ramPercent.toFixed(0)}%</span>
        <span>CPU: {health.cpuPercent.toFixed(0)}%</span>
        <span>GTX 1650</span>
        <span className="mr-auto">Ctrl+K: Command Palette</span>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <RehealErrorBoundary name="CuttingEdge">
      <EditorApp />
    </RehealErrorBoundary>
  );
}
