# gemini-tts

A Claude Code plugin that auto-speaks every Claude response aloud using Gemini TTS.

## Requirements

- Windows (Git Bash must be installed)
- Python on PATH with these packages installed:

```bash
pip install google-genai sounddevice
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
    "GEMINI_API_KEY": "<your_key>",
    "TTS_VOICE": "Zephyr"
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

Set `TTS_VOICE` in the `env` block of `~/.claude/settings.json` (default: `Zephyr`):

```json
"env": {
  "GEMINI_API_KEY": "<your_key>",
  "TTS_VOICE": "Aoede"
}
```

Available voices: Aoede, Charon, Fenrir, Kore, Leda, Orus, Puck, Schedar, Umbriel, Zephyr, Algieba, Algenib, Ankaa, Arcturus, Callirrhoe, Despina, Enceladus, Gacrux, Iocaste, Laomedeia, Lysithea, Propus, Pulcherrima, Rasalgethi, Sadachbia, Sadaltager, Sulafat, Vindemiatrix, Wasat, Zubenelgenubi.

## Limitations

- **Generation delay:** TTS runs synchronously after each response. Claude Code is blocked until audio finishes playing, so long responses will delay the next prompt by several seconds.
- **Windows only:** Relies on `run-hook.cmd` and Git Bash. Not tested on macOS or Linux.

## License

MIT
