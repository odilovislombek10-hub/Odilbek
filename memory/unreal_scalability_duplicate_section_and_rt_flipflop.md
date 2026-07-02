---
name: unreal-scalability-duplicate-section-and-rt-flipflop
description: "2026-07-02 ~14:20: found DefaultEngine.ini had a second, never-fixed [ScalabilityGroups] section stuck at Epic(3); also documented that r.RayTracing.Shadows/Skylight has been flip-flopped True/False 6x across today's auto-commits by different sessions"
metadata:
  type: project
  originSessionId: d809bf2c-2455-47d7-a376-89860435b6c1
---

User reported (via screenshot) Play-time errors recurring identically after supposedly being fixed, and explicitly suspected "something else is changing settings when I press Play, not what you changed." This suspicion was correct — two concrete mechanisms found:

## 1. Duplicate `[ScalabilityGroups]` section in `Config/DefaultEngine.ini` — the real "silent quality downgrade" bug
`DefaultEngine.ini` has **two different sections** that both set `sg.*` cvars:
- `[ScalabilityGroups]` at ~line 280 — a second, independent copy that NO prior session (including [[unreal_full_audit_2026_07_02]]) had touched. Was still `sg.ViewDistanceQuality=3` etc. (Epic), and was **entirely missing** `sg.ReflectionQuality`/`sg.GlobalIlluminationQuality`.
- `[/Script/Engine.GameUserSettings]` at ~line 291 — this is the one the full-audit session fixed to `=4` (Cinematic) for all 11 categories.
`Config/DefaultScalability.ini` and `Config/DefaultDeviceProfiles.ini` both correctly say `=4` everywhere.
**Verified live via `unreal-mcp` `SearchCVars`**: despite 2 of 3 files saying Cinematic, the actually-running editor had `sg.ViewDistanceQuality/ShadowQuality/GlobalIlluminationQuality/etc. = 3` (Epic) — i.e. Lumen GI/Reflections/Shadow quality was silently capped at Epic system-wide. This directly explains "Lumen/RT settings don't seem to apply" and visual quality looking different from what the ini implies.
**Fix applied 2026-07-02 ~14:20**: rewrote `DefaultEngine.ini`'s `[ScalabilityGroups]` section to `=4` for all 10 categories (added the 2 missing ones), matching the other two files. **Requires Editor restart** to take effect (same class of bug as [[unreal_rt_geometry_budget_fix]] — `[ScalabilityGroups]`/`ApplyCVarSettingsFromIni`-style sections only load at engine init).
**How to apply:** if a scalability/quality complaint recurs, don't just check `DefaultScalability.ini` — `grep -n "ScalabilityGroups" Config/*.ini` across ALL project ini files, since this project apparently has a stray duplicate section that's easy to miss.

## 2. `r.RayTracing.Shadows`/`r.RayTracing.Skylight` has been flip-flopped 6 times today by different sessions — not a new bug, a repeated undo war
`git log --oneline` + `git show <commit> -- Config/DefaultEngine.ini Config/DefaultDeviceProfiles.ini` shows this exact pair of cvars toggled True→False→True→False→True→False→True across commits `45f3975→7390753→ac87ba0→2016fdd→ba178ff` (same day, 2026-07-02). Each flip came with a plausible-sounding comment ("avoid 2x RT load with Lumen HWRT" vs. "disabling it didn't reduce RT geometry memory, only cost quality") — **both were written by different sessions of me, each unaware the other had already tried the opposite**.
**Current state (as of commit `ba178ff`, 14:12, and confirmed live via `SearchCVars`): `True`/`True`** — i.e. ray traced shadows/skylight ARE currently on, on top of `r.Lumen.HardwareRayTracing=True`.
**How to apply: before touching `r.RayTracing.Shadows`/`r.RayTracing.Skylight`/`r.RayTracing.Reflections` again, run `git log -p -- Config/DefaultEngine.ini Config/DefaultDeviceProfiles.ini | grep -B2 -A2 "RayTracing.Shadows"` first** to see the full flip history before "fixing" it — do not re-flip without new measured evidence (e.g. an actual RT geometry memory delta from a live PIE test), since this exact toggle has already been tried both ways multiple times today.

## 3. Live PIE test after the fix
Started a real PIE session via `unreal-mcp` `StartPIE` + `CaptureViewport` after applying fix #1 (editor was NOT restarted yet, so fix #1 likely not yet live). No red/yellow on-screen RT/VSM/streaming error text was visible in the captured frame — but this is inconclusive: the level auto-quits PIE after ~30-40s on its own (some scripted intro/timer), and on-screen debug messages (`GEngine->AddOnScreenDebugMessage`) may not always be present at the exact frame captured. Also noticed the giant white arrows over every window (previously investigated in [[unreal_full_audit_2026_07_02]], attributed to `BP_POI`'s `arrow_LookAtDirection` gizmo) ARE still visible during this Play-In-Viewport capture, plus a large red crosshair/reticle HUD overlay not previously catalogued — worth asking the user if that reticle is intentional UI.
**How to apply:** to actually verify a rendering/perf fix works, use `unreal-mcp` `StartPIE` (warmupSeconds small, e.g. 3-5, since this level self-terminates PIE quickly) + `CaptureViewport` immediately, decode the returned base64 PNG via **PowerShell** (`[Convert]::FromBase64String` + `[System.IO.File]::WriteAllBytes`) — NOT `python3`/`python` from Git Bash, which resolves to a broken WindowsApps stub and fails silently with exit code 49 on this machine. Save to the scratchpad and `Read` it as an image. The raw JSON tool result is too large for direct tool-result text (>1M chars) and gets written to a `tool-results/*.txt` file instead — must be decoded from there, not read as text.
