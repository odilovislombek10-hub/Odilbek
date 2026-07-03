---
name: unreal_engine_ini_clean_rt_deferred_cvars
description: "Engine-install base ini files are CLEAN (no hidden RT/streaming override); real cause of the 0 B / 15,999 EiB over-budget error is deferred/dummy RT cvars + broken RT residency accounting, NOT ini values or a hidden engine override"
metadata: 
  node_type: memory
  type: project
  originSessionId: c850d648-44a8-4d31-b58b-65150fc12222
---

2026-07-03: User hypothesized the persistent RT-geometry + texture-streaming "over budget" error came from a hidden override in the engine-install main ini files (`C:\Program Files\Epic Games\UE_5.8\Engine\Config`). Investigated with hard evidence from the project itself. Verdict: engine base files are CLEAN — but the user's deeper instinct ("it's not the True/False values, it's structural") is CORRECT.

**Engine-install ini files — checked, all CLEAN (do NOT re-investigate these):**
- `Engine\Config\ConsoleVariables.ini` — only `[Startup]` header, ZERO RT/Lumen/Streaming/Shadow entries. (This file has `SetByConsoleVariablesIni` priority, HIGHER than project `SetByProjectSetting`, so it was the prime suspect — but it's empty of overrides. An earlier session's engine-level edits were correctly reverted, see [[unreal_rt_geometry_budget_fix]].)
- `BaseDeviceProfiles.ini` `[WindowsEditor DeviceProfile]` and `[Windows DeviceProfile]` — no RT/streaming/scalability CVars.
- `BaseEngine.ini` — no `ResidentGeometryMemoryPoolSizeInMB` / `UseReferenceBasedResidency` / `NumAlwaysResidentLODs` defaults at all.

**Proof the project config IS loaded correctly (so "you didn't restart" was always false — see [[feedback_restart_was_done_stop_blaming_it]]):** `Saved/Logs/Odilbek.log` / `Odilbek_2.log` show at startup: `Set CVar r.RayTracing.Shadows:0`, `Skylight:0`, `ResidentGeometryMemoryPoolSizeInMB:4096`, `UseReferenceBasedResidency:0`, `NumAlwaysResidentLODs:0`, `r.Streaming.PoolSize:9216`, `UseFixedPoolSize:1`, `LimitPoolSizeToVRAM:1`. Editor active device profile = `WindowsEditor` (which has no CVar section), so in the editor ONLY DefaultEngine.ini applies → RT.Shadows/Skylight are OFF in the editor. The `[Windows DeviceProfile]` Shadows=True/Skylight=True applies ONLY to a packaged/standalone Windows build.

**REAL structural cause of the `0 B / 15,999 EiB` over-budget error:**
1. Several RT cvars log as `deferred - dummy variable created` and are NEVER re-applied later: `r.RayTracing.Reflections`, `r.RayTracing.Reflections.MaxRoughness`, `r.RayTracing.Geometry.Instancing`, `r.RayTracing.Geometry.StripMinLodData`, `r.Lumen.Translucency.Reflections.HardwareRayTracing`. They're set from `[/Script/Engine.RendererSettings]` before the RT module registers them → dummy placeholder → may not take intended effect. (Note: `deferred/dummy` is a common, often-harmless UE message, but here these RT cvars never show a second real application.)
2. The on-screen numbers `0 B / 15,999 EiB` are NONSENSE (0 bytes resident, ~infinite budget, yet flagged over-budget) = the RT geometry residency manager can't compute a valid budget. In fixed-pool mode (`UseReferenceBasedResidency=0`) + LOD-less geometry (Cesium 3D Tiles + Level/Export CAD props), the always-resident BLAS set has no valid cap. `15,999 EiB` is UE's overflow display.

**Conclusion:** flipping RT.Shadows/Skylight/pool True/False in project ini does NOTHING for this — that's why ~8 flip-flops over 26h failed. Real fix is NOT ini numbers: either `UseReferenceBasedResidency=1` + **Rendering > Generate Ray Tracing Proxies** (gives geometry evictable RT LODs), or give Cesium/heavy meshes real LODs / disable RT on them. Texture streaming pool is `LimitPoolSizeToVRAM=1` → actual pool 14839 MB / 21198 MB VRAM (log line 1202), squeezed by RT/Lumen/Nanite VRAM use. Relates to [[unreal_cesium_3dtiles_weight]], [[unreal_rt_geometry_budget_fix]], [[unreal_scalability_duplicate_section_and_rt_flipflop]], [[unreal_gpu_crash_lumen_hwrt_pagefault]].
