---
name: unreal-vr-perf-optimization
description: "VR level performance: audit findings (vr_perf_audit.py) + VR-only optimizations applied in VRPawn BeginPlay + Instanced Stereo; what's left"
metadata: 
  node_type: memory
  type: project
  originSessionId: b4d7b4d9-0113-48e5-98ec-f8b0fc508ab5
---

2026-07-03. VR level (`/Game/Level/Odilbek/VR`) stutters/lags in headset. Root cause = the project's rendering config is tuned for max-quality FLAT (monitor) — Lumen + Hardware RT + TSR + Nanite@1.0 + ScreenPercentage 100 — which is brutal in stereo VR. Fix strategy: apply lighter settings ONLY in VR (so Glavniy/Pragulka keep their look), via VRPawn BeginPlay console commands + one project-wide-but-VR-only config flag.

**AUDIT — `Content/Python/vr_perf_audit.py`** (user runs in Editor Python console: `exec(open(r"D:/.../Content/Python/vr_perf_audit.py").read())`; writes `Saved/VR_Perf_Audit.txt` + logs `VRAUDIT:` lines). VR level results: 702 actors, 374 unique static meshes / 2452 draws, 1772 HISM foliage (190 hosts), **0 skeletal meshes** (no heavy characters — good), 3 DirectionalLights only (2 dynamic-shadow), 35 decals, 1 VolumetricCloud + UDS, ~30 detailed car BPs (Maybach/Range Rover/Kia/Gentra…), 3 Cesium actors but NO heavy Cesium3DTileset. **Biggest costs: 199 TRANSLUCENT material slots (car glass/windows) + 1392 two-sided slots + volumetric clouds + Lumen HWRT.** So the problem is the RENDER PATH, not actor count. NOTE: the script's triangle-count API returned 0 for every mesh (StaticMeshEditorSubsystem.get_number_triangles / EditorStaticMeshLibrary path failed on this build) — tri data missing; fix the tri fn if poly data is needed later.

**APPLIED (2026-07-03):**
- **VRPawn `EventBeginPlay`** (inside the existing `if IsHeadMountedDisplayEnabled` branch, via write_graph_dsl full-rewrite — merged clean, `Development|ExecuteConsoleCommand` nodes): `r.Lumen.HardwareRayTracing 0`, `r.Lumen.Reflections.HardwareRayTracing 0`, `r.Nanite.MaxPixelsPerEdge 2`, `r.VolumetricCloud.ReflectionRaySampleMaxCount 0`, `r.ScreenPercentage 90`. Compiled+saved. These run ONLY when an HMD is active (real VR), so flat levels are untouched. Reversible (edit the pawn). **VERIFY r.Lumen.HardwareRayTracing toggles at runtime** — if it's read-only on this build, HWRT stays on and we must move it to a VR device-profile/config route.
- **`Config/DefaultEngine.ini` `[/Script/Engine.RendererSettings]`**: added `vr.InstancedStereo=True` (both eyes one pass, ~30-40% render-thread CPU saving; only affects stereo, zero impact on flat). **Needs Editor restart + one-time shader recompile.**

**STILL TODO (bigger, content-level — only if still not smooth after the above + restart):**
- **199 translucent slots**: car glass etc. — biggest remaining VR cost (overdraw). Options: opaque/cheaper glass material for VR, or cull distant cars. ~30 car BPs likely lack aggressive LODs.
- **1392 two-sided slots**: audit them; many are probably wrongly two-sided (cf. the TwoSidedFoliage shading-model bugs in [[unreal_uds_weather_realism_tuning]]/[[unreal_wood_material_shading_model_fix]]). Turning off unneeded two-sided halves their shading.
- Volumetric clouds: `r.VolumetricCloud 0` in VR (or drop ViewRaySampleMaxCount hard) if clouds still cost too much — tradeoff: flatter sky in VR.
- Further `r.ScreenPercentage` 80 / `vr.PixelDensity 0.8` if GPU-bound.
- Shadows: reduce VSM (`r.Shadow.Virtual.MaxPhysicalPages`) or `sg.ShadowQuality`.
- Draw calls: 61 BP_NVSplineMesh + 332 StaticMeshActors — merge/instance candidates.
- PSO precaching for the hitch/"shuvalash" (200 PSO hitches noted in [[unreal_cesium_3dtiles_weight]]).

Approach principle: keep VR changes VR-scoped (VRPawn BeginPlay cvars or vr.* config) so the flat archviz look (Lumen+HWRT) is preserved. See [[unreal_weather_panel_vr_pragulka]] (VRPawn already hosts the weather-panel menu), [[unreal_audit_python_script]], [[feedback_respond_in_uzbek]].
