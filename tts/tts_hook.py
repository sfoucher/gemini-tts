import re
import json
import os
import sys
from pathlib import Path


def strip_markdown(text: str) -> str:
    # Remove fenced code blocks (``` ... ```) with newline cleanup
    text = re.sub(r'\n```[\s\S]*?```\n', '\n', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove inline code
    text = re.sub(r'`[^`\n]*`', '', text)
    # Remove markdown links, keep display text
    text = re.sub(r'\[([^\]]+)\]\((?:[^()]+|\([^)]*\))*\)', r'\1', text)
    # Remove bare URLs (but not trailing punctuation)
    text = re.sub(r'https?://[^\s.,:;!?)\]"\'`]*(?:\.[^\s.,:;!?)\]"\'`]+)*', '', text)
    # Remove header markers (## Title -> Title)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    # Remove italic (*text* or _text_)
    text = re.sub(r'\*([^*\n]+)\*', r'\1', text)
    text = re.sub(r'_([^_\n]+)_', r'\1', text)
    # Remove bullet list markers
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    # Remove numbered list markers
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Collapse 3+ blank lines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Cleanup stray bold/italic markers
    text = re.sub(r'\*{2,}', '', text)
    text = re.sub(r'_{2,}', '', text)
    return text.strip()


def parse_audio_mime_type(mime_type: str) -> dict:
    if not mime_type:
        return {"bits_per_sample": 16, "rate": 24000}
    bits_per_sample = 16
    rate = 24000
    for param in mime_type.split(";"):
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate = int(param.split("=", 1)[1])
            except (ValueError, IndexError):
                pass
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass
    return {"bits_per_sample": bits_per_sample, "rate": rate}


def get_last_assistant_message(transcript_path: str) -> str | None:
    path = Path(transcript_path)
    if not path.exists():
        return None
    last_assistant = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    continue
                # Real Claude Code transcripts wrap messages in a "message" envelope
                msg = obj.get("message", obj)
                if not isinstance(msg, dict):
                    continue
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        last_assistant = content
                    elif isinstance(content, list):
                        texts = [
                            block.get("text", "")
                            for block in content
                            if isinstance(block, dict) and block.get("type") == "text"
                        ]
                        joined = " ".join(t for t in texts if t)
                        if joined:
                            last_assistant = joined
            except json.JSONDecodeError:
                continue
    return last_assistant


def play_tts(text: str, voice: str = "Zephyr") -> None:
    import sounddevice as sd
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
            )
        ),
    )
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=text)])
    ]

    stream = None
    try:
        for chunk in client.models.generate_content_stream(
            model="gemini-3.1-flash-tts-preview",
            contents=contents,
            config=config,
        ):
            if not chunk.parts or not chunk.parts[0].inline_data:
                continue
            inline_data = chunk.parts[0].inline_data
            if not inline_data.data:
                continue
            if stream is None:
                params = parse_audio_mime_type(inline_data.mime_type)
                stream = sd.RawOutputStream(
                    samplerate=params["rate"],
                    channels=1,
                    dtype=f"int{params['bits_per_sample']}",
                )
                stream.start()
            stream.write(inline_data.data)
    finally:
        if stream is not None:
            stream.stop()
            stream.close()


def main() -> None:
    mute_flag = Path.home() / ".tts_muted"
    if mute_flag.exists():
        return
    try:
        payload = json.loads(sys.stdin.read())
        transcript_path = payload.get("transcript_path")
        if not transcript_path:
            return
        text = get_last_assistant_message(transcript_path)
        if not text or not text.strip():
            return
        clean = strip_markdown(text)
        if not clean:
            return
        play_tts(clean)
    except Exception:
        pass


if __name__ == "__main__":
    main()
