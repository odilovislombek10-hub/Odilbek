---
name: unreal-packaged-vs-editor-exposure
description: "Packaged EXE \"looks Medium/washed vs editor\" root cause = EXPOSURE (not scalability, not HW/SW Lumen); how to diagnose packaged runtime via -log + exec diag.txt"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7cc3da9e-b40e-4cad-8512-f15a63d1c1b2
---

2026-07-03: User reported packaged Development EXE (E:\MIR MIRON PACKAGE\Windows) looks
"Medium/washed, not Epic like editor", and "Light_Inst1 material doesn't work in EXE".

INVESTIGATION RESULT — it is NOT a quality/scalability downgrade and NOT a Lumen HW→SW fallback:
- Runtime cvar dump (exec diag.txt) proved EXE runs FULL EPIC: all sg.*=3, project cvars win over
  scalability (LastSetBy: ProjectSetting), ScreenPercentage=100, MaterialQualityLevel=3,
  Shadow.MaxResolution=2048, SSR=3, VolumetricFog=1.
- Hardware Ray Tracing is ACTIVE in packaged: log "Ray tracing is enabled (dynamic)", DXR tier 1.1,
  r.Lumen.HardwareRayTracing=1, and RT SBT built ("Recreating Persistent SBTs ... NumGeometrySegments
  0->2304"), 0 errors/fatals. Editor runtime SearchCVars = IDENTICAL (EnableOnDemand=1, Lumen.HWRT=1,
  LightingMode=0). So editor & EXE use the exact same HW-RT pipeline.
- Side-by-side screenshots (user gave EXE vs editor-Standalone, both 16:00 same weather): EXE is
  ~1 stop BRIGHTER + LOWER CONTRAST + washed/milky; editor is contrasty with GLOWING street lamps.
  Uniform brightness wash across sky+walls+ground = EXPOSURE signature, NOT a GI method change.
- `Light_Inst1` (Content/TwinEra/material/Light/Light_Inst1.uasset) IS cooked & in the pak (6 hits);
  it's the emissive street-lamp material. It looks "not working" only because over-exposure crushes
  its glow contrast.

ROOT CAUSE: r.DefaultFeature.AutoExposure=1 set by **Constructor (engine default)** — exposure is NOT
locked by any project PPV, so auto-exposure/eye-adaptation lands differently between editor-standalone
and packaged. Fix = lock exposure (Manual metering / Min EV100==Max EV100) in the level's global
PostProcessVolume or UDS post-process, matching the editor look. Related: [[unreal-uds-weather-realism-tuning]].

DIAGNOSTIC TECHNIQUE (packaged Development build, UE5.8): launch INNER binary directly
(E:\...\Odilbek\Binaries\Win64\Odilbek.exe, NOT the Windows\Odilbek.exe shim — shim does NOT forward
-ExecCmds, log shows "Command Line:" empty). Use DIAG_LOG.bat. In-game console `exec diag.txt` reads
the file from <Project>/Binaries/ (NOT ProjectDir root). diag.txt lists bare cvar names (echo value +
LastSetBy) + `scalability` + `HighResShot 1920x1080` (PNG to Odilbek\Saved\Screenshots\Windows\ —
readable). Log: Odilbek\Saved\Logs\Odilbek.log. See [[unreal-packaging-workflow]].
