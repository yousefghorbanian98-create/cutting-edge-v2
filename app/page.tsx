'use client';

import { useRef, useState } from 'react';
import {
  Activity, Aperture, ArrowUpRight, Bot, ChevronDown, Clock3, Film,
  FolderOpen, Gauge, Grid2X2, HelpCircle, LayoutTemplate, Menu, Mic2,
  MoreHorizontal, Play, Plus, Search, Settings, Sparkles, Upload,
  WandSparkles, Waves, X, Zap
} from 'lucide-react';

const clips = [
  { label: 'MORNING LIFT', meta: '00:18  •  4K', color: 'thumb-orange' },
  { label: 'RITUAL / CUT 02', meta: '00:12  •  1080p', color: 'thumb-blue' },
  { label: 'NIGHT SESSION', meta: '00:24  •  4K', color: 'thumb-purple' },
  { label: 'B-ROLL 08', meta: '00:09  •  1080p', color: 'thumb-green' },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState('Editor');
  const [playing, setPlaying] = useState(false);
  const [enhancer, setEnhancer] = useState(false);
  const [chat, setChat] = useState(false);
  const [intensity, setIntensity] = useState(62);
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [aiInput, setAiInput] = useState('');
  const [aiMessages, setAiMessages] = useState<{ role: 'ai' | 'user'; text: string }[]>([
    { role: 'ai', text: 'Good morning, Alex. Upload a clip and I will help shape the cut.' }
  ]);
  const videoRef = useRef<HTMLVideoElement>(null);

  const loadVideo = (file?: File) => {
    if (!file || !file.type.startsWith('video/')) return;
    if (videoSrc) URL.revokeObjectURL(videoSrc);
    setVideoSrc(URL.createObjectURL(file));
    setCurrentTime(0);
  };
  const sendAiMessage = async () => {
    const message = aiInput.trim();
    if (!message) return;
    setAiInput('');
    setAiMessages(prev => [...prev, { role: 'user', text: message }]);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_AI_URL || 'http://127.0.0.1:8001'}/ai/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, language: 'fa' })
      });
      const data = await response.json();
      setAiMessages(prev => [...prev, { role: 'ai', text: data.reply || data.error || 'The AI core returned no response.' }]);
    } catch {
      setAiMessages(prev => [...prev, { role: 'ai', text: 'AI core is offline. Start FastAPI on port 8001 to enable chat.' }]);
    }
  };

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Aperture size={19} strokeWidth={2.5} /></div><span>cutting edge</span><small>v2</small></div>
        <button className="new-project"><Plus size={17} /> New project <span>⌘ N</span></button>
        <nav>
          <p className="nav-label">WORKSPACE</p>
          {[[Film,'Editor'],[LayoutTemplate,'Templates'],[Sparkles,'AI tools'],[Clock3,'Recent']].map(([Icon, label]) => <button key={label as string} className={`nav-item ${activeTab === label ? 'selected' : ''}`} onClick={() => setActiveTab(label as string)}><Icon size={17}/>{label as string}{label === 'AI tools' && <i>3</i>}</button>)}
          <p className="nav-label projects-label">PROJECTS</p>
          <button className="project-row"><span className="project-dot dot-pink"/>Cinematic Gym<span className="dots">•••</span></button>
          <button className="project-row"><span className="project-dot dot-yellow"/>Summer campaign<span className="dots">•••</span></button>
          <button className="project-row"><span className="project-dot dot-cyan"/>Personal archive<span className="dots">•••</span></button>
        </nav>
        <div className="sidebar-bottom"><button className="nav-item"><Settings size={17}/>Settings</button><button className="nav-item"><HelpCircle size={17}/>Help center</button><div className="user"><div className="avatar">AR</div><div><b>Alex Rivera</b><small>Pro workspace</small></div><MoreHorizontal size={17}/></div></div>
      </aside>

      <section className="workspace">
        <header className="topbar"><div className="crumb"><span>Projects</span><ChevronDown size={14}/><b>Cinematic Gym</b><span className="saved"><span/> Saved just now</span></div><div className="top-actions"><button className="icon-button"><Search size={17}/></button><button className="share"><ArrowUpRight size={15}/> Share</button><button className="export"><Upload size={15}/> Export <ChevronDown size={14}/></button></div></header>
        <div className="content">
          <div className="page-heading"><div><p className="eyebrow"><span className="live-dot"/> EDITOR / TIMELINE</p><h1>Make the moment <em>unmissable.</em></h1></div><div className="heading-right"><span className="autosave"><Activity size={14}/> Autosave on</span><button className="more"><MoreHorizontal size={20}/></button></div></div>
          <div className="editor-grid">
            <section className="preview-panel panel"><div className="panel-head"><div><span className="panel-kicker">PREVIEW</span><b>Ritual / cut 02</b></div><span className="resolution">16:9 <ChevronDown size={13}/></span></div><div className="video-stage" onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); loadVideo(e.dataTransfer.files[0]); }}><div className="video-art">{videoSrc ? <video ref={videoRef} src={videoSrc} className="uploaded-video" onTimeUpdate={() => setCurrentTime(videoRef.current?.currentTime || 0)} onLoadedMetadata={() => setDuration(videoRef.current?.duration || 0)} onEnded={() => setPlaying(false)} /> : <label className="upload-prompt"><Upload size={28}/><b>Drop a video to start editing</b><span>or click to browse MP4, MOV, WebM</span><input type="file" accept="video/*" onChange={e => loadVideo(e.target.files?.[0])}/></label>}<span className="timecode">{videoSrc ? `${Math.floor(currentTime / 60).toString().padStart(2,'0')}:${Math.floor(currentTime % 60).toString().padStart(2,'0')} / ${Math.floor(duration / 60).toString().padStart(2,'0')}:${Math.floor(duration % 60).toString().padStart(2,'0')}` : '00:00 / 00:12'}</span>{videoSrc && <button className="play" onClick={() => { if (!videoRef.current) return; if (playing) videoRef.current.pause(); else void videoRef.current.play(); setPlaying(!playing); }}>{playing ? 'Ⅱ' : <Play size={21} fill="white"/>}</button>}<div className="stage-caption">TRAIN WITH INTENT</div></div></div><div className="player-controls"><button onClick={() => { if (!videoRef.current) return; if (playing) videoRef.current.pause(); else void videoRef.current.play(); setPlaying(!playing); }}>{playing ? 'Ⅱ' : <Play size={16} fill="currentColor"/>}</button><div className="progress"><span style={{width: `${duration ? (currentTime / duration) * 100 : 0}%`}}/></div><span className="control-time">{Math.floor(currentTime / 60).toString().padStart(2,'0')}:{Math.floor(currentTime % 60).toString().padStart(2,'0')}</span><Waves size={16}/><MaximizeIcon/></div></section>
            <aside className="ai-panel panel"><div className="ai-title"><div className="ai-symbol"><Sparkles size={16}/></div><div><b>AI copilot</b><small>Ready to help you shape the cut</small></div><span className="online"/></div><div className="ai-message"><p>Good morning, Alex. Your footage has a <strong>focused, high-energy</strong> feel.</p><p>I found 4 moments that could make this sequence hit harder.</p><button className="ai-action"><WandSparkles size={15}/> Show me the moments <ArrowUpRight size={14}/></button></div><div className="suggestions"><span>Try asking</span><button>“Find the best take”</button><button>“Match my reference”</button></div><div className="chat-messages">{aiMessages.map((message, index) => <div key={index} className={`chat-bubble ${message.role}`}>{message.text}</div>)}</div><div className="chat-input-wrap"><input className="chat-input" value={aiInput} onChange={e => setAiInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') void sendAiMessage(); }} placeholder="Ask anything about your edit"/><button onClick={() => void sendAiMessage()}>↵</button></div></aside>
          </div>
          <section className="timeline panel"><div className="timeline-head"><div><span className="panel-kicker">TIMELINE</span><b>Cinematic Gym</b><span className="timeline-meta">· 24 clips · 01:42</span></div><div className="timeline-tools"><button><Grid2X2 size={15}/>Storyboard</button><button><Gauge size={15}/>Beat map</button><button className="zoom">−</button><div className="zoom-line"><span/></div><button className="zoom">+</button></div></div><div className="ruler"><span>00:00</span><span>00:15</span><span>00:30</span><span>00:45</span><span>01:00</span><span>01:15</span><span>01:30</span></div><div className="tracks"><div className="track-label">VIDEO <span>⌃</span></div><div className="track-content"><div className="clip clip-one">OPENING / WIDE <small>00:00 — 00:08</small></div><div className="clip clip-two">RITUAL / CUT 02 <small>00:08 — 00:20</small></div><div className="clip clip-three">FOCUS / CLOSE <small>00:20 — 00:33</small></div><div className="clip clip-four">FINISHER <small>00:33 — 00:47</small></div></div><div className="track-label audio-label">AUDIO <span>⌃</span></div><div className="audio-track"><div className="waveform">{Array.from({length: 60}).map((_, i) => <i key={i} style={{height: `${12 + ((i * 17) % 28)}px`}}/> )}</div></div><div className="playhead"><span/></div></div></section>
          <div className="bottom-row"><section className="media panel"><div className="section-head"><div><span className="panel-kicker">MEDIA</span><b>Your footage</b></div><button className="add-media"><Plus size={15}/> Add media</button></div><div className="clip-grid">{clips.map(c => <div className="media-card" key={c.label}><div className={`media-thumb ${c.color}`}><Play size={14} fill="white"/></div><b>{c.label}</b><small>{c.meta}</small></div>)}</div></section><section className={`enhancer panel ${enhancer ? 'active' : ''}`}><div className="enhancer-head"><div className="enhancer-icon"><Zap size={17} fill="currentColor"/></div><div><span className="panel-kicker">AI TOOL</span><b>Muscle enhancer</b></div><button className={`toggle ${enhancer ? 'on' : ''}`} onClick={() => setEnhancer(!enhancer)}><span/></button></div><p>Bring out definition with natural, frame-aware detail.</p><div className="slider-row"><span>Subtle</span><input type="range" min="0" max="100" value={intensity} onChange={e => setIntensity(+e.target.value)}/><span>Bold</span></div><div className="enhancer-footer"><span><span className="status-dot"/> {enhancer ? 'Active on selected clip' : 'Select a clip to preview'}</span><b>{intensity}%</b></div></section></div>
        </div>
        <footer className="statusbar"><span><span className="status-dot"/> All systems healthy</span><span><Zap size={13}/> GPU acceleration on</span><span className="status-right">24 fps <i/> 1920 × 1080 <i/> ProRes 422</span></footer>
      </section>
    </main>
  );
}
function MaximizeIcon() { return <span className="maximize">↗</span>; }
