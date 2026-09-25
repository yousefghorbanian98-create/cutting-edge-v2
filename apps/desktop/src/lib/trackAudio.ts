/**
 * S-022 audio bus. One oscillator per audio track, summed into an AnalyserNode.
 * Mute/solo come from trackIsActive. This is not the S-024 clip graph.
 */

import type { Sequence } from '@/domain/timeline';
import { trackIsActive } from '@/domain/tracks';

export type AudioCapability = 'available' | 'missing' | 'unknown';

interface TrackVoice {
  osc: OscillatorNode;
  gain: GainNode;
}

interface TrackGraph {
  ctx: AudioContext;
  analyser: AnalyserNode;
  voices: Map<string, TrackVoice>;
}

declare global {
  interface Window {
    webkitAudioContext?: typeof AudioContext;
  }
  interface HTMLElement {
    __ceAnalyser?: AnalyserNode;
  }
}

let graph: TrackGraph | null = null;
let meter: HTMLElement | null = null;
let playing = false;
let capability: AudioCapability = 'unknown';

function contextCtor(): typeof AudioContext | undefined {
  if (typeof window === 'undefined') return undefined;
  return window.AudioContext ?? window.webkitAudioContext;
}

function paintMeter(): void {
  if (!meter) return;
  meter.dataset.capability = capability;
  meter.dataset.contextState = graph?.ctx.state ?? 'unknown';
  meter.dataset.playing = playing ? '1' : '0';
  if (graph) meter.__ceAnalyser = graph.analyser;
}

export function attachTrackMeter(node: HTMLElement | null): void {
  meter = node;
  paintMeter();
}

function ensureGraph(): TrackGraph | null {
  const Ctor = contextCtor();
  if (!Ctor) {
    capability = 'missing';
    paintMeter();
    return null;
  }
  if (!graph) {
    const ctx = new Ctor();
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 2048;
    analyser.connect(ctx.destination);
    graph = { ctx, analyser, voices: new Map() };
    capability = 'available';
  }
  paintMeter();
  return graph;
}

function ensureVoice(current: TrackGraph, trackId: string): TrackVoice {
  const existing = current.voices.get(trackId);
  if (existing) return existing;
  const osc = current.ctx.createOscillator();
  const gain = current.ctx.createGain();
  osc.frequency.value = 440;
  osc.type = 'sine';
  gain.gain.value = 0;
  osc.connect(gain);
  gain.connect(current.analyser);
  osc.start();
  const voice = { osc, gain };
  current.voices.set(trackId, voice);
  return voice;
}

export function syncTrackOutput(sequence: Sequence, nextPlaying: boolean): void {
  playing = nextPlaying;
  const current = graph ?? (nextPlaying ? ensureGraph() : null);
  const video = document.querySelector('[data-testid=preview-video]');
  if (video instanceof HTMLVideoElement) {
    const visible = sequence.tracks.some(
      (track) => track.kind === 'video' && trackIsActive(sequence, track.id)
    );
    video.dataset.videoActive = visible ? '1' : '0';
    video.style.visibility = visible ? 'visible' : 'hidden';
  }
  if (!current) {
    paintMeter();
    return;
  }
  const audioIds = new Set(
    sequence.tracks.filter((track) => track.kind === 'audio').map((track) => track.id)
  );
  for (const [id, voice] of current.voices) {
    if (audioIds.has(id)) continue;
    voice.osc.stop();
    voice.osc.disconnect();
    voice.gain.disconnect();
    current.voices.delete(id);
  }
  for (const track of sequence.tracks) {
    if (track.kind !== 'audio') continue;
    const voice = ensureVoice(current, track.id);
    const open = playing && trackIsActive(sequence, track.id);
    voice.gain.gain.value = open ? 0.2 : 0;
  }
  paintMeter();
}

export function resumeTrackAudio(sequence: Sequence): AudioCapability {
  const current = ensureGraph();
  if (!current) return capability;
  void current.ctx.resume().then(() => paintMeter());
  syncTrackOutput(sequence, true);
  return capability;
}

export function pauseTrackAudio(sequence: Sequence): void {
  syncTrackOutput(sequence, false);
}

export function isTrackAudioPlaying(): boolean {
  return playing;
}
