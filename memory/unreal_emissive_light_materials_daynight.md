---
name: unreal-emissive-light-materials-daynight
description: How Light_Inst emissive lamp materials were made to turn on at night (like NightLight-tagged lights) via Emissive_MPC StreetLights scalar driven from BP_WeatherTime_Widget:ApplyTime
metadata: 
  node_type: memory
  type: project
  originSessionId: 3d36b9e6-ef67-4475-b241-dafc32d6e91b
---

2026-07-04. User: "Light_Inst SHUNAQA LIGHT MATERIALLARNIHAM ... SOATI VAQTI BULGANDA YONADIGON QILOLASANMI?" = make the emissive lamp MATERIALS (Light_Inst family) also switch on/off by time-of-day, like the NightLight-tagged light ACTORS from [[unreal_uds_weather_panel_progress]]. DONE.

**The Light_Inst family:** `Light_Inst`, `Light_Inst1`, `Light_Inst2`, `Light_Inst3` in `/Game/TwinEra/material/Light/` are all `MaterialInstanceConstant` children of ONE base material **`/Game/TwinEra/material/Light/Light`**. Emissive brightness = `EmsColor(VectorParam) × EMS(ScalarParam)` (Multiply_0 → MP_EmissiveColor). EMS varies per instance (Light_Inst=20 bright, Light_Inst1=0.2 dim). Because they share ONE parent, editing the base material covers all 4 at once. `Light_Inst1` = confirmed street-lamp material (see [[unreal_packaged_vs_editor_exposure]]). NOT covered (different parents): padez `Emessive_Light_Inst`, `Emissive_fasad-light`, `M_Emissive_Master` — mention to user if they want those too.

**Why MPC, not per-instance:** MaterialInstanceConstant can't be changed at runtime without MIDs. Standard fix = route emissive through a MaterialParameterCollection scalar (global, runtime-settable, no shader recompile). Reused the project's existing `Emissive_MPC` (`/Game/ArchVizExplorer/Materials/MPC/Emissive_MPC`) which already had scalars Buildings(1)/Effects(0) for window-glow.

**What I did (all via unreal-mcp, editor live):**
1. Added scalar **`StreetLights`** (defaultValue=**1**, so lamps stay ON if nothing drives it = safe fallback) to Emissive_MPC via ObjectTools.set_properties on its ScalarParameters array (needed a full-array rewrite incl the existing 2 + a hand-picked GUID; the `id` field is set fine via the array, unlike a node's ParameterId).
2. Base material `Light`: added `MaterialExpressionCollectionParameter_0` (Collection=Emissive_MPC, ParameterName=StreetLights) + a new `Multiply_1`. Rewired: `Multiply_0 → Multiply_1.A`, `CollectionParam → Multiply_1.B`, `Multiply_1 → MP_EmissiveColor`. So Emissive = EmsColor×EMS×StreetLights. recompile() SUCCEEDED (no raise) → this PROVES the CollectionParameter resolved StreetLights correctly. **GOTCHA:** MaterialExpressionCollectionParameter.ParameterId can NOT be set/read via ObjectTools (both error "could not be set/read"); DON'T panic — setting ParameterName + Collection triggers PostEditChangeProperty which syncs ParameterId internally, confirmed by the clean recompile (a zero-GUID ParameterId would make Compile() Errorf → recompile would raise).
3. `BP_WeatherTime_Widget:ApplyTime(Hours)`: SURGICAL add (did NOT write_graph_dsl the whole fn — its readback is lossy per [[unreal_uds_weather_panel_progress]] and would break the working UDS-time logic). Reused the EXISTING OR node (`K2Node_CommutativeAssociativeBinaryOperator_0`, ORBoolean = `(Hours>=18) OR (Hours<7)` = isNight, the same bool the NightLight ForEach uses via NOT). Added `Math|Float|SelectFloat`(A=1,B=0,bPickA=OR) + `Rendering|Material|SetScalarParameterValue` (declaring_class `/Script/Engine.KismetMaterialLibrary` to get the collection version, NOT the MID version). Wired: OR→SelectFloat.bPickA, SelectFloat→ParameterValue, **ForEach.Completed(out idx3)→SetScalar.exec** (Completed was unconnected, so no break needed). Collection pin=Emissive_MPC, ParameterName=StreetLights. Compiled clean.

**Result (verified via read_graph_dsl):** ApplyTime now ends with `(SetScalarParameterValue Emissive_MPC "StreetLights" (SelectFloat 1.0 0.0 isNight))` right after the NightLight ForEach. isNight = ≥18:00 OR <07:00 — IDENTICAL window to the tagged light actors. ApplyTime is called by EventConstruct(16), Time ⏴/⏵ buttons, and EventTick slider-change → lamp materials + tagged lights toggle together on every time change. Saved: Light material, Emissive_MPC, BP_WeatherTime_Widget.

**NOT yet PIE-tested visually** (needs Play + slider to night). Structurally verified: material recompiled clean (param resolves), BP compiled clean, DSL correct. To visually confirm: PIE Glavniy_MirMIron → panel top-left → slide time to 20:00 → lamp emissives should light up; back to 12:00 → off. (Alt cheap editor test: set Emissive_MPC StreetLights defaultValue 1→0, lamp emissives darken live in viewport, then restore.)

See [[unreal_uds_weather_panel_progress]], [[unreal_weather_panel_vr_pragulka]], [[unreal_packaged_vs_editor_exposure]], [[feedback_respond_in_uzbek]].
