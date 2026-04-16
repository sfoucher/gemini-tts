# gemini-tts

A Claude Code plugin that auto-speaks every Claude response aloud using Gemini TTS.

## Requirements

- Windows (Git Bash must be installed)
- Python on PATH with these packages installed:

```bash
pip install google-genai sounddevice numpy
```

- A Gemini API key

## Installation

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "gemini-tts@sfoucher": true
  },
  "extraKnownMarketplaces": {
    "sfoucher": {
      "source": { "source": "github", "repo": "sfoucher/gemini-tts" }
    }
  },
  "env": {
    "GEMINI_API_KEY": "<your_key>"
  }
}
```

Restart Claude Code. TTS fires automatically on every response.

## Mute / Unmute

Say **"mute"** or **"unmute"** to Claude — it will run the appropriate command.

Or manually:

```bash
touch ~/.tts_muted    # mute
rm -f ~/.tts_muted    # unmute
```

## Voice

The default voice is `Zephyr`. To change it, edit `tts/tts_hook.py` and update the `voice_name` in `play_tts()`.

Available voices: Aoede, Charon, Fenrir, Kore, Leda, Orus, Puck, Schedar, Umbriel, Zephyr, Algieba, Algenib, Ankaa, Arcturus, Callirrhoe, Despina, Enceladus, Gacrux, Iocaste, Laomedeia, Lysithea, Propus, Pulcherrima, Rasalgethi, Sadachbia, Sadaltager, Sulafat, Vindemiatrix, Wasat, Zubenelgenubi.

## License

MIT
