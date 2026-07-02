---
name: unreal_anima_visual_config_merge
description: 2026-07-03 user liked D:/ANIMA_Character DefaultEngine.ini look; merged its visual/render cvars into Odilbek + flipped AllowStaticLighting=True; kept our levels/GameMode/crash-fixes
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ca2f74c-63b5-4d72-97d6-f3f2a139a311
---

2026-07-03: user said "MENGA MANASHU INI FAYIL YOQTI" about `D:\ANIMA_Character\Config\DefaultEngine.ini` and asked to bring that look into our Odilbek project. Chose "vizual look'ni to'liq moslashtir" option (merge render cvars + AllowStaticLighting=True), NOT a full overwrite — a full overwrite would break the project (ANIMA's GameMaps/GameMode/GameNameRedirects point to `/Game/ArchvisProject/...` and `ANIMA_Character`, which don't exist here, and would wipe all crash-fixes).

**Applied to `Config/DefaultEngine.ini` `[/Script/Engine.RendererSettings]` (new "ANIMA look" block near line ~179):**
- `r.AllowStaticLighting=False → True` (baked lightmaps alongside Lumen — the big one; needs Editor restart + possibly Build Lighting)
- `r.Tonemapper.Sharpen=1.5 → 2` (in RendererSettings AND the `[/Script/Engine.Engine]` duplicate section)
- Added: `LightPropagationVolume=0`, `HighResScreenshotDelay=8`, `DefaultBackBufferPixelFormat=4`, `AllowGlobalClipPlane=False`, `SupportSkyAtmosphereAffectsHeightFog=True`, `DefaultFeature.LensFlare=True`, `ClearCoatNormal=False`, `NormalMapsForStaticLighting=False`, `GenerateMeshDistanceFields=True`, `PostProcessing.PropagateAlpha=1`, `SkinCache.SceneMemoryLimitInMB=16962`, `SkinCache.DefaultBehavior=1`, `CustomDepth=3`, `MSAACount=4`, `RayTracing.Geometry.InstancedStaticMeshes.Culling=0`

**Also fixed the device-profile runtime override** (the classic bug — see [[unreal_play_error_rt_streaming_fix]]): `Config/DefaultDeviceProfiles.ini` `[Windows DeviceProfile]` had `r.Tonemapper.Sharpen=1.5` which wins at Play → changed to `2` so the ANIMA look holds at runtime. Rest of the ANIMA cvars are startup cvars not present in the device profile, so no other conflict.

**Kept ours (NOT copied from ANIMA):** startup level `Glavniy_MirMIron`, `BP_Explorer_*` GameMode/GameInstance, `shablon_test` GameNameRedirects, and ALL crash-fixes (RT geometry budget cap, `Lumen.DiffuseIndirect.AsyncCompute=0`, streaming pool 12GB, GPUCrashDebugging, scalability).

**⚠️ Watch:** `r.RayTracing.Geometry.InstancedStaticMeshes.Culling=0` increases RT geometry memory — if the old RT "Over Budget"/page-fault error returns (see [[unreal_rt_geometry_budget_fix]] and [[unreal_gpu_crash_lumen_hwrt_pagefault]]), set it back to `1` first.

Backup of pre-merge file: `Config/DefaultEngine.ini.bak_before_anima_visual`. NEEDS EDITOR RESTART to take effect (RendererSettings cvars apply only at engine startup). Not yet visually verified by the user as of 2026-07-03.
