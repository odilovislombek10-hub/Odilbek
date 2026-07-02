---
name: unreal-wood-material-shading-model-fix
description: "Root cause + fix for washed-out/pale Wood_* materials: Base_Material had wrong Shading Model (TwoSidedFoliage instead of DefaultLit)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1494aed5-be46-471c-a1a5-5800ec513937
---

## The bug (found + fixed 2026-07-02)
User reported `/Game/Mavrid/material/material/Wood_06` rendering pale/white-washed with only faint wood grain visible, despite the assigned textures (`wood__texture12__9_` Base, `wood_planks_normal`, `wood_planks_roughness`) being correct — screenshot showed a smooth chrome/plastic-looking sphere in the Material Instance Editor preview, not brown wood.

Traced the shared parent `/Game/Mavrid/Default_M/Base_Material` graph (`MaterialTools.get_property_input`/`get_expression_inputs` chain from `MP_BaseColor` down through `Power_0` → `Desaturation_0` → `Multiply_2` → `TextureSampleParameter2D_3`) and the math didn't explain the washout (Brightness=0.8, desaturation=0.3 shouldn't turn dark brown into white). The actual cause was **`Base_Material`'s `ShadingModel` property was set to `MSM_TwoSidedFoliage`** (meant for leaves/plants — light passes through, subsurface-scatter style, gives that pale/waxy/backlit look) instead of `MSM_DefaultLit`. Confirmed by directly querying `ObjectTools.get_properties` on the Material asset itself (`shadingModel`/`blendMode`/`bFullyRough` are readable this way; per-pin defaults like `Metallic` constant are not).

**Fix applied:** `ObjectTools.set_properties` → `{"shadingModel":"MSM_DefaultLit"}` on `Base_Material`, then `MaterialTools.recompile`, verified visually via `EditorAppToolset.CaptureAssetImage` (renders a live thumbnail PNG — decode by saving the tool's JSON output then `[Convert]::FromBase64String($json.returnValue.data)` in PowerShell, since the raw MCP result is too large for the token limit and gets written to a `tool-results/*.txt` file automatically). Before/after thumbnails confirmed proper brown wood grain replaced the white-washed look. Saved both `Base_Material` and `Wood_06`.

**Blast radius:** `Base_Material` is referenced by 19 assets (`get_referencers`): all `Wood_*`/`welo_*`/`DPK_Wood_08` material instances, `Soil`/`Soil1`, and 3 automotive detail materials (`M_Rodiator`, `Range_Rower_Sport`/`5`/`6` logos) under `ArchvisDefault/Model/avto_skm/AutomotiveMaterials`. All of these were rendering with the same wrong foliage-subsurface shading and are now fixed by this one change. Deliberately did NOT touch `BlendMode` (`BLEND_Masked`) even though also unusual for a solid wood material — the automotive logo materials likely need Masked for alpha-cutout logos, and Wood's default Opacity texture is full-white (`MeshModelingToolsetExp/Textures/DefaultOpacity`) so Masked blend mode alone causes no visible bug, just a minor unnecessary alpha-test cost.

**Known remaining polish (not fixed, deliberately left for user):** the sphere is still somewhat glossy/reflective after the shading-model fix — `Specular` override on `Wood_06` is 1.05 (vs. engine default 0.5) and the "Reflection" scalar param (confusingly named — it actually multiplies the Roughness texture sample, `Multiply_1` feeding `MP_Roughness`) is 0.245, giving a fairly low/glossy final roughness. If asked to make wood look more matte, tune these on the MI rather than the shared master.

**Why:** avoids re-deriving the graph trace or re-discovering that `CaptureAssetImage` + PowerShell base64-decode is the way to visually verify material fixes without relying on the user's screenshots.
**How to apply:** if another `Wood_*`/`welo_*`/`Soil*` material or the automotive radiator/logo materials are reported as looking "washed out", "pale", "plastic", or "waxy", check whether they've since been re-pointed to a different parent — if still on `Base_Material`, this fix already covers them, so look for MI-level scalar overrides (`Specular`/`Reflection`/`desaturation`/`Brighness`) instead of re-diagnosing the shading model.
