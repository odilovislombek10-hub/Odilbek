---
name: unreal_audio_routed_to_oculus
description: PIE game audio is routed to Oculus VR virtual audio device — why user hears no sound on Play
metadata: 
  node_type: memory
  type: project
  originSessionId: bbc80fbe-7b23-49c1-be34-530a8bd784cd
---

2026-07-03: User reported "no sound on Play" (Glavniy_MirMIron, ArchViz Explorer). Root cause was NOT the sound setup — PIE audio log showed the output device is the **Oculus/Meta VR headset's virtual audio device**, not the PC speakers/headphones the user listens on:

```
LogAudioMixer: Using Audio Hardware Device Наушники (Oculus Virtual Audio Device)
LogAudioEnumeration: Default Render Role='Communications', Device='Наушники (Oculus Virtual Audio Device)'
```

A connected VR headset makes Windows set the Oculus Virtual Audio Device as default render, so UE routes ALL game audio there. Sound plays fine — user just can't hear it.

**Fix (user side):** Windows Sound settings → Output → select real speakers/headphones (or disconnect Oculus), then RESTART the editor (UE picks the audio device only at startup, not per-PIE).

**Diagnostic technique:** `LogsToolset.GetLogEntries` pattern `(?i)(audiomixer|audiodevice|listener|metasound)` shows the chosen "Using Audio Hardware Device ...". Always check this FIRST when "no sound" is reported on this machine — the VR headset is usually plugged in. Relevant to all audio work here incl. [[unreal_weather_sound_system]].
