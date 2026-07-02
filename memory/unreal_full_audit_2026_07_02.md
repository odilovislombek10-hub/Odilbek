---
name: unreal-full-audit-2026-07-02
description: "Full project audit (config/PSO/scalability/materials/BP_POI) triggered by user complaint that project stays heavy and RT/shadows/materials look wrong despite settings being on"
metadata:
  node_type: memory
  type: project
  originSessionId: 31f44c6d-96a9-4978-8942-df0a42c71549
---

## Context
User (frustrated, wrote in Uzbek slang) asked for an exhaustive audit of everything — assets, textures, materials, actors, meshes, levels, blueprints, widgets, lighting, ini files, git history — because the project stays heavy and RT/shadows/hardware settings "don't seem to work," and materials look dull/washed-out until opened in the Material Editor (which then makes them look correct). Gave blanket permission to fix/test without asking again.

## Root causes found and fixed

**1. PSO Shader Cache misconfigured — likely primary cause of "material clarifies when opened in Material Editor" + general stutter/ms hitches.**
`Config/DefaultEngine.ini`: `r.ShaderPipelineCache.StartupMode=3` was an **invalid value** (engine only defines 0/1/2, default=1; see cvar help text). Confirmed via live log during PIE: `LogPSOHitching: Encountered 50 PSO creation hitches so far (20 graphics, 30 compute). 0 of them were precached.` — zero precached PSOs matches a broken StartupMode causing on-demand/fallback shader compilation at first draw (which is why opening the Material Editor, which force-compiles, "fixes" the look). Fixed to `1` (Fast precompile mode, matches engine default).

**2. Scalability level contradicted itself across 3 ini files.**
`Config/DefaultEngine.ini`'s `[/Script/Engine.GameUserSettings]` section had `OverallScalabilityLevel=3` / `sg.ShadowQuality=3` etc (High) while `Config/DefaultDeviceProfiles.ini` and `Config/DefaultScalability.ini` forced the same groups to `=4` (Cinematic) via `[ScalabilityGroups]`/device profile CVars (which have `SetByScalability` priority, lower than `SetByProjectSetting` — confirmed via log: `Setting the console variable '...' with 'SetByScalability' was ignored`). This produced unpredictable effective quality depending on load order — matches user's "settings don't seem to take effect" complaint. Fixed `DefaultEngine.ini` to `=4` everywhere to match the rest.

**3. `bUseVSync` literally contradicted itself** — `DefaultEngine.ini`=False vs `DefaultScalability.ini`=True, same `[/Script/Engine.GameUserSettings]` section in two files. Fixed `DefaultScalability.ini` to False (matches the "no vsync, benchmark real fps" RTX3090 intent stated in `DefaultEngine.ini` comments).

**4. Systemic `MSM_TwoSidedFoliage` shading-model bug beyond the already-fixed [[unreal-wood-material-shading-model-fix]] Base_Material.** Ran a bulk audit via `ProgrammaticToolset.execute_tool_script` (batches `find_assets` + `ObjectTools.get_properties` across all 229 `/Game/` Material assets in one call — far cheaper than per-asset MCP round-trips). Found 7 more materials whose *names/textures* are clearly non-organic but were stuck on `MSM_TwoSidedFoliage` (giving the same pale/waxy/backlit look as the Wood bug):
   - `/Game/Mavrid/Default_M/Base_Marble_Tile` (marble)
   - `/Game/Mavrid/Default_M/Base_Tile` (generic tile)
   - `/Game/Level/Mega_Polis/textura/Ploshatka/Base_Material` (plaza pavement)
   - `/Game/Mavrid/FBX_Exporter/Tuvak_gullar/RECLAIMED_ARTIZAN_IRON_XL/Map/M_Material` (iron)
   - `/Game/Statik_tree/Tuvak_gullar/RECLAIMED_ARTIZAN_IRON_XL/Map/M_Material` (iron, duplicate)
   - `/Game/AutomotiveMaterials/Avto_Materials/Exterior/Reflector/MI_Reflector_Base` (car reflector)
   - `/Game/Mavrid/Default_M/aqon` (confirmed via `get_dependencies` — uses `rope__bump` texture, i.e. rope, not foliage)
   All fixed to `MSM_DefaultLit` via `ObjectTools.set_properties` → `MaterialTools.recompile` → `AssetTools.save_assets`, scripted in one `execute_tool_script` call.
   **Left unfixed (ambiguous):** `/Game/Level/Mega_Polis/modell/NewMaterial` — depends on generically-named textures `b_b/b_o/b_r/b_s`, couldn't confirm organic vs. non-organic without a visual check. Flagged for user.
   **How to apply:** if more materials are reported as pale/waxy/washed-out, re-run the bulk `execute_tool_script` shading-model audit (see script pattern above) rather than tracing graphs one at a time — this is clearly a recurring import/duplication pattern in this project (likely everything descended from one bad "Base_Material" template before the parent was fixed).

## Investigated, not a project bug

**Giant blue arrows covering every window during Play.** Traced to `BP_POI` (`/Game/ArchVizExplorer/Blueprints/BP_POI`) — ArchVizExplorer's Point-of-Interest actor, one per window/room (confirmed via `find_actors(name="HISM")` catching labels, then `CaptureViewport` with `annotations` to read actor labels near the arrows: `BP_POI_C_*`). The `arrow_LookAtDirection` `ArrowComponent` on it is a design-time "look at" direction gizmo. Its `bHiddenInGame` property is already correctly `true` — so this is **not a Blueprint misconfiguration**. Most likely explanation: Play-in-Viewport mode (the default green Play button) can still render editor-only visualizer/gizmo components unless the viewport's "Game View" (press `G`) is toggled on — a per-viewport editor display setting, not a project asset issue. **Not yet confirmed by the user pressing G during Play** — if they report arrows persist even with Game View on, this needs re-investigation (possibly `bIsEditorOnly` needs to be set `true` too, or the component needs to be destroyed at BeginPlay).

**Ray Tracing IS active at runtime**, contradicting the user's belief that "RT doesn't work even when enabled": confirmed live via `SearchCVars` during PIE — `r.RayTracing=1`, `r.RayTracing.Shadows=1`, `r.RayTracing.SkyLight=1`, `r.RayTracing.Enable=1`. So the "RT/shadows don't work" complaint is more likely about *visual quality* (materials looking wrong due to the PSO/shading-model bugs above) than RT literally being disabled.

**Texture streaming pool is correctly 16GB** (`r.Streaming.PoolSize=16384`, confirmed both in config and live via `SearchCVars`) — the older 8GB-vs-12GB bug from [[unreal_perf_texture_audit]] is still resolved, not regressed.

## Useful technique discovered this session
`editor_toolset.toolsets.programmatic.ProgrammaticToolset.execute_tool_script` lets you write a Python script (sandboxed: only `json/math/datetime/copy/re/time` importable) that calls `execute_tool(tool_name, json_input)` in a loop, batching many MCP tool calls into one round-trip. This is dramatically cheaper than calling `find_assets` + `get_properties` per-asset for bulk audits (used it to check ShadingModel across all 229 project materials in a single call instead of ~230 separate tool calls). Call `get_execution_environment` once first to get the exact `execute_tool` calling convention. Use this pattern for any future "check X property across all Y assets" request.

## Remaining scope not covered this session
User asked for exhaustive audit of meshes/actors/levels/blueprints/widgets/lighting + full git commit history review — only config + materials were covered in depth before running out of session budget. If resumed, prioritize: (1) confirming the BP_POI Game View theory with the user, (2) resolving the ambiguous `modell/NewMaterial`, (3) a similar bulk-script audit for StaticMesh nanite/LOD settings and Blueprint tick cost, since those are the likely next-biggest perf contributors per [[unreal_perf_texture_audit]] (mesh geometry, not textures, was already identified as the main weight driver).
