---
name: unreal-texture-material-dedup-round3
description: "2026-07-02 continuation of duplicate texture/material cleanup: Megascans Concrete_Wall base-material graph fix + 8 more AutomotiveMaterials Materials/Avto_Materials/avto_skm duplicate texture groups consolidated via MaterialInstanceTools"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7adce85f-9ecf-4986-9ff6-556f318ad0f6
---

Continuation of [[unreal_pending_fixes_and_mcp_status]]'s Round 1/2 dedup work, same session as [[unreal_mesh_instancing_workflow]].

## AutomotiveMaterials: 8 more duplicate texture groups fixed via MaterialInstanceTools.set_texture_parameter
Same recurring pattern as before: `AutomotiveMaterials/Materials/`, `AutomotiveMaterials/Avto_Materials/`, and `ArchvisDefault/Model/avto_skm/AutomotiveMaterials/Materials/` are 2-3 parallel trees with their own copies of the same source textures. Found via the 2026-07-01 `mcp_texture_audit_20260701.json` duplicate-group list (`Saved/AuditExport/`), cross-referenced with live `get_referencers`. Fixed by finding each affected MI's Texture-type parameter (`MaterialInstanceTools.list_parameters` + `get_texture_parameter`), matching against an old→canonical map, and calling `set_texture_parameter` — safer than editing base-Material graph nodes directly since it goes through the proper supported API.
Groups fixed (canonical copy chosen as whichever tree had more referencers, not always "Materials/"):
- `T_Metal_Anodized_01_BC` + `_R`: canonical=`Materials/`, fixed `Avto_Materials/.../MI_Metal_Anodized_01`. **Deleted** old `Avto_Materials/` copies (referencers went to 0 immediately).
- `T_Reflector_Triangle_N`: canonical=`Avto_Materials/` (4 referencers vs 2), fixed `avto_skm/.../MI_Reflector_Triangle_Red` + `MI_Reflector_Triangle_Orange`. **Deleted** old `avto_skm/` copy.
- `T_MetalWear_Frosted_N`/`_R`, `T_MetalWear_Lines_N`, `T_ReflectorHexagon_N`, `T_Leather_Small_N`, `T_Rubber_04_R`, `T_Tire_Sidewall_N`: all fixed (MI parameter repointed + saved) but **NOT deleted** — `get_referencers` still shows the fixed MIs as referencers of the old texture even after the parameter change and save. Same stale-`FMaterialCachedExpressionData` issue as [[unreal_mi_cached_data_stale_after_direct_edit]], this time triggered even through the proper `MaterialInstanceTools` API (not just raw reflection edits) — so this isn't specific to editing base-Material graphs directly, it's a general MI-cache-refresh gap in this MCP/engine combination.

## Skipped, correctly, without re-investigation
- `T_Painted_Gun_Metal_shrbbavc_4K_D`: NOT a simple duplicate — one copy lives under `/Game/TwinEra/material/Plastic/` (19+ MI referencers, a separate plugin/area), the other under `/Game/Megascans/Surfaces/Painted_Gun_Metal_shrbbavc/` (used by `BP_GLASS1` in the main Level). Different subsystems, low confidence they're meant to be merged — left alone.
- `T_CrackTileLarge_C`/`_N`: one copy feeds `asphalt` master material, the other feeds `bruschatka` (paving) master material — two semantically different road-surface systems, not the familiar twin-folder accidental-duplicate signature. Left alone; would need visual same-content confirmation plus material-graph tracing before touching.
- `T_OrangePeel_N`, `T_Flakes_D3_*`: already correctly identified in Round 1 as genuine CarPaint per-color variants, not duplicates — still correct, not re-touched.
- The ~70 remaining duplicate-name groups in the 2026-07-01 audit (`T_Generic_*`, `T_Gray/White/Black_Linear`, `BaseTexture`/`MRTexture`/`NormalTexture`/`EmissiveTexture`, `Manny_*` mannequin textures, `Placeholder`/`FlatNormal`, Megascans plant textures like `Agave_sisalana`/`PLANT_TEXTURE_*`/`Ash_*`/`gno_fiz_*`) are vendor noise or unreviewed — not touched this round, same as before.

## Remaining cleanup once the MI-cache staleness clears (needs Editor restart)
After a restart, re-run `get_referencers` on these and delete if truly empty:
- `/Game/AutomotiveMaterials/Avto_Materials/Exterior/Metal/Textures/T_MetalWear_Frosted_N`, `_R`
- `/Game/AutomotiveMaterials/Avto_Materials/Exterior/Metal/Textures/T_MetalWear_Lines_N`
- `/Game/ArchvisDefault/Model/avto_skm/AutomotiveMaterials/Materials/Exterior/Reflector/Textures/T_ReflectorHexagon_N`
- `/Game/ArchvisDefault/Model/avto_skm/AutomotiveMaterials/Materials/Interior/Leather/Textures/T_Leather_Small_N`
- `/Game/AutomotiveMaterials/Avto_Materials/Exterior/Rubber/Textures/T_Rubber_04_R`, `T_Tire_Sidewall_N`
- Also from [[unreal_mi_cached_data_stale_after_direct_edit]]: the 3 Megascans `Concrete_Wall_uepobaiew/NewFolder/` textures, plus the still-uninvestigated 4th lone texture `/Game/Megascans/Surfaces/Concrete_Wall_uepobaiew/1`.

**Why:** completes the "merge duplicate textures/materials" part of the user's optimization request, using the safer `MaterialInstanceTools` API where possible instead of raw MaterialExpression node edits.
**How to apply:** if the user reports the Editor was restarted, re-check all the "remaining cleanup" paths above with `get_referencers` before deleting — don't assume restart fixed it without checking.
