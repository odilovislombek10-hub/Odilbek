---
name: unreal-weather-responsive-materials-task
description: "PENDING user task (crashed before starting): make Glavniy_MirMIron materials react to UltraDynamicSky weather/season — wet asphalt+puddles+raindrop ripples in rain, snow on ground+walls in winter, as one universal optimized material"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa5d47bd-1a99-45a5-8267-f7746d4ca737
---

**User's original command (recovered 2026-07-03 from local transcript session `a0e9b6d8`, 2026-07-02T17:39; the work CRASHED Unreal when first attempted so this section was never done — user re-asked in session `8e9840ef` 18:36 and again `aa5d47bd` / current).** Conversation transcripts (.jsonl) are NOT in git — only `memory/` + audit JSON are committed (auto_commit pushes to the sibling `Muslimatun` repo `D:\...\Unreal Engine\Muslimatun`, still no jsonl). Transcripts live locally at `C:\Users\Windows 11\.claude\projects\D--...-Odilbek\*.jsonl` (30 sessions); recover user commands via PowerShell ConvertFrom-Json per line filtering type=='user'.

**Exact command (Uzbek, verbatim):** "BP_WeatherTime_Widget BIZDA SHU WIDGET BOR ULTRA DIYNAMIC SKAY BUNI UZING QILDING, ENDI BUNDAY QILISH KERAK GLAVNI LEVELDAGI MATERIALLARNI ULTRA DIYNAMC SKAYGA MOSLAB YOMGIR YOGANDA MIDOL UCHUN ASFALT SUV BULISH KERAK SUV TUPLANGAN JOYLAR BULISH KERAK YOMGIR ASFALTGA TUSHGANDA ASFALTDAGI TUPLANGAN SUVLARGA TOPCHI TUHGANI BILINISH KERAK DEVOR TEXTURALARIDAHAM SHUNDAY BULISH KERAK, QOR YOGANDAHAM HUDDA SHUNDAY BULISH KERAK MATERIALLARNI SHUNAQA QILIB UNIVERSAL MATERIAL QILIB OPTIMIZATSIYA QILISH KERAK"

**Requirement, decoded:**
- Make **Glavniy_MirMIron** level materials respond to UltraDynamicSky weather/season (the [[unreal_uds_weather_panel_progress]] BP_WeatherTime_Widget already drives UDS weather/season).
- **Rain:** asphalt gets wet (darker + higher specular/lower roughness), puddles form in low spots, visible raindrop ripple impacts on the pooled water.
- **Winter/snow:** snow accumulation on ground AND on wall textures (up-facing surfaces).
- Do it as ONE **universal material** (a shared master with weather params driven globally) — optimized, not per-asset hand-editing.
- User-identified target materials so far: **`M_Asphalt_base_Inst1`** = asphalt, **`M_Grass`** = lawn/gazon. (More surfaces — walls — to be enumerated.)

**VERTICAL vs HORIZONTAL surface handling (user explicitly confirmed this 2026-07-03, discussed earlier in session `8e9840ef` 18:48):** the effect must be driven by **world-space surface normal**, not applied uniformly:
- **Horizontal / up-facing surfaces** (normal Z ≈ +1: ground, roads, plaza, sidewalks, roofs, horizontal ledges) → **snow accumulates** here (top-down snow mask) AND **rain puddles pool** here. Strongest visual.
- **Vertical surfaces** (walls / `DEVOR`, normal Z ≈ 0) → snow barely accumulates, but **wetness/darkening + downward streaks** apply. User DID ask walls to respond too ("DEVOR TEXTURALARIDAHAM SHUNDAY").
- This world-normal masking is exactly what UDS's **`Surface_Weather_Effects`** material function does.

**Key assets found (session `8e9840ef`):** UDS surface function = **`Surface_Weather_Effects`** (603 nodes, 44 inputs — heavy). Most project materials derive from one **`Base_Material`** (`/Game/Mavrid/Default_M/Base_Material`, see [[unreal_wood_material_shading_model_fix]]) → cleanest to add the function ONCE to that master so instances inherit. **CRASH CAUSE identified:** adding this heavy 603-node function to MANY materials = many recompiles = the Lumen HWRT GPU crash. Mitigation: add to ONE master (or a few key ground materials) not per-asset; compile+save incrementally.

**PROGRESS — material #1 (asphalt) DONE 2026-07-03, awaiting user PIE test before #2.** User's execution plan: do ground materials **one at a time**, test each in PIE, THEN next — keeps recompiles light so no crash. Ground materials all live in `/Game/ArchvisDefault/Material/master_material/` (subfolders `asphalt/` and `bruschatka/`). Masters vs instances: `M_Asphalt_base` = **Material (master)**, `M_Asphalt_base_Inst1`/`_Inst` = MaterialInstanceConstant (inherit automatically); `M_Grass`, `M_landscape_01..12` = instances too; bruschatka master = `m_Bruschatka_base`, variants `M_Bruschatka_01..14`/`M_Ariq1`. So editing a MASTER covers all its instances at once = one recompile per master.

**EXACT WORKING TECHNIQUE (verified on M_Asphalt_base):** these masters use the **Material Attributes** workflow — individual MP_BaseColor/Roughness/Normal outputs are all disconnected; instead one `MaterialFunctionCall` (`MA_Out`) → `MP_MaterialAttributes`. So inserting UDS weather = trivial: drop `Surface_Weather_Effects` (`/Game/UltraDynamicSky/Materials/Weather/Surface_Weather_Effects`) between that final node and the output.
Steps via MaterialTools (MCP):
1. `add_expression` class `/Script/Engine.MaterialExpressionMaterialFunctionCall`; set its function via `ObjectTools.set_properties` values=`{"MaterialFunction":"/Game/UltraDynamicSky/Materials/Weather/Surface_Weather_Effects.Surface_Weather_Effects"}`.
2. Its input pin **"Material Attributes"** ← the old final node's `MA_Out`; its output **"Material Attributes"** → `connect_to_output` MP_MaterialAttributes.
3. **REQUIRED inputs with NO default (compile fails without them): "Apply Wetness" and "Apply Snow / Dust".** Add two `MaterialExpressionStaticBoolParameter` (named "Enable Wetness"/"Enable Snow", `DefaultValue:true`, Group "Weather (UDS)") → connect each to those two pins. (All other ~41 inputs have defaults — leave unwired.) The function reads UDS global weather state internally (Use Local Parameters defaults false) so it auto-responds to the BP_WeatherTime_Widget rain/season, and applies wetness/snow by WORLD NORMAL (horizontal→snow+puddles, vertical→wetness) = the vertical/horizontal requirement, for free.
4. `recompile` (raises on shader error — returned null=OK), then `save_assets`. Verified via LogsToolset: clean save at 20.15.34, thumbnail rendered, NO GPUCrash/Aftermath. Output pins also expose "Snow / Dust Opacity" + "Wetness Opacity" if finer masking needed later.
**Note on log clock skew:** editor session log timestamps read ~14h behind wall-clock (showed 2026.07.02-20.15 while real date 07-03) — correlate by event order / `LogModelContextProtocol: Dispatching` lines, not timestamp.

**NEXT MATERIALS (same technique, one at a time, test between each):** #2 `M_Grass` (BUT it's a MaterialInstanceConstant — need to find/edit ITS master, likely also M_landscape-family master or its own base; check `get_asset_class` + parent), then bruschatka master `m_Bruschatka_base` (note bruschatka already has `MF_Puddle_v2`/`MFI_Puddle_Ground` puddle functions — may already do wetness, verify before double-applying), then M_landscape_* masters. Grass/landscape: snow matters more than puddles; can set "Enable Wetness" false on those instances if wetness looks wrong on grass.

**Approach notes (not yet started):** UDS ships a global weather-wetness/snow system — typical integration is a Material Parameter Collection (MPC) or global scalar/vector params (`Wetness`, `Snow Amount`) that UltraDynamicWeather writes each frame, which surface master materials read to blend a wet/snow layer (world-space up-vector mask for snow, puddle mask from a noise/heightmap for water, panner-driven ripple normal for rain impacts). Check UDS docs/blueprints for the exact MPC/param names it already exposes (`/Game/UltraDynamicSky/...`) BEFORE authoring a new material — UDS likely already has "Post Process Materials" / "Wetness" hooks (`Ultra_Dynamic_Weather` has wetness & snow settings). **CAUTION: this crashed Unreal on first attempt — start small (one material, e.g. M_Asphalt_base_Inst1), save often, watch for the Lumen HWRT async GPU crash [[unreal_gpu_crash_lumen_hwrt_pagefault]].**

See [[unreal_uds_weather_panel_progress]], [[unreal_wood_material_shading_model_fix]], [[feedback_respond_in_uzbek]].
