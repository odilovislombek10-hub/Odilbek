---
name: unreal_planerovka_textures_real_vram_hog
description: "The real 19 GB VRAM hog in Glavniy_MirMIron = 97 Planerovka floor-plan textures with TC_EditorIcon (uncompressed, non-streamable) format — NOT Cesium; fix = change CompressionSettings to TC_BC7"
metadata: 
  node_type: memory
  type: project
  originSessionId: c850d648-44a8-4d31-b58b-65150fc12222
---

2026-07-03: Definitively identified via `memreport -full` (captured during editor via Content/Python/capture_play_diag.py, then read from Saved/Profiling/MemReports/*.memreport) what fills VRAM in Glavniy_MirMIron.

**HARD DATA (memreport, Glavniy_MirMIron, editor/static state):**
- `Texture 2D Memory = 19,661 MB (~19.2 GB)` of ~21 GB usable VRAM (rhi.DumpMemory).
- Of that, **97 Planerovka floor-plan textures = 17.64 GB** (summed from the memreport "Listing all textures" section). Each is `PF_B8G8R8A8` (uncompressed 4 B/px), up to 9925×7017 (~70 MP = 366 MB each) or 8270×5847 (~249 MB), `TEXTUREGROUP_World`, `Streaming: NO`, `UsageCount: 0` (not even displayed) — pure permanent-resident waste.
- **Cesium is NOT the hog**: `CesiumGltfPrimitiveComponent = 249 instances, only 755 MB` geometry; Cesium textures negligible. So optimizing Cesium (SSE/cache/tile-loads) saves almost nothing on VRAM — user's assumption that Cesium ate the 19 GB was disproved by data.
- RayTracing Acceleration Structure = 2,286 MB (BLAS 2,238 + TLAS 48); RT Geometry Resident = 3,001 MB — under the 4,096 MB pool, so RT is NOT actually out of memory (see the separate spurious RT over-budget finding).

**Why the earlier "optimization" ([[unreal_play_error_rt_streaming_fix]]) did nothing:** that session set `NeverStream=false` on the 99 Planerovka textures intending stream-on-demand. VERIFIED INEFFECTIVE: the textures were left `CompressionSettings=TC_EditorIcon`, and TC_EditorIcon is an inherently uncompressed, NON-STREAMABLE format — setting NeverStream=false on it is a no-op, the format itself blocks streaming. So they stayed fully resident at full uncompressed size. Confirmed live via ObjectTools.get_properties on `/Game/Level/Odilbek/Planerovka/4blok_tipovoy-page-00001`: `CompressionSettings=TC_EditorIcon, NeverStream=false, MaxTextureSize=0, LODGroup=TEXTUREGROUP_World, MipGenSettings=TMGS_SimpleAverage, SRGB=true`.

**REAL FIX (one change fixes both size AND streaming):** set `CompressionSettings` from `TC_EditorIcon` to `TC_BC7` (near-lossless, keeps floor-plan text readable, resolution preserved). This (a) compresses 4 B/px -> 1 B/px = **4x smaller** (366 MB -> ~92 MB), and (b) makes it a streamable format so the existing NeverStream=false FINALLY takes effect -> evicts when the floor-plan viewer widget isn't showing it (UsageCount=0 -> ~0 resident). Applied+saved as a test on `4blok_tipovoy-page-00001` via ObjectTools.set_properties (values `{"CompressionSettings":"TC_BC7"}`) + AssetTools.save_assets — returned true. For all 97: 17.64 GB -> ~8.9 GB if all loaded, ~1-2 GB actual with streaming working = ~15 GB VRAM freed. Optional extra lever: MaxTextureSize=4096 cap (9925 is overkill; 4096 still readable) for further reduction.

**How to apply the batch:** find all Texture2D under `/Game/Level/Odilbek/Planerovka` (recursive, includes Xonadonlar/1..8Block), for each set CompressionSettings=TC_BC7, then save. Use ProgrammaticToolset/AssetTools batch (same pattern as the prior 99/99 NeverStream run). Verify readability on one displayed plan before/after. This is the fix for the "TEXTURE STREAMING POOL OVER ... MiB BUDGET" on-screen error. Relates to [[unreal_vram_texture_breakdown]], [[unreal_perf_texture_audit]], [[unreal_play_error_rt_streaming_fix]].
