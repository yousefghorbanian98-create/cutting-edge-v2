"""Allow-listed audio mix operations (S-032)."""

from __future__ import annotations


def audio_filter(ops: list[dict], settings: dict) -> str | None:
    """Return the audio filter chain, or None when the plan has no audio."""
    audios = [op for op in ops if op["op"] == "trim" and op["kind"] == "audio"]
    if not audios:
        return None
    parts: list[str] = []
    labels: list[str] = []
    for index, op in enumerate(audios):
        label = f"a{index}"
        start = op["in_s"]
        end = op["in_s"] + op["duration_s"]
        fade_in = max(0, int(op.get("fade_in_ms") or 0)) / 1000
        fade_out = max(0, int(op.get("fade_out_ms") or 0)) / 1000
        gain = float(op.get("gain_db") or 0)
        linear = 10 ** (gain / 20)
        chain = (
            f"[{op['input']}:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,"
            f"aformat=channel_layouts=mono,volume={linear}"
        )
        if fade_in:
            chain += f",afade=t=in:st=0:d={fade_in}"
        if fade_out:
            chain += f",afade=t=out:st={max(0, op['duration_s'] - fade_out)}:d={fade_out}"
        delay = int(round(op["start_s"] * 1000))
        if delay:
            chain += f",adelay={delay}:all=1"
        chain += f"[{label}]"
        parts.append(chain)
        labels.append(f"[{label}]")
    if len(audios) == 1 and settings.get("mix") != "bed":
        parts[-1] = parts[-1][: -len(labels[0])] + "[aout]"
        return ";".join(parts)
    if settings.get("mix") == "bed":
        voice = next((op for op in audios if not op.get("duck")), None)
        music = next((op for op in audios if op.get("duck")), None)
        if voice is None or music is None:
            raise ValueError("bed mix needs a voice and a ducked music bed")
        voice_i = audios.index(voice)
        music_i = audios.index(music)
        parts.append(f"[a{voice_i}]aformat=channel_layouts=mono,asplit=2[voice_sc][voice_keep]")
        parts.append("[voice_sc]aformat=channel_layouts=mono[side]")
        parts.append("[voice_keep]aformat=channel_layouts=mono[voice_mix]")
        parts.append(f"[a{music_i}]aformat=channel_layouts=mono[music_in]")
        parts.append("[music_in][side]sidechaincompress=threshold=0.02:ratio=20:attack=5:release=250:makeup=1[ducked]")
        parts.append(
            "[ducked][voice_mix]amix=inputs=2:duration=longest:dropout_transition=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]"
        )
        return ";".join(parts)
    parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:dropout_transition=0[aout]")
    return ";".join(parts)
