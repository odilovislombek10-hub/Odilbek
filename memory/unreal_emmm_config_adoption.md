---
name: unreal_emmm_config_adoption
description: "2026-07-03: user preferred the E:\\mmirmmmmm\\Unreal Engine config look; adopted it wholesale into Odilbek (lighter/softer profile) but re-patched our 3 crash/safety fixes; supersedes ANIMA visual merge"
metadata: 
  node_type: memory
  type: project
  originSessionId: dad784af-3cec-4cff-ad4f-fed6d09e62c0
---

**2026-07-03: user said "E:\mmirmmmmm\Unreal Engine — MNEGA MANASHU CONFIG YOQTI" (I like THIS config).** That `E:\mmirmmmmm\Unreal Engine` is a sibling/variant copy of the Odilbek ArchViz project (same levels Glavniy_MirMIron, same BP_Explorer GameInstance/GameMode, same redirects) with a **lighter, more conservative render config**. Only `DefaultEngine.ini` + `DefaultDeviceProfiles.ini` differ; `DefaultScalability.ini` and `DefaultGame.ini` are identical.

**What the E: config's look IS (vs our prior heavy Odilbek config):** softer & lighter, fully-dynamic-Lumen. Key diffs — Tonemapper.Sharpen **1.5** (we had 2 from ANIMA merge), AA method **2/TAA** at runtime via device profile (we had 4/TSR), Lumen Detail/LightingQuality **1** (we had 4), Shadow MaxResolution **2048** + MaxPhysicalPages 8192 (we had 4096/16384), **AllowStaticLighting=False** (we had True from ANIMA), **PathTracing=False** (we had True), RT.Reflections/GI OFF. IMPORTANT nuance: E: DEVICE PROFILE (wins at runtime) sets **RayTracing.Shadows=True + Skylight=True** even though its Engine.ini says False — so E: effectively runs RT crisp shadows+skylight but Lumen for GI+reflections. That balance is the look the user likes.

**ACTION TAKEN (user was away/no AskUserQuestion answer → proceeded with recommended option, backup taken, reversible, no effect until Editor restart):** copied E:'s `DefaultEngine.ini` + `DefaultDeviceProfiles.ini` verbatim over Odilbek's, THEN re-patched our 3 critical fixes so we keep the look + stability WITHOUT losing crash protection:
1. **`r.GPUCrashDebugging=1`** re-added to Engine.ini (E: lacked it).
2. **`r.Lumen.DiffuseIndirect.AsyncCompute=0`** re-added to BOTH Engine.ini AND the device profile (device profile wins at runtime, so belt+suspenders) — this is THE fix for the Lumen HWRT async page-fault GPU crash [[unreal_gpu_crash_lumen_hwrt_pagefault]]. E: config had neither.
3. **Streaming.PoolSize 8192→12288** in the device profile (E: had an internal inconsistency: Engine.ini said 12288 but device profile said 8192, and device profile wins → E: actually ran 8GB. Fixed to 12GB, matching [[unreal_perf_texture_audit]]).
4. Removed the deprecated **`r.Mobile.VirtualTextures=True`** from Engine.ini (fires a separate Ensure/warning).

**Backups (reversible):** `Config/DefaultEngine.ini.bak_before_Emmm_20260703_113241` + `DefaultDeviceProfiles.ini.bak_before_Emmm_20260703_113241`. To revert entirely, copy those back.

**This SUPERSEDES the [[unreal_anima_visual_config_merge]] visual choices** — the ANIMA merge had pushed Sharpen=2 + AllowStaticLighting=True; the user now prefers the softer E: look (Sharpen 1.5, AllowStaticLighting=False, fully dynamic). Kept our crash-fixes and the shared project settings (levels/GameMode/audio/packaging unchanged since E: has the same ones).

**NEEDS EDITOR RESTART** to take effect. Note the current live Editor session still runs the pre-swap config (it already had AsyncCompute=0 live-confirmed, so still crash-safe now). Verify the look in-Editor/PIE after restart; if user wants RT shadows lighter still, the device profile RayTracing.Shadows/Skylight are the knobs (but memory warns against random-flipping them — see [[unreal_scalability_duplicate_section_and_rt_flipflop]]).
