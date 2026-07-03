---
name: unreal_frontlayer_translucency_crash_fix
description: FrontLayerTranslucency.cpp:716 ensure crash (glass reflection RDG bug) fixed by disabling Lumen front-layer translucency reflections project-wide
metadata: 
  node_type: memory
  type: project
  originSessionId: ca50f5d1-4ff0-4007-aeec-446007683ea2
---

2026-07-03: Play/render crash — two chained ensures:
- `FrontLayerTranslucency.cpp:716` `bAnyViewRendersPass` — GBuffer created but no view renders the pass.
- `RenderGraphValidation.cpp:653` — `TranslucencyElements(BeforeDistortion)` reads `FrontLayerTranslucency.GBufferC` which was never written.

Root cause: Lumen **Front Layer Translucency Reflections** (high-quality glass/oyna surface reflection). Project has 8 glass-Nanite meshes + Lumen HWRT reflections (see [[unreal_cesium_3dtiles_weight]]); the front-layer GBuffer pass gets allocated but no view renders it (scene-capture/preview/reflection view combo) → RDG dependency validation ensure. Known UE5 engine bug.

Fix applied to BOTH config files (needs Editor restart):
- DefaultEngine.ini `[/Script/Engine.RendererSettings]` (after r.Lumen.Translucency.Reflections lines): `r.Lumen.TranslucencyReflections.FrontLayer.EnableForProject=False` + `.Allow=0`
- DefaultDeviceProfiles.ini (after `r.Lumen.TranslucencyReflections=1`): same two cvars =0

Trade-off: glass keeps SSR + Lumen radiance-cache reflections; loses only the front-layer sharp layer (minor visual). If user dislikes glass look, revert these lines. Relates to weather/glass realism work [[unreal_weather_responsive_materials_task]].
