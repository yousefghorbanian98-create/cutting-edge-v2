"""Auto Narrator — Free TTS in Persian/English using edge-tts"""
import asyncio

VOICES = {"fa":"fa-IR-FaridNeural","en":"en-US-GuyNeural"}

async def _gen(text, output, voice):
    try:
        import edge_tts
        c = edge_tts.Communicate(text=text, voice=voice)
        await c.save(output)
    except ImportError:
        print("edge-tts not installed")

def narrate(text: str, output: str, lang="fa"):
    asyncio.run(_gen(text, output, VOICES.get(lang, "fa-IR-FaridNeural")))
